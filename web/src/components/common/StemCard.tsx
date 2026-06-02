import { Play, Pause, Volume2, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/utils/cn';
import type { StemResult } from '@/types';
import { getDownloadUrl } from '@/services/api';

interface StemCardProps {
  stem: StemResult;
  taskId: string;
  isSolo: boolean;
  isMuted: boolean;
  volume: number;
  isPlaying: boolean;
  onToggleSolo: () => void;
  onToggleMute: () => void;
  onVolumeChange: (vol: number) => void;
  onTogglePlay: () => void;
}

export function StemCard({
  stem,
  taskId,
  isSolo,
  isMuted,
  volume,
  isPlaying,
  onToggleSolo,
  onToggleMute,
  onVolumeChange,
  onTogglePlay,
}: StemCardProps) {
  const colorMap: Record<string, string> = {
    vocals: 'from-rose-500 to-pink-500',
    accompaniment: 'from-indigo-500 to-blue-500',
    drums: 'from-amber-500 to-orange-500',
    bass: 'from-emerald-500 to-green-500',
    other: 'from-purple-500 to-violet-500',
  };

  const gradient = colorMap[stem.stem_id] ?? 'from-gray-500 to-gray-400';

  return (
    <Card className={cn('overflow-hidden transition-all', isMuted && 'opacity-50', isSolo && 'ring-2 ring-primary')}>
      {/* 顶部色条 */}
      <div className={cn('h-1.5 bg-gradient-to-r', gradient)} />

      <CardContent className="p-4">
        {/* 标题行 */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-foreground">{stem.label}</h4>
            {isSolo && (
              <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">
                SOLO
              </span>
            )}
            {isMuted && (
              <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                MUTE
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <a
              href={getDownloadUrl(taskId, stem.stem_id)}
              download
              className="inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              title="下载此音轨"
            >
              <Download className="h-4 w-4" />
            </a>
          </div>
        </div>

        {/* 迷你波形占位 */}
        <div className="mb-3 flex h-12 items-end gap-[1px] rounded-md bg-muted/50 p-1">
          {stem.waveform_data
            ? stem.waveform_data.slice(0, 80).map((v, i) => (
                <div
                  key={i}
                  className={cn(
                    'flex-1 rounded-sm',
                    isPlaying ? 'bg-primary' : 'bg-primary/30',
                  )}
                  style={{ height: `${Math.abs(v) * 100}%` }}
                />
              ))
            : Array.from({ length: 60 }).map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    'flex-1 rounded-sm',
                    isPlaying ? 'bg-primary animate-pulse' : 'bg-primary/30',
                  )}
                  style={{ height: `${10 + Math.random() * 80}%` }}
                />
              ))}
        </div>

        {/* 控制区 */}
        <div className="space-y-3">
          {/* Solo / Mute */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Switch checked={isSolo} onCheckedChange={() => onToggleSolo()} id={`solo-${stem.stem_id}`} />
              <Label htmlFor={`solo-${stem.stem_id}`} className="text-xs cursor-pointer">独奏</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={isMuted} onCheckedChange={() => onToggleMute()} id={`mute-${stem.stem_id}`} />
              <Label htmlFor={`mute-${stem.stem_id}`} className="text-xs cursor-pointer">静音</Label>
            </div>
            <div className="flex-1" />
            <Button variant="ghost" size="icon" onClick={onTogglePlay} title={isPlaying ? '暂停' : '试听'}>
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
          </div>

          {/* 音量 */}
          <div className="flex items-center gap-3">
            <Volume2 className="h-4 w-4 text-muted-foreground shrink-0" />
            <Slider
              value={[volume * 100]}
              min={0}
              max={100}
              step={1}
              onValueChange={([v]) => onVolumeChange(v! / 100)}
            />
            <span className="text-xs text-muted-foreground w-8 text-right">
              {Math.round(volume * 100)}%
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
