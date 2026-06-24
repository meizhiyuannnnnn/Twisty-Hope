import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';

interface PitchControlProps {
  pitch: number;
  onPitchChange: (pitch: number) => void;
  disabled?: boolean;
}

const PRESETS = [
  { label: '-5', value: -5 },
  { label: '-3', value: -3 },
  { label: '0', value: 0 },
  { label: '+3', value: 3 },
  { label: '+5', value: 5 },
];

export function PitchControl({ pitch, onPitchChange, disabled }: PitchControlProps) {
  const sign = pitch > 0 ? '+' : '';
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-foreground">变调</h4>
        <span className="text-2xl font-bold text-primary tabular-nums">
          {sign}{pitch} <span className="text-sm text-muted-foreground">半音</span>
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground w-8">-12</span>
        <Slider
          value={[pitch]}
          min={-12}
          max={12}
          step={1}
          onValueChange={([v]) => onPitchChange(v!)}
          disabled={disabled}
          className="flex-1"
        />
        <span className="text-xs text-muted-foreground w-8">+12</span>
      </div>

      <div className="flex gap-2">
        {PRESETS.map((preset) => (
          <Button
            key={preset.label}
            variant={pitch === preset.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => onPitchChange(preset.value)}
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
