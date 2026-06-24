import { create } from 'zustand';
import type {
  AudioFile,
  SeparationMode,
  TaskProgress,
  StemResult,
  TransformParams,
  ChordSegment,
  ChordNotation,
} from '@/types';
import { DEFAULT_TRANSFORM } from '@/types';
import { clearWebSocketState } from '@/hooks/useWebSocket';

// ── sessionStorage 持久化 key ────────────────────────────────────
// 使用 sessionStorage 而非 localStorage：
//   - 刷新页面 → 保留状态（sessionStorage 在同一标签页内持久）
//   - 关闭标签页/浏览器 → 自动清除（符合"关闭网站后清除结果"的需求）
// 历史记录独立保存在 localStorage 中，不受影响。
const STORE_KEY = 'audio_sep_app_state';

interface PersistedState {
  taskId: string | null;
  token: string | null;
  taskProgress: TaskProgress | null;
  stems: StemResult[];
}

function loadPersisted(): PersistedState {
  try {
    const raw = sessionStorage.getItem(STORE_KEY);
    if (!raw) return { taskId: null, token: null, taskProgress: null, stems: [] };
    const parsed = JSON.parse(raw);
    // 迁移旧版数据（taskStatus 字符串 → 完整 taskProgress 对象）
    if (parsed.taskStatus && !parsed.taskProgress) {
      parsed.taskProgress = {
        task_id: parsed.taskId ?? '',
        status: parsed.taskStatus,
        progress: parsed.taskStatus === 'completed' ? 100 : 0,
        message: '',
        stems: parsed.stems ?? [],
      };
      delete parsed.taskStatus;
    }
    // 确保恢复的 taskProgress 包含 stems（修补不完整的持久化数据）
    if (parsed.taskProgress && !parsed.taskProgress.stems && parsed.stems?.length > 0) {
      parsed.taskProgress.stems = parsed.stems;
    }
    return parsed as PersistedState;
  } catch {
    return { taskId: null, token: null, taskProgress: null, stems: [] };
  }
}

function savePersisted(state: Partial<PersistedState>): void {
  try {
    const current = loadPersisted();
    const updated = { ...current, ...state };
    sessionStorage.setItem(STORE_KEY, JSON.stringify(updated));
  } catch {
    // ignore
  }
}

const INITIAL_PERSISTED = loadPersisted();

// ──────────────────────────────────────────────────────────────────

interface AppState {
  // ---- 文件 ----
  currentFile: AudioFile | null;
  setCurrentFile: (file: AudioFile | null) => void;

  // ---- 上传 ----
  uploadProgress: number;
  setUploadProgress: (p: number) => void;
  isUploading: boolean;
  setIsUploading: (v: boolean) => void;

  // ---- 分离 ----
  separationMode: SeparationMode;
  setSeparationMode: (mode: SeparationMode) => void;
  taskId: string | null;
  setTaskId: (id: string | null) => void;
  token: string | null;
  setToken: (token: string | null) => void;
  taskProgress: TaskProgress | null;
  setTaskProgress: (p: TaskProgress | null) => void;
  stems: StemResult[];
  setStems: (stems: StemResult[]) => void;

  // ── 持久化恢复 ──
  restoreFromHistory: (taskId: string, token: string, stems: StemResult[]) => void;

  // ---- 变速/变调 ----
  transformParams: TransformParams;
  setTransformParams: (params: Partial<TransformParams>) => void;
  isTransformDirty: boolean;
  setIsTransformDirty: (v: boolean) => void;

  // ---- 和弦 ----
  chords: ChordSegment[];
  setChords: (chords: ChordSegment[]) => void;
  chordNotation: ChordNotation;
  setChordNotation: (n: ChordNotation) => void;
  isChordLoading: boolean;
  setIsChordLoading: (v: boolean) => void;

  // ---- UI ----
  activeTab: 'separate' | 'chords' | 'transform';
  setActiveTab: (tab: 'separate' | 'chords' | 'transform') => void;

  // ---- 重置 ----
  resetAll: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentFile: null,
  setCurrentFile: (file) => set({ currentFile: file }),

  uploadProgress: 0,
  setUploadProgress: (p) => set({ uploadProgress: p }),
  isUploading: false,
  setIsUploading: (v) => set({ isUploading: v }),

  separationMode: '2track',
  setSeparationMode: (mode) => set({ separationMode: mode }),

  // ── 从 sessionStorage 恢复（刷新保留，关闭标签页清除）──
  taskId: INITIAL_PERSISTED.taskId,
  setTaskId: (id) => {
    savePersisted({ taskId: id });
    set({ taskId: id });
  },
  token: INITIAL_PERSISTED.token,
  setToken: (token) => {
    savePersisted({ token });
    set({ token });
  },
  // 如果 stems 有数据但 taskProgress 缺失，自动构造完成状态保证 UI 正常
  taskProgress: INITIAL_PERSISTED.taskProgress
    ?? (INITIAL_PERSISTED.stems.length > 0
      ? {
          task_id: INITIAL_PERSISTED.taskId ?? '',
          status: 'completed' as const,
          progress: 100,
          message: '',
          stems: INITIAL_PERSISTED.stems,
        }
      : null),
  setTaskProgress: (p) => {
    savePersisted({ taskProgress: p });
    set({ taskProgress: p });
  },
  stems: INITIAL_PERSISTED.stems,
  setStems: (stems) => {
    savePersisted({ stems });
    set({ stems });
  },

  restoreFromHistory: (taskId: string, token: string, stems: StemResult[]) => {
    const tp: TaskProgress = stems.length > 0
      ? { task_id: taskId, status: 'completed', progress: 100, message: '从历史恢复', stems }
      : { task_id: taskId, status: 'pending', progress: 0, message: '' };
    savePersisted({ taskId, token, taskProgress: tp, stems });
    set({ taskId, token, taskProgress: tp, stems });
  },

  transformParams: { ...DEFAULT_TRANSFORM },
  setTransformParams: (params) =>
    set((s) => ({ transformParams: { ...s.transformParams, ...params } })),
  isTransformDirty: false,
  setIsTransformDirty: (v) => set({ isTransformDirty: v }),

  chords: [],
  setChords: (chords) => set({ chords }),
  chordNotation: 'name',
  setChordNotation: (n) => set({ chordNotation: n }),
  isChordLoading: false,
  setIsChordLoading: (v) => set({ isChordLoading: v }),

  activeTab: 'separate',
  setActiveTab: (tab) => set({ activeTab: tab }),

  resetAll: () => {
    sessionStorage.removeItem(STORE_KEY);
    clearWebSocketState();
    set({
      currentFile: null,
      uploadProgress: 0,
      isUploading: false,
      separationMode: '2track',
      taskId: null,
      token: null,
      taskProgress: null,
      stems: [],
      transformParams: { ...DEFAULT_TRANSFORM },
      isTransformDirty: false,
      chords: [],
      chordNotation: 'name',
      isChordLoading: false,
      activeTab: 'separate',
    });
  },
}));
