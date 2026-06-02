import axios, { type AxiosProgressEvent } from 'axios';
import type {
  ApiResponse,
  UploadResponse,
  TaskProgress,
  SeparationRequest,
  ChordRequest,
  ChordSegment,
  TransformRequest,
} from '@/types';

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
});

// ============ 文件上传 ============

export async function uploadFile(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadResponse> {
  const form = new FormData();
  form.append('file', file);

  const { data } = await http.post<ApiResponse<UploadResponse>>('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e: AxiosProgressEvent) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });

  if (!data.success || !data.data) {
    throw new Error(data.error ?? '上传失败');
  }
  return data.data;
}

// ============ 任务操作 ============

export async function getTaskStatus(taskId: string): Promise<TaskProgress> {
  const { data } = await http.get<ApiResponse<TaskProgress>>(`/task/${taskId}`);
  if (!data.success || !data.data) {
    throw new Error(data.error ?? '查询失败');
  }
  return data.data;
}

export async function triggerSeparation(
  taskId: string,
  params: SeparationRequest,
): Promise<TaskProgress> {
  const { data } = await http.post<ApiResponse<TaskProgress>>(
    `/task/${taskId}/separate`,
    params,
  );
  if (!data.success || !data.data) {
    throw new Error(data.error ?? '分离请求失败');
  }
  return data.data;
}

export async function triggerChordAnalysis(
  taskId: string,
  params: ChordRequest = {},
): Promise<ChordSegment[]> {
  const { data } = await http.post<ApiResponse<ChordSegment[]>>(
    `/task/${taskId}/chords`,
    params,
  );
  if (!data.success || !data.data) {
    throw new Error(data.error ?? '和弦分析失败');
  }
  return data.data;
}

export async function triggerTransform(
  taskId: string,
  params: TransformRequest,
): Promise<TaskProgress> {
  const { data } = await http.post<ApiResponse<TaskProgress>>(
    `/task/${taskId}/transform`,
    params,
  );
  if (!data.success || !data.data) {
    throw new Error(data.error ?? '处理失败');
  }
  return data.data;
}

// ============ 下载 ============

export function getDownloadUrl(taskId: string, stemId: string): string {
  return `/api/task/${taskId}/download/${stemId}`;
}

export async function downloadStem(
  taskId: string,
  stemId: string,
  format: string = 'mp3',
): Promise<Blob> {
  const { data } = await http.get<Blob>(`/task/${taskId}/download/${stemId}`, {
    params: { format },
    responseType: 'blob',
  });
  return data;
}

// ============ 和弦导出 ============

export function getChordExportUrl(taskId: string): string {
  return `/api/task/${taskId}/chords/export`;
}

// ============ WebSocket URL ============

export function getWsUrl(taskId: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}/ws/task/${taskId}`;
}

export default http;
