import { useEffect, useRef, useCallback } from 'react';
import { usePlayerStore } from '@/stores/usePlayerStore';

export function useAudioPlayer() {
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceNodesRef = useRef<Map<string, AudioBufferSourceNode>>(new Map());
  const gainNodesRef = useRef<Map<string, GainNode>>(new Map());
  const buffersRef = useRef<Map<string, AudioBuffer>>(new Map());
  const startTimeRef = useRef(0);
  const pauseOffsetRef = useRef(0);
  const animFrameRef = useRef<number>(0);

  const {
    setPlayState,
    setCurrentTime,
    setDuration,
    duration,
  } = usePlayerStore();

  // 初始化 AudioContext
  const ensureContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext();
    }
    if (audioContextRef.current.state === 'suspended') {
      void audioContextRef.current.resume();
    }
    return audioContextRef.current;
  }, []);

  // 加载音频
  const loadAudio = useCallback(async (stemId: string, url: string) => {
    const ctx = ensureContext();
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to fetch audio: ${response.status}`);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
    buffersRef.current.set(stemId, audioBuffer);
    // 更新总时长 = 最长的 stem
    const currentDuration = usePlayerStore.getState().duration;
    if (audioBuffer.duration > currentDuration) {
      setDuration(audioBuffer.duration);
    }
    return audioBuffer;
  }, [ensureContext, setDuration]);

  // 创建音源节点
  const createSourceNodes = useCallback(
    (stemId: string, buffer: AudioBuffer) => {
      const ctx = ensureContext();
      const source = ctx.createBufferSource();
      source.buffer = buffer;
      source.loop = false;

      const gain = ctx.createGain();
      gain.gain.value = 0.8;
      source.connect(gain);
      gain.connect(ctx.destination);

      sourceNodesRef.current.set(stemId, source);
      gainNodesRef.current.set(stemId, gain);

      return { source, gain };
    },
    [ensureContext],
  );

  // 播放
  const play = useCallback(() => {
    // 取消任何正在运行的进度更新循环（防止多个 rAF 并存）
    cancelAnimationFrame(animFrameRef.current);
    // 没有加载完成的音频缓冲区，不播放
    if (buffersRef.current.size === 0) return;

    const ctx = ensureContext();
    // 确保 AudioContext 已恢复（浏览器自动播放策略要求用户手势）
    if (ctx.state === 'suspended') {
      ctx.resume().catch(() => { /* 忽略自动播放策略限制 */ });
    }
    const offset = pauseOffsetRef.current;

    // 停止所有已有的音源
    sourceNodesRef.current.forEach((source) => {
      try { source.stop(); } catch { /* already stopped */ }
    });
    sourceNodesRef.current.clear();
    gainNodesRef.current.clear();

    // 读取最新 store 状态，避免闭包过期
    const { tracks, auditioningStemId } = usePlayerStore.getState();

    if (auditioningStemId) {
      // ── 试听模式：只播放被试听的单轨，忽略 solo/mute ──
      buffersRef.current.forEach((buffer, stemId) => {
        if (stemId !== auditioningStemId) return;
        const track = tracks.find((t) => t.stemId === stemId);
        const { source, gain } = createSourceNodes(stemId, buffer);
        const vol = Math.max(0, Math.min(1, track?.volume ?? 0.8));
        gain.gain.value = vol;
        source.start(0, offset);
      });
    } else {
      // ── 正常模式：按 solo/mute 规则播放 ──
      const anySoloed = tracks.some((t) => t.solo);
      buffersRef.current.forEach((buffer, stemId) => {
        const track = tracks.find((t) => t.stemId === stemId);
        if (!track) return;
        // solo 生效时：只播放 solo 的轨道
        if (anySoloed && !track.solo) return;
        // 正常模式：跳过 mute 的轨道
        if (!anySoloed && track.mute) return;

        const { source, gain } = createSourceNodes(stemId, buffer);
        const vol = Math.max(0, Math.min(1, track.volume ?? 0.8));
        gain.gain.value = vol;
        source.start(0, offset);
      });
    }

    startTimeRef.current = ctx.currentTime - offset;
    usePlayerStore.getState().setIsGlobalPlaying(true);
    setPlayState('playing');

    // 更新进度
    const currentDuration = usePlayerStore.getState().duration;
    const updateTime = () => {
      if (!audioContextRef.current) return;
      const elapsed = audioContextRef.current.currentTime - startTimeRef.current;
      setCurrentTime(elapsed);
      if (elapsed >= currentDuration) {
        pause();
        setCurrentTime(0);
        pauseOffsetRef.current = 0;
      } else {
        animFrameRef.current = requestAnimationFrame(updateTime);
      }
    };
    animFrameRef.current = requestAnimationFrame(updateTime);
  }, [ensureContext, createSourceNodes, pause, setPlayState, setCurrentTime]);

  // 暂停
  const pause = useCallback(() => {
    cancelAnimationFrame(animFrameRef.current);

    sourceNodesRef.current.forEach((source) => {
      try { source.stop(); } catch { /* already stopped */ }
    });
    sourceNodesRef.current.clear();
    gainNodesRef.current.clear();

    if (audioContextRef.current) {
      pauseOffsetRef.current = audioContextRef.current.currentTime - startTimeRef.current;
    }

    usePlayerStore.getState().setIsGlobalPlaying(false);
    setPlayState('paused');
  }, [setPlayState]);

  // 停止
  const stop = useCallback(() => {
    cancelAnimationFrame(animFrameRef.current);
    sourceNodesRef.current.forEach((source) => {
      try { source.stop(); } catch { /* already stopped */ }
    });
    sourceNodesRef.current.clear();
    gainNodesRef.current.clear();
    pauseOffsetRef.current = 0;
    setCurrentTime(0);
    usePlayerStore.getState().setIsGlobalPlaying(false);
    usePlayerStore.getState().setAuditioningStemId(null);
    setPlayState('idle');
  }, [setPlayState, setCurrentTime]);

  // 跳转
  const seek = useCallback(
    (time: number) => {
      pauseOffsetRef.current = Math.max(0, Math.min(time, duration));
      setCurrentTime(pauseOffsetRef.current);
      if (usePlayerStore.getState().isGlobalPlaying) {
        play();
      }
    },
    [duration, play, setCurrentTime],
  );

  // 更新音量
  const updateVolume = useCallback((stemId: string, volume: number) => {
    const gain = gainNodesRef.current.get(stemId);
    if (gain) {
      gain.gain.value = Math.max(0, Math.min(1, volume));
    }
  }, []);

  // 批量应用所有轨道的 solo/mute/volume 到 gain 节点（实时生效）
  const applyTrackStates = useCallback(() => {
    const { tracks: currentTracks, auditioningStemId } = usePlayerStore.getState();

    if (auditioningStemId) {
      // 试听模式：只让被试听轨道出声，其余静音
      currentTracks.forEach((t) => {
        const gain = gainNodesRef.current.get(t.stemId);
        if (!gain) return;
        const vol = Math.max(0, Math.min(1, t.volume ?? 0.8));
        gain.gain.value = t.stemId === auditioningStemId ? vol : 0;
      });
    } else {
      // 正常模式：solo 优先于 mute
      const anySoloed = currentTracks.some((t) => t.solo);
      currentTracks.forEach((t) => {
        const gain = gainNodesRef.current.get(t.stemId);
        if (!gain) return;
        const effectiveMute = anySoloed ? !t.solo : t.mute;
        const vol = Math.max(0, Math.min(1, t.volume ?? 0.8));
        gain.gain.value = effectiveMute ? 0 : vol;
      });
    }
  }, []);

  // 更新静音（实时）
  const updateMute = useCallback((stemId: string, muted: boolean) => {
    const gain = gainNodesRef.current.get(stemId);
    if (gain) {
      const currentTracks = usePlayerStore.getState().tracks;
      const track = currentTracks.find((t) => t.stemId === stemId);
      const anySoloed = currentTracks.some((t) => t.solo);
      const effectiveMute = anySoloed ? !(track?.solo ?? false) : muted;
      const vol = Math.max(0, Math.min(1, track?.volume ?? 0.8));
      gain.gain.value = effectiveMute ? 0 : vol;
    }
  }, []);

  // 更新独奏（实时）— 切换 solo 后立即生效
  const updateSolo = useCallback(() => {
    applyTrackStates();
  }, [applyTrackStates]);

  // 清理
  useEffect(() => {
    return () => {
      cancelAnimationFrame(animFrameRef.current);
      sourceNodesRef.current.forEach((source) => {
        try { source.stop(); } catch { /* ok */ }
      });
      if (audioContextRef.current) {
        void audioContextRef.current.close();
      }
    };
  }, []);

  return {
    loadAudio,
    play,
    pause,
    stop,
    seek,
    updateVolume,
    updateMute,
    updateSolo,
  };
}
