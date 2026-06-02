import { Clock, Trash2, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';
import type { HistoryEntry } from '@/types';

interface HistoryListProps {
  entries: HistoryEntry[];
  onSelect: (entry: HistoryEntry) => void;
  onRemove: (id: string) => void;
  onClearAll: () => void;
}

export function HistoryList({ entries, onSelect, onRemove, onClearAll }: HistoryListProps) {
  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-6 text-muted-foreground">
        <Clock className="h-8 w-8 opacity-30" />
        <p className="text-sm">暂无处理记录</p>
        <p className="text-xs">处理过的音频会出现在这里</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-foreground">最近处理 ({entries.length})</h4>
        <Button variant="ghost" size="sm" onClick={onClearAll} className="text-xs text-muted-foreground hover:text-destructive">
          清空全部
        </Button>
      </div>

      <div className="space-y-2">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className={cn(
              'flex items-center gap-3 rounded-lg border border-app-border bg-card p-3 transition-colors hover:bg-accent/50',
            )}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{entry.fileName}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary" className="text-[10px]">
                  {entry.mode === '2track' ? '人声分离' : '4轨分离'}
                </Badge>
                <span className="text-[10px] text-muted-foreground">
                  {new Date(entry.createdAt).toLocaleDateString('zh-CN', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => onSelect(entry)}
                title="查看详情"
              >
                <ExternalLink className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                onClick={() => onRemove(entry.id)}
                title="删除记录"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
