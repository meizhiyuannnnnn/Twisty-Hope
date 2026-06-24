import { useEffect, useRef, useState, useMemo } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Music, Wand2, Waves, Clock, AlertTriangle } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { FileUpload } from '@/components/common/FileUpload';
import { StemCard } from '@/components/common/StemCard';
import { GlobalPlayer } from '@/components/common/GlobalPlayer';
import { ChordDisplay } from '@/components/common/ChordDisplay';
import { HistoryList } from '@/components/common/HistoryList';

import { useFileUpload } from '@/hooks/useFileUpload';
import { useWebSocket, connectWebSocket } from '@/hooks/useWebSocket';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { useHistory } from '@/hooks/useHistory';

import { useAppStore } from '@/stores/useAppStore';
import { usePlayerStore } from '@/stores/usePlayerStore';

import * as api from '@/services/api';

import type { SeparationMode, HistoryEntry, TaskProgress } from '@/types';
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
    chords,
    setChords,
    isChordLoading,
    setIsChordLoading,
    activeTab,
    setActiveTab,
    resetAll,
    restoreFromHistory,
  } = useAppStore();

  const {
    tracks,
    initTracks,
    toggleSolo,
    toggleMute,
    setVolume,
    resetPlayer,
  } = usePlayerStore();

  const { lastMessage, disconnect: wsDisconnect } = useWebSocket(taskId, token);
  const { loadAudio, play, pause, stop, seek, updateVolume, updateMute, updateSolo } = useAudioPlayer();
  const history = useHistory();
  const auditioningStemId = usePlayerStore((s) => s.auditioningStemId);

  // ── 防重复处理守卫 ── 同一 task_id + status 组合只处理一次
  const lastProcessedKeyRef = useRef('');
  // ── 操作纪元 ── 每次新上传递增，防止旧回调污染新状态
  const mutationEpochRef = useRef(0);
  // ── 处理计时器 ── 记录开始处理的时间戳，用于展示耗时
  const processingStartRef = useRef<number>(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // ---- WebSocket 消息处理 ----
  // 路径 A：hook → lastMessage → 同步到 store
  useEffect(() => {
    if (lastMessage) {
      setTaskProgress(lastMessage);
    }
  }, [lastMessage, setTaskProgress]);

  // 路径 B：store.taskProgress 变化 → 处理完成/失败
  useEffect(() => {
    if (!taskProgress) return;
    // 防重复处理
    const key = `${taskProgress.task_id}-${taskProgress.status}`;
    if (key === lastProcessedKeyRef.current) return;
    lastProcessedKeyRef.current = key;

    if (taskProgress.status === 'completed' && taskProgress.stems) {
      setStems(taskProgress.stems);
      const modeLabels = separationMode === '2track' ? TRACK_2_LABELS : TRACK_4_LABELS;
      initTracks(
        taskProgress.stems.map((s) => ({
          stemId: s.stem_id,
          label: s.label ?? (modeLabels as Record<string, string>)[s.stem_id] ?? s.stem_id,
        })),
      );
      // 预加载音频
      taskProgress.stems.forEach((s) => {
        loadAudio(s.stem_id, s.url).catch(() => {
          // 预加载失败不影响使用
        });
      });
      // 写入历史记录（含 token，支持恢复）
      history.addEntry({
        id: taskProgress.task_id,
        taskId: taskProgress.task_id,
        token: token ?? '',
        fileName: file?.name ?? '未知文件',
        mode: separationMode,
        stems: taskProgress.stems,
        createdAt: new Date().toISOString(),
      });
    }
    if (taskProgress.status === 'failed') {
      history.addEntry({
        id: taskProgress.task_id,
        taskId: taskProgress.task_id,
        token: token ?? '',
        fileName: file?.name ?? '未知文件',
        mode: separationMode,
        stems: [],
        createdAt: new Date().toISOString(),
      });
    }
    // 和弦分析完成 → 拉取和弦结果
    if (taskProgress.status === 'completed') {
      const { isChordLoading: loading, taskId: tid, token: tok } = useAppStore.getState();
      if (loading && tid && tok) {
        api.getTaskDetail(tid, tok).then((detail) => {
          if (detail.chord_result?.chords) {
            const chords = detail.chord_result.chords.map((c, i) => ({
              id: `${tid}-${i}`,
              chord: c.chord,
              degree: '',
              start_time: c.start,
              end_time: c.end,
            }));
            setChords(chords);
          }
          setIsChordLoading(false);
        }).catch(() => {
          setIsChordLoading(false);
        });
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskProgress, separationMode]);

  // ---- 上传 ----
  const uploadMutation = useMutation({
    mutationFn: (f: File) => {
      setProgress(0);
      return api.uploadFile(f, (p) => setProgress(p));
    },
    onSuccess: (data) => {
      // 防止旧上传回调污染新操作状态
      if (mutationEpochRef.current === 0) return;
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
      // 检查返回的 task_id 是否与当前 store 一致（防止旧回调污染）
      const { taskId: currentTid } = useAppStore.getState();
      if (data.task_id !== currentTid) return;
      // 后端 HTTP 返回 progress_message，前端统一用 message
      const httpData = data as TaskProgress & { progress_message?: string };
      const tp: TaskProgress = { ...data, message: httpData.progress_message ?? data.message ?? '' };
      setTaskProgress(tp);
      // WebSocket 已由 useWebSocket hook 自动连接（taskId 变化时触发）
      // 若需强制刷新连接，调用方可通过 store 更新 taskId 触发
    },
    onError: () => {
      setTaskProgress({ task_id: '', status: 'failed', progress: 0, message: '分离请求失败，请重试', error: '请求失败' });
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
    onSuccess: () => {
      // triggerChordAnalysis 返回 TaskResponse（异步处理），
      // 和弦结果通过 WebSocket 完成消息触发拉取
    },
    onError: () => {
      setIsChordLoading(false);
    },
  });

  // ---- 操作函数 ----
  const handleStartSeparation = () => {
    if (!file) return;
    // 清理上一次操作的残留状态
    stop();
    resetPlayer();
    setStems([]);
    setTaskProgress(null);
    setElapsedSeconds(0);
    lastProcessedKeyRef.current = '';
    // 启动处理计时器
    processingStartRef.current = Date.now();
    // 递增纪元，使旧 mutation 回调失效
    mutationEpochRef.current += 1;
    uploadMutation.mutate(file.file);
  };

  const handleModeSwitch = (mode: SeparationMode) => {
    if (mode === separationMode) return; // 相同模式，无需切换
    setSeparationMode(mode);
    if (taskId && token) {
      // 切换模式时重置结果，让用户看到正在处理的反馈
      stop();
      resetPlayer();
      setStems([]);
      setTaskProgress(null);
      lastProcessedKeyRef.current = '';
      separateMutation.mutate({ mode });
    }
  };

  const handleAnalyzeChords = () => {
    if (taskId && chords.length === 0) {
      chordMutation.mutate();
    }
  };

  const handlePlay = () => {
    // 全局播放时退出试听模式
    usePlayerStore.getState().setAuditioningStemId(null);
    play();
  };

  const handlePause = () => {
    // 全局暂停时退出试听模式
    usePlayerStore.getState().setAuditioningStemId(null);
    pause();
  };

  const handleSeek = (time: number) => {
    seek(time);
  };

  const handleReset = () => {
    stop();
    resetAll();
    resetPlayer();
    clearFile();
    setElapsedSeconds(0);
    processingStartRef.current = 0;
    lastProcessedKeyRef.current = '';
    mutationEpochRef.current = 0;
  };

  const handleHistorySelect = (entry: HistoryEntry) => {
    // 清理当前状态
    stop();
    wsDisconnect();
    resetPlayer();
    clearFile();
    // 恢复历史任务（已有 stems 直接展示，无需等待 WebSocket）
    restoreFromHistory(entry.taskId, entry.token, entry.stems);
    // 用 connectWebSocket 连接，避免闭包捕获旧 taskId/token
    const { setTaskProgress: setTP } = useAppStore.getState();
    connectWebSocket(entry.taskId, entry.token, setTP);
  };

  // ---- 加载/错误状态 ----
  const isPending = taskProgress?.status === 'pending';
  const isProcessing = taskProgress?.status === 'processing' || isPending;
  const isCompleted = taskProgress?.status === 'completed';
  const hasStems = stems.length > 0;
  const isUploadLoading = uploadMutation.isPending;
  const isSepLoading = separateMutation.isPending;

  // ── 处理计时器：运行时每秒更新耗时 ─────────────────────────────
  useEffect(() => {
    if (!isProcessing) {
      setElapsedSeconds(0);
      return;
    }
    if (processingStartRef.current === 0) {
      processingStartRef.current = Date.now();
    }
    const timer = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - processingStartRef.current) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [isProcessing]);

  // 耗时格式化
  const elapsedDisplay = useMemo(() => {
    const mins = Math.floor(elapsedSeconds / 60);
    const secs = elapsedSeconds % 60;
    if (mins > 0) return `${mins} 分 ${secs} 秒`;
    return `${secs} 秒`;
  }, [elapsedSeconds]);

  // 超过 2 分钟进度仍为 0 → 可能正在下载模型
  const isLikelyDownloadingModel = isProcessing && elapsedSeconds > 120 && (taskProgress?.progress ?? 0) === 0;

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
            disabled={isUploadLoading || isSepLoading || isProcessing}
            className="h-12 px-8 gap-2"
          >
            <Wand2 className="h-5 w-5" />
            {isUploadLoading ? '上传中...' : (isSepLoading || isProcessing) ? '处理中...' : '开始分离'}
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
              <div className="flex items-center gap-3 text-sm">
                <p className="font-medium text-primary">
                  {taskProgress?.progress ?? 0}%
                </p>
                <span className="text-muted-foreground">·</span>
                <span className="text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  已耗时 {elapsedDisplay}
                </span>
              </div>
              {/* 首次运行模型下载提示 */}
              {isLikelyDownloadingModel && (
                <div className="flex items-start gap-2 rounded-md bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 px-3 py-2 max-w-md">
                  <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
                  <div className="text-xs text-amber-800 dark:text-amber-200">
                    <p className="font-medium">首次运行需下载 AI 模型（约 300MB）</p>
                    <p className="mt-0.5">下载进度将在完成后显示，请耐心等待。后续处理将直接使用缓存模型。</p>
                  </div>
                </div>
              )}
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
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="separate" className="gap-1.5">
                <Waves className="h-4 w-4" />
                音轨
              </TabsTrigger>
              <TabsTrigger value="chords" className="gap-1.5" onClick={handleAnalyzeChords}>
                <Music className="h-4 w-4" />
                和弦
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
                      isPlaying={auditioningStemId === stem.stem_id}
                      onToggleSolo={() => {
                        toggleSolo(stem.stem_id);
                        updateSolo();
                      }}
                      onToggleMute={() => {
                        toggleMute(stem.stem_id);
                        const newMuted = !track?.mute;
                        updateMute(stem.stem_id, newMuted);
                      }}
                      onVolumeChange={(vol) => {
                        setVolume(stem.stem_id, vol);
                        updateVolume(stem.stem_id, vol);
                      }}
                      onTogglePlay={() => {
                        const store = usePlayerStore.getState();
                        if (store.auditioningStemId === stem.stem_id) {
                          // 停止试听当前轨 → stop() 会清除 auditioningStemId
                          stop();
                        } else {
                          // 开始试听：不修改其他轨道的 mute/solo 状态
                          stop();
                          store.setAuditioningStemId(stem.stem_id);
                          play();
                        }
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
