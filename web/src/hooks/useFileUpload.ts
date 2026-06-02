import { useCallback, useRef, useState } from 'react';
import type { AudioFile } from '@/types';
import { MAX_FILE_SIZE } from '@/types';
import { validateFileFormat, validateFileSize } from '@/utils/format';

interface UseFileUploadReturn {
  file: AudioFile | null;
  isDragging: boolean;
  error: string | null;
  progress: number;
  handleDragOver: (e: React.DragEvent) => void;
  handleDragLeave: (e: React.DragEvent) => void;
  handleDrop: (e: React.DragEvent) => void;
  handleFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  openFileDialog: () => void;
  clearFile: () => void;
  setProgress: (p: number) => void;
}

export function useFileUpload(): UseFileUploadReturn {
  const [file, setFile] = useState<AudioFile | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const dragCounter = useRef(0);

  const processFile = useCallback((f: File) => {
    setError(null);
    setProgress(0);

    const format = validateFileFormat(f.name);
    if (!format) {
      setError('不支持的音频格式，请上传 MP3/WAV/FLAC/M4A/OGG 文件');
      return;
    }

    if (!validateFileSize(f.size, MAX_FILE_SIZE)) {
      setError('文件大小超过 100MB 限制，请压缩后重试');
      return;
    }

    const audioFile: AudioFile = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name: f.name,
      size: f.size,
      format,
      file: f,
      url: URL.createObjectURL(f),
    };

    setFile(audioFile);
    return audioFile;
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      dragCounter.current = 0;

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        processFile(files[0]);
      }
    },
    [processFile],
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        processFile(files[0]);
      }
      // 重置 input 以允许重复选择同一文件
      e.target.value = '';
    },
    [processFile],
  );

  const openFileDialog = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const clearFile = useCallback(() => {
    if (file?.url) {
      URL.revokeObjectURL(file.url);
    }
    setFile(null);
    setError(null);
    setProgress(0);
  }, [file]);

  return {
    file,
    isDragging,
    error,
    progress,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    openFileDialog,
    clearFile,
    setProgress,
  };
}
