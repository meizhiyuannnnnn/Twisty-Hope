import { useRef } from 'react';
import { Upload, Music, FileAudio } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { formatFileSize } from '@/utils/format';
import type { AudioFile } from '@/types';

interface FileUploadProps {
  file: AudioFile | null;
  isDragging: boolean;
  error: string | null;
  progress: number;
  isUploading: boolean;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onClear: () => void;
}

export function FileUpload({
  file,
  isDragging,
  error,
  progress,
  isUploading,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileSelect,
  onClear,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    inputRef.current?.click();
  };

  if (file) {
    return (
      <div className="flex flex-col items-center gap-4 rounded-2xl border-2 border-app-border bg-card p-8">
        <div className="flex items-center gap-4 w-full">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
            <FileAudio className="h-7 w-7 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">{file.name}</p>
            <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClear} disabled={isUploading}>
            更换
          </Button>
        </div>

        {isUploading && (
          <div className="w-full space-y-2">
            <Progress value={progress} className="h-3" />
            <p className="text-center text-sm text-muted-foreground">上传中 {progress}%</p>
          </div>
        )}

        {!isUploading && (
          <p className="text-sm text-muted-foreground">文件已就绪，点击"开始分离"处理</p>
        )}
      </div>
    );
  }

  return (
    <div
      className={`relative flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-12 transition-all duration-200 cursor-pointer
        ${isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/50'}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') handleClick();
      }}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".mp3,.wav,.flac,.m4a,.ogg,audio/mpeg,audio/wav,audio/flac,audio/mp4,audio/ogg"
        onChange={onFileSelect}
      />

      <div className={`flex h-20 w-20 items-center justify-center rounded-2xl transition-colors ${isDragging ? 'bg-primary/20' : 'bg-muted'}`}>
        {isDragging ? (
          <Upload className="h-10 w-10 text-primary animate-bounce" />
        ) : (
          <Music className="h-10 w-10 text-muted-foreground" />
        )}
      </div>

      <div className="text-center space-y-1">
        <p className="text-lg font-medium text-foreground">
          {isDragging ? '松开鼠标上传文件' : '拖拽音频文件到此处'}
        </p>
        <p className="text-sm text-muted-foreground">或点击选择文件</p>
      </div>

      <div className="flex gap-2">
        {['MP3', 'WAV', 'FLAC', 'M4A', 'OGG'].map((fmt) => (
          <span key={fmt} className="rounded-full bg-secondary px-2.5 py-0.5 text-xs text-muted-foreground">
            {fmt}
          </span>
        ))}
      </div>

      <p className="text-xs text-muted-foreground">最大 100MB</p>

      {error && (
        <div className="mt-2 rounded-lg bg-destructive/10 px-4 py-2 text-sm text-destructive">
          {error}
        </div>
      )}
    </div>
  );
}
