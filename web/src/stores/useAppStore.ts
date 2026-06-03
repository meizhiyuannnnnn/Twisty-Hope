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
  taskId: null,
  setTaskId: (id) => set({ taskId: id }),
  token: null,
  setToken: (token) => set({ token }),
  taskProgress: null,
  setTaskProgress: (p) => set({ taskProgress: p }),
  stems: [],
  setStems: (stems) => set({ stems }),

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

  resetAll: () =>
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
    }),
}));
