import { useState } from 'react';
import { Music, Download } from 'lucide-react';
import { cn } from '@/utils/cn';
import { formatDuration } from '@/utils/format';
import type { ChordSegment, ChordNotation } from '@/types';
import { useAppStore } from '@/stores/useAppStore';
import { getChordExportUrl } from '@/services/api';

interface ChordDisplayProps {
  chords: ChordSegment[];
  taskId: string;
  onSeekTo: (time: number) => void;
  disabled?: boolean;
}

export function ChordDisplay({ chords, taskId, onSeekTo, disabled }: ChordDisplayProps) {
  const { chordNotation, setChordNotation } = useAppStore();
  const [activeChordId, setActiveChordId] = useState<string | null>(null);

  const handleClick = (seg: ChordSegment) => {
    if (!disabled) {
      setActiveChordId(seg.id);
      onSeekTo(seg.start_time);
    }
  };

  const displayText = (seg: ChordSegment) =>
    chordNotation === 'degree' ? seg.degree : seg.chord;

  if (chords.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 py-8 text-muted-foreground">
        <Music className="h-12 w-12 opacity-30" />
        <p className="text-sm">暂无和弦数据</p>
        <p className="text-xs">完成人声/伴奏分离后可分析和弦</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 记法切换 + 导出 */}
      <div className="flex items-center justify-between">
        <div className="flex rounded-lg border border-input p-0.5" role="radiogroup">
          {(['name', 'degree'] as ChordNotation[]).map((mode) => (
            <button
              key={mode}
              type="button"
              role="radio"
              aria-checked={chordNotation === mode}
              className={cn(
                'rounded-md px-3 py-1 text-sm font-medium transition-colors',
                chordNotation === mode
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground',
              )}
              onClick={() => setChordNotation(mode)}
            >
              {mode === 'name' ? '和弦名称' : '级数记法'}
            </button>
          ))}
        </div>

        <a
          href={getChordExportUrl(taskId)}
          download
          className="inline-flex items-center gap-1.5 rounded-lg border border-input px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        >
          <Download className="h-3.5 w-3.5" />
          导出文本
        </a>
      </div>

      {/* 和弦时间轴 */}
      <div className="flex flex-wrap gap-1.5">
        {chords.map((seg) => (
          <button
            key={seg.id}
            type="button"
            disabled={disabled}
            onClick={() => handleClick(seg)}
            className={cn(
              'group relative flex flex-col items-center rounded-lg border px-3 py-2 transition-all hover:shadow-sm',
              activeChordId === seg.id
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-app-border bg-card hover:border-primary/40',
              disabled && 'cursor-default',
            )}
            title={`${formatDuration(seg.start_time)} - ${formatDuration(seg.end_time)}`}
          >
            <span className="text-lg font-bold leading-tight">
              {displayText(seg)}
            </span>
            <span className="text-[10px] text-muted-foreground">
              {formatDuration(seg.start_time)}
            </span>
          </button>
        ))}
      </div>

      {/* 和弦密度提示 */}
      <p className="text-xs text-muted-foreground">
        共识别 {chords.length} 个和弦，点击可跳转到对应时间点
      </p>
    </div>
  );
}
