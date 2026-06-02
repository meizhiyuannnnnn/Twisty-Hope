import { Play, Pause, SkipBack, SkipForward } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { usePlayerStore } from '@/stores/usePlayerStore';
import { formatDuration } from '@/utils/format';

interface GlobalPlayerProps {
  onPlay: () => void;
  onPause: () => void;
  onSeek: (time: number) => void;
  disabled?: boolean;
}

export function GlobalPlayer({ onPlay, onPause, onSeek, disabled }: GlobalPlayerProps) {
  const { isGlobalPlaying, currentTime, duration } = usePlayerStore();

  const handleTogglePlay = () => {
    if (isGlobalPlaying) {
      onPause();
    } else {
      onPlay();
    }
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-sm">
      {/* 进度条 */}
      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground w-12 text-right tabular-nums">
          {formatDuration(currentTime)}
        </span>
        <Slider
          value={[progressPercent]}
          min={0}
          max={100}
          step={0.1}
          onValueChange={([v]) => onSeek((v! / 100) * duration)}
          disabled={disabled || duration === 0}
          className="flex-1"
        />
        <span className="text-xs text-muted-foreground w-12 tabular-nums">
          {formatDuration(duration)}
        </span>
      </div>

      {/* 播放控制 */}
      <div className="flex items-center justify-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          disabled={disabled}
          onClick={() => onSeek(0)}
          title="回到开头"
        >
          <SkipBack className="h-5 w-5" />
        </Button>

        <Button
          size="lg"
          className="h-12 w-12 rounded-full"
          disabled={disabled}
          onClick={handleTogglePlay}
        >
          {isGlobalPlaying ? (
            <Pause className="h-6 w-6" />
          ) : (
            <Play className="h-6 w-6 ml-0.5" />
          )}
        </Button>

        <Button
          variant="ghost"
          size="icon"
          disabled={disabled || currentTime >= duration}
          onClick={() => onSeek(Math.min(duration, currentTime + 5))}
          title="快进 5 秒"
        >
          <SkipForward className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
