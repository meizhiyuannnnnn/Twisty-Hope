import axios, { type AxiosProgressEvent } from 'axios';
import type {
  UploadResponse,
  TaskProgress,
  SeparationRequest,
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

  const { data } = await http.post<UploadResponse>('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e: AxiosProgressEvent) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });

  return data;
}

// ============ 任务操作 ============

export async function getTaskStatus(
  taskId: string,
  token: string,
): Promise<TaskProgress> {
  const { data } = await http.get<TaskProgress>(`/task/${taskId}`, {
    params: { token },
  });
  return data;
}

export interface TaskDetail extends TaskProgress {
  result_stems?: string[] | null;
  chord_result?: { chords: { start: number; end: number; chord: string }[] } | null;
  error_message?: string | null;
}

export async function getTaskDetail(
  taskId: string,
  token: string,
): Promise<TaskDetail> {
  const { data } = await http.get<TaskDetail>(`/task/${taskId}`, {
    params: { token },
  });
  return data;
}

export async function triggerSeparation(
  taskId: string,
  token: string,
  params: SeparationRequest,
): Promise<TaskProgress> {
  const { data } = await http.post<TaskProgress>(
    `/task/${taskId}/separate`,
    params,
    { params: { token } },
  );
  return data;
}

export async function triggerChordAnalysis(
  taskId: string,
  token: string,
): Promise<TaskProgress> {
  const { data } = await http.post<TaskProgress>(
    `/task/${taskId}/chords`,
    {},
    { params: { token } },
  );
  return data;
}

export async function triggerTransform(
  taskId: string,
  token: string,
  params: TransformRequest,
): Promise<TaskProgress> {
  const { data } = await http.post<TaskProgress>(
    `/task/${taskId}/transform`,
    params,
    { params: { token } },
  );
  return data;
}

// ============ 下载 ============

export function getDownloadUrl(taskId: string, token: string, stemId: string): string {
  return `/api/task/${taskId}/download/${stemId}?token=${encodeURIComponent(token)}`;
}

export async function downloadStem(
  taskId: string,
  token: string,
  stemId: string,
): Promise<Blob> {
  const { data } = await http.get<Blob>(
    `/task/${taskId}/download/${stemId}`,
    {
      params: { token },
      responseType: 'blob',
    },
  );
  return data;
}

// ============ 和弦导出 ============

export function getChordExportUrl(taskId: string, token: string): string {
  return `/api/task/${taskId}/chords/export?token=${encodeURIComponent(token)}`;
}

// ============ WebSocket URL ============

export function getWsUrl(taskId: string, token: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}/ws/task/${taskId}?token=${encodeURIComponent(token)}`;
}

export default http;
