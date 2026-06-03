import { useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Music, Wand2, Gauge, Waves } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { FileUpload } from '@/components/common/FileUpload';
import { StemCard } from '@/components/common/StemCard';
import { GlobalPlayer } from '@/components/common/GlobalPlayer';
import { SpeedControl } from '@/components/common/SpeedControl';
import { PitchControl } from '@/components/common/PitchControl';
import { ChordDisplay } from '@/components/common/ChordDisplay';
import { HistoryList } from '@/components/common/HistoryList';

import { useFileUpload } from '@/hooks/useFileUpload';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { useHistory } from '@/hooks/useHistory';

import { useAppStore } from '@/stores/useAppStore';
import { usePlayerStore } from '@/stores/usePlayerStore';

import * as api from '@/services/api';

import type { SeparationMode, HistoryEntry, TransformParams } from '@/types';
import { TRACK_2_LABELS, TRACK_4_LABELS } from '@/types';

export function HomePage() {
  // ---- Hooks ----
  const {
    file,
    isDragging,
    error: uploadError,
    progress: uploadProgress,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    clearFile,
    setProgress,
  } = useFileUpload();

  const {
    separationMode,
    setSeparationMode,
    taskId,
    setTaskId,
    token,
    setToken,
    taskProgress,
    setTaskProgress,
    stems,
    setStems,
    transformParams,
    setTransformParams,
    isTransformDirty,
    setIsTransformDirty,
    chords,
    setChords,
    isChordLoading,
    setIsChordLoading,
    activeTab,
    setActiveTab,
    resetAll,
  } = useAppStore();

  const {
    tracks,
    initTracks,
    toggleSolo,
    toggleMute,
    setVolume,
    resetPlayer,
  } = usePlayerStore();

  const { lastMessage, connect: wsConnect, disconnect: wsDisconnect } = useWebSocket(taskId, token);
  const { loadAudio, play, pause, stop, seek } = useAudioPlayer();
  const history = useHistory();

  // ---- WebSocket 消息处理 ----
  useEffect(() => {
    if (lastMessage) {
      setTaskProgress(lastMessage);
      if (lastMessage.status === 'completed' && lastMessage.stems) {
        setStems(lastMessage.stems);
        const modeLabels = separationMode === '2track' ? TRACK_2_LABELS : TRACK_4_LABELS;
        initTracks(
          lastMessage.stems.map((s) => ({
            stemId: s.stem_id,
            label: s.label ?? (modeLabels as Record<string, string>)[s.stem_id] ?? s.stem_id,
          })),
        );
        // 预加载音频
        lastMessage.stems.forEach((s) => {
          loadAudio(s.stem_id, s.url).catch(() => {
            // 预加载失败不影响使用
          });
        });
      }
    }
  }, [lastMessage, separationMode, setTaskProgress, setStems, initTracks, loadAudio]);

  // ---- 上传 ----
  const uploadMutation = useMutation({
    mutationFn: (f: File) => {
      setProgress(0);
      return api.uploadFile(f, (p) => setProgress(p));
    },
    onSuccess: (data) => {
      setTaskId(data.task_id);
      setToken(data.token);
      // 上传成功，自动开始分离
      separateMutation.mutate({ mode: separationMode });
    },
    onError: () => {
      setProgress(0);
    },
  });

  // ---- 分离 ----
  const separateMutation = useMutation({
    mutationFn: (params: { mode: SeparationMode }) => {
      const { taskId: tid, token: tok } = useAppStore.getState();
      if (!tid) throw new Error('无任务 ID');
      return api.triggerSeparation(tid, tok!, params);
    },
    onSuccess: (data) => {
      setTaskProgress(data);
      wsConnect();
    },
  });

  // ---- 和弦分析 ----
  const chordMutation = useMutation({
    mutationFn: () => {
      const { taskId: tid, token: tok } = useAppStore.getState();
      if (!tid) throw new Error('无任务 ID');
      setIsChordLoading(true);
      return api.triggerChordAnalysis(tid, tok!);
    },
    onSuccess: (data) => {
      setChords(data);
      setIsChordLoading(false);
    },
    onError: () => {
      setIsChordLoading(false);
    },
  });

  // ---- 变速变调 ----
  const transformMutation = useMutation({
    mutationFn: (params: TransformParams) => {
      const { taskId: tid, token: tok } = useAppStore.getState();
      if (!tid) throw new Error('无任务 ID');
      return api.triggerTransform(tid, tok!, params);
    },
    onSuccess: () => {
      setIsTransformDirty(false);
    },
  });

  // ---- 操作函数 ----
  const handleStartSeparation = () => {
    if (!file) return;
    uploadMutation.mutate(file.file);
  };

  const handleModeSwitch = (mode: SeparationMode) => {
    setSeparationMode(mode);
    if (taskId) {
      separateMutation.mutate({ mode });
    }
  };

  const handleAnalyzeChords = () => {
    if (taskId && chords.length === 0) {
      chordMutation.mutate();
    }
  };

  const handleApplyTransform = () => {
    if (taskId) {
      transformMutation.mutate(transformParams);
    }
  };

  const handlePlay = () => {
    if (stems.length > 0) {
      play();
    }
  };

  const handlePause = () => {
    pause();
  };

  const handleSeek = (time: number) => {
    seek(time);
  };

  const handleReset = () => {
    stop();
    wsDisconnect();
    resetAll();
    resetPlayer();
    clearFile();
  };

  const handleHistorySelect = (_entry: HistoryEntry) => {
    // 从历史恢复 - 这里作为占位，实际需要后端支持
    handleReset();
  };

  // ---- 加载/错误状态 ----
  const isProcessing = taskProgress?.status === 'processing';
  const isCompleted = taskProgress?.status === 'completed';
  const hasStems = stems.length > 0;
  const isUploadLoading = uploadMutation.isPending;
  const isSepLoading = separateMutation.isPending;
  const isTransforming = transformMutation.isPending;

  return (
    <div className="flex flex-col gap-6 px-4 py-6 max-w-5xl mx-auto w-full">
      {/* ====== 顶部导航 ====== */}
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary">
            <Waves className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground">音频分离工具</h1>
            <p className="text-xs text-muted-foreground">免费在线 · 人声伴奏分离</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {hasStems && (
            <Button variant="outline" size="sm" onClick={handleReset}>
              重新开始
            </Button>
          )}
        </div>
      </header>

      {/* ====== 文件上传区 ====== */}
      <FileUpload
        file={file}
        isDragging={isDragging}
        error={uploadError}
        progress={uploadProgress}
        isUploading={isUploadLoading}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onFileSelect={handleFileSelect}
        onClear={clearFile}
      />

      {/* ====== 模式选择 + 开始按钮 ====== */}
      {file && !hasStems && (
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-foreground">分离模式</p>
            <div className="flex rounded-lg border border-input p-0.5" role="radiogroup">
              {[
                { value: '2track' as const, label: '人声 + 伴奏', desc: '2 轨' },
                { value: '4track' as const, label: '多乐器分离', desc: '4 轨' },
              ].map((m) => (
                <button
                  key={m.value}
                  type="button"
                  role="radio"
                  aria-checked={separationMode === m.value}
                  className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                    separationMode === m.value
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                  onClick={() => setSeparationMode(m.value)}
                >
                  {m.label}
                  <span className="text-[10px] opacity-70">{m.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <Button
            size="lg"
            onClick={handleStartSeparation}
            disabled={isUploadLoading || isSepLoading}
            className="h-12 px-8 gap-2"
          >
            <Wand2 className="h-5 w-5" />
            {isUploadLoading ? '上传中...' : isSepLoading ? '处理中...' : '开始分离'}
          </Button>
        </div>
      )}

      {/* ====== 进度显示 ====== */}
      {isProcessing && (
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Music className="h-8 w-8 text-primary animate-pulse" />
              </div>
              <div className="text-center space-y-1">
                <p className="font-semibold text-foreground">正在处理中...</p>
                <p className="text-sm text-muted-foreground">{taskProgress?.message ?? '请稍候'}</p>
              </div>
              <Progress value={taskProgress?.progress ?? 0} className="h-3 w-full max-w-md" />
              <p className="text-sm font-medium text-primary">
                {taskProgress?.progress ?? 0}%
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ====== 错误状态 ====== */}
      {taskProgress?.status === 'failed' && (
        <Card className="border-destructive/50">
          <CardContent className="p-6">
            <div className="flex flex-col items-center gap-3 text-center">
              <p className="font-semibold text-destructive">处理失败</p>
              <p className="text-sm text-muted-foreground">{taskProgress.error ?? '未知错误，请重试'}</p>
              <Button variant="outline" size="sm" onClick={handleStartSeparation}>
                重试
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ====== 结果展示区 ====== */}
      {isCompleted && hasStems && (
        <div className="space-y-6">
          {/* 全局播放控制 */}
          <GlobalPlayer
            onPlay={handlePlay}
            onPause={handlePause}
            onSeek={handleSeek}
          />

          {/* 功能 Tab */}
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="separate" className="gap-1.5">
                <Waves className="h-4 w-4" />
                音轨
              </TabsTrigger>
              <TabsTrigger value="chords" className="gap-1.5" onClick={handleAnalyzeChords}>
                <Music className="h-4 w-4" />
                和弦
              </TabsTrigger>
              <TabsTrigger value="transform" className="gap-1.5">
                <Gauge className="h-4 w-4" />
                调节
              </TabsTrigger>
            </TabsList>

            {/* 音轨 Tab */}
            <TabsContent value="separate" className="mt-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-foreground">
                    {separationMode === '2track' ? '人声 + 伴奏' : '多乐器分离'}
                  </h3>
                  <Badge variant="secondary">{separationMode === '2track' ? '2轨' : '4轨'}</Badge>
                </div>
                <div className="flex rounded-lg border border-input p-0.5">
                  {[
                    { value: '2track' as const, label: '2轨' },
                    { value: '4track' as const, label: '4轨' },
                  ].map((m) => (
                    <button
                      key={m.value}
                      type="button"
                      className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                        separationMode === m.value
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:text-foreground'
                      }`}
                      onClick={() => handleModeSwitch(m.value)}
                      disabled={isSepLoading}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              {isSepLoading && (
                <div className="flex items-center justify-center py-12">
                  <Progress value={taskProgress?.progress ?? 0} className="h-2 w-64" />
                </div>
              )}

              <div className="grid gap-4 sm:grid-cols-2">
                {stems.map((stem) => {
                  const track = tracks.find((t) => t.stemId === stem.stem_id);
                  return (
                    <StemCard
                      key={stem.stem_id}
                      stem={{
                        ...stem,
                        label:
                          stem.label ??
                          (separationMode === '2track'
                            ? (TRACK_2_LABELS as Record<string, string>)[stem.stem_id]
                            : (TRACK_4_LABELS as Record<string, string>)[stem.stem_id]) ??
                          stem.stem_id,
                      }}
                      taskId={taskId ?? ''}
                      isSolo={track?.solo ?? false}
                      isMuted={track?.mute ?? false}
                      volume={track?.volume ?? 0.8}
                      isPlaying={false}
                      onToggleSolo={() => toggleSolo(stem.stem_id)}
                      onToggleMute={() => toggleMute(stem.stem_id)}
                      onVolumeChange={(vol) => setVolume(stem.stem_id, vol)}
                      onTogglePlay={() => {
                        // 单轨试听
                      }}
                    />
                  );
                })}
              </div>
            </TabsContent>

            {/* 和弦 Tab */}
            <TabsContent value="chords" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">和弦识别</CardTitle>
                </CardHeader>
                <CardContent>
                  {isChordLoading ? (
                    <div className="flex flex-col items-center gap-3 py-8">
                      <Music className="h-8 w-8 text-primary animate-pulse" />
                      <p className="text-sm text-muted-foreground">正在分析和弦...</p>
                    </div>
                  ) : (
                    <ChordDisplay
                      chords={chords}
                      taskId={taskId ?? ''}
                      onSeekTo={handleSeek}
                    />
                  )}

                  {chords.length === 0 && !isChordLoading && (
                    <div className="flex justify-center pt-2">
                      <Button variant="outline" size="sm" onClick={handleAnalyzeChords}>
                        <Music className="h-4 w-4 mr-1.5" />
                        开始分析和弦
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* 变速/变调 Tab */}
            <TabsContent value="transform" className="mt-4">
              <Card>
                <CardContent className="p-5 space-y-8">
                  <SpeedControl
                    speed={transformParams.speed}
                    onSpeedChange={(speed) => {
                      setTransformParams({ speed });
                      setIsTransformDirty(true);
                    }}
                    disabled={isTransforming}
                  />

                  <div className="border-t" />

                  <PitchControl
                    pitch={transformParams.pitch}
                    onPitchChange={(pitch) => {
                      setTransformParams({ pitch });
                      setIsTransformDirty(true);
                    }}
                    disabled={isTransforming}
                  />

                  {isTransformDirty && (
                    <div className="flex justify-center pt-2">
                      <Button
                        onClick={handleApplyTransform}
                        disabled={isTransforming}
                        className="gap-2"
                      >
                        <Wand2 className="h-4 w-4" />
                        {isTransforming ? '处理中...' : '应用效果'}
                      </Button>
                    </div>
                  )}

                  {isTransforming && (
                    <div className="flex items-center justify-center gap-3 text-sm text-muted-foreground">
                      <Wand2 className="h-4 w-4 animate-spin" />
                      正在处理音频...
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}

      {/* ====== 底部：历史记录 ====== */}
      <div className="mt-4 border-t pt-6">
        <HistoryList
          entries={history.entries}
          onSelect={handleHistorySelect}
          onRemove={history.removeEntry}
          onClearAll={history.clearAll}
        />
      </div>

      {/* ====== 脚注 ====== */}
      <footer className="mt-8 border-t pt-4 text-center">
        <p className="text-xs text-muted-foreground">
          音频分离工具 - 完全免费，无需注册，所有处理在本地完成
        </p>
      </footer>
    </div>
  );
}
