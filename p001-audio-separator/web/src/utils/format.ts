/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * 格式化时间（秒 → mm:ss 或 hh:mm:ss）
 */
export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const pad = (n: number) => n.toString().padStart(2, '0');
  if (h > 0) return `${pad(h)}:${pad(m)}:${pad(s)}`;
  return `${pad(m)}:${pad(s)}`;
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}

/**
 * 验证文件格式
 */
import type { SupportedFormat } from '@/types';
import { SUPPORTED_FORMATS } from '@/types';

export function validateFileFormat(filename: string): SupportedFormat | null {
  const ext = filename.split('.').pop()?.toLowerCase();
  if (ext && (SUPPORTED_FORMATS as readonly string[]).includes(ext)) {
    return ext as SupportedFormat;
  }
  return null;
}

/**
 * 验证文件大小
 */
export function validateFileSize(size: number, maxSize: number = 100 * 1024 * 1024): boolean {
  return size <= maxSize;
}
