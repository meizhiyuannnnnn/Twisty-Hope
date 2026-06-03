// ============ 音频文件相关 ============

export const SUPPORTED_FORMATS = ['mp3', 'wav', 'flac', 'm4a', 'ogg'] as const;
export type SupportedFormat = (typeof SUPPORTED_FORMATS)[number];

export const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

export interface AudioFile {
  id: string;
  name: string;
  size: number;
  format: SupportedFormat;
  duration?: number;
  file: File;
  url: string; // ObjectURL
}

// ============ 分离模式 ============

export type SeparationMode = '2track' | '4track';

export const TRACK_2_LABELS = {
  vocals: '人声',
  accompaniment: '伴奏',
} as const;

export const TRACK_4_LABELS = {
  vocals: '人声',
  drums: '鼓',
  bass: '贝斯',
  other: '其他',
} as const;

export type StemId2Track = keyof typeof TRACK_2_LABELS;
export type StemId4Track = keyof typeof TRACK_4_LABELS;
export type StemId = StemId2Track | StemId4Track;

// ============ 任务状态 ============

export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface TaskProgress {
  task_id: string;
  status: TaskStatus;
  progress: number; // 0-100
  message: string;
  stems?: StemResult[];
  error?: string;
}

export interface StemResult {
  stem_id: StemId;
  label: string;
  url: string;
  waveform_data?: number[]; // 波形采样数据 [-1, 1]
  duration?: number;
}

// ============ 变速/变调 ============

export interface TransformParams {
  speed: number; // 0.5 - 1.5
  pitch: number; // -12 - +12 半音
}

export const DEFAULT_TRANSFORM: TransformParams = {
  speed: 1.0,
  pitch: 0,
};

// ============ 和弦 ============

export interface ChordSegment {
  id: string;
  chord: string; // 和弦名称，如 "Am", "G7"
  degree: string; // 级数记法，如 "VIm", "V7"
  start_time: number; // 秒
  end_time: number; // 秒
}

export type ChordNotation = 'name' | 'degree';

// ============ 播放器 ============

export interface TrackState {
  stemId: StemId;
  label: string;
  solo: boolean;
  mute: boolean;
  volume: number; // 0-1
}

export type PlayState = 'idle' | 'playing' | 'paused';

// ============ 历史记录 ============

export interface HistoryEntry {
  id: string;
  fileName: string;
  taskId: string;
  mode: SeparationMode;
  createdAt: string; // ISO string
  stems: StemResult[];
}

// ============ 批量队列 ============

export interface QueueItem {
  id: string;
  file: AudioFile;
  taskId?: string;
  status: TaskStatus;
  progress: number;
}

// ============ API 通用响应 ============

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadResponse {
  task_id: string;
  token: string;
  original_filename: string;
  file_size: number;
  duration: number | null;
  message?: string;
}

export interface SeparationRequest {
  mode: SeparationMode;
}

export interface ChordRequest {
  notation?: ChordNotation;
}

export interface TransformRequest {
  speed: number;
  pitch: number;
}

export interface DownloadOptions {
  format: 'mp3' | 'wav' | 'flac';
  bitrate?: string;
}
