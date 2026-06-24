import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';

interface SpeedControlProps {
  speed: number;
  onSpeedChange: (speed: number) => void;
  disabled?: boolean;
}

const PRESETS = [
  { label: '0.5x', value: 0.5 },
  { label: '0.75x', value: 0.75 },
  { label: '1x', value: 1.0 },
  { label: '1.25x', value: 1.25 },
  { label: '1.5x', value: 1.5 },
];

export function SpeedControl({ speed, onSpeedChange, disabled }: SpeedControlProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-foreground">变速</h4>
        <span className="text-2xl font-bold text-primary tabular-nums">
          {speed.toFixed(2)}x
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground w-8">50%</span>
        <Slider
          value={[speed * 100]}
          min={50}
          max={150}
          step={1}
          onValueChange={([v]) => onSpeedChange(v! / 100)}
          disabled={disabled}
          className="flex-1"
        />
        <span className="text-xs text-muted-foreground w-8">150%</span>
      </div>

      <div className="flex gap-2">
        {PRESETS.map((preset) => (
          <Button
            key={preset.label}
            variant={Math.abs(speed - preset.value) < 0.005 ? 'default' : 'outline'}
            size="sm"
            onClick={() => onSpeedChange(preset.value)}
            disabled={disabled}
            className="flex-1"
          >
            {preset.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
