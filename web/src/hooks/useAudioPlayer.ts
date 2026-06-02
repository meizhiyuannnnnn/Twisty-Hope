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
    duration,
    tracks,
    isGlobalPlaying,
    setIsGlobalPlaying,
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
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
    buffersRef.current.set(stemId, audioBuffer);
    return audioBuffer;
  }, [ensureContext]);

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
    const ctx = ensureContext();
    const offset = pauseOffsetRef.current;

    // 停止所有已有的音源
    sourceNodesRef.current.forEach((source) => {
      try { source.stop(); } catch { /* already stopped */ }
    });
    sourceNodesRef.current.clear();
    gainNodesRef.current.clear();

    // 为每个未 mute 的音轨创建音源
    buffersRef.current.forEach((buffer, stemId) => {
      const track = tracks.find((t) => t.stemId === stemId);
      if (track?.mute) return;

      const { source, gain } = createSourceNodes(stemId, buffer);
      const vol = Math.max(0, Math.min(1, track?.volume ?? 0.8));
      gain.gain.value = vol;

      source.start(0, offset);
    });

    startTimeRef.current = ctx.currentTime - offset;
    setIsGlobalPlaying(true);
    setPlayState('playing');

    // 更新进度
    const updateTime = () => {
      if (!audioContextRef.current) return;
      const elapsed = audioContextRef.current.currentTime - startTimeRef.current;
      setCurrentTime(elapsed);
      if (elapsed >= duration) {
        pause();
        setCurrentTime(0);
        pauseOffsetRef.current = 0;
      } else {
        animFrameRef.current = requestAnimationFrame(updateTime);
      }
    };
    animFrameRef.current = requestAnimationFrame(updateTime);
  }, [ensureContext, createSourceNodes, tracks, duration, setPlayState, setCurrentTime, setIsGlobalPlaying]);

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

    setIsGlobalPlaying(false);
    setPlayState('paused');
  }, [setPlayState, setIsGlobalPlaying]);

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
    setIsGlobalPlaying(false);
    setPlayState('idle');
  }, [setPlayState, setCurrentTime, setIsGlobalPlaying]);

  // 跳转
  const seek = useCallback(
    (time: number) => {
      pauseOffsetRef.current = Math.max(0, Math.min(time, duration));
      setCurrentTime(pauseOffsetRef.current);
      if (isGlobalPlaying) {
        play();
      }
    },
    [duration, isGlobalPlaying, play, setCurrentTime],
  );

  // 更新音量
  const updateVolume = useCallback((stemId: string, volume: number) => {
    const gain = gainNodesRef.current.get(stemId);
    if (gain) {
      gain.gain.value = Math.max(0, Math.min(1, volume));
    }
  }, []);

  // 更新静音
  const updateMute = useCallback((stemId: string, muted: boolean) => {
    const gain = gainNodesRef.current.get(stemId);
    if (gain) {
      gain.gain.value = muted ? 0 : 0.8;
    }
  }, []);

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
  };
}
