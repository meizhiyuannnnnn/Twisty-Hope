import { create } from 'zustand';
import type { StemId, PlayState, TrackState } from '@/types';

interface PlayerState {
  // ---- 播放状态 ----
  playState: PlayState;
  setPlayState: (s: PlayState) => void;
  currentTime: number;
  setCurrentTime: (t: number) => void;
  duration: number;
  setDuration: (d: number) => void;

  // ---- 音轨控制 ----
  tracks: TrackState[];
  initTracks: (tracks: { stemId: StemId; label: string }[]) => void;
  toggleSolo: (stemId: StemId) => void;
  toggleMute: (stemId: StemId) => void;
  setVolume: (stemId: StemId, vol: number) => void;

  // ---- 全局 ----
  isGlobalPlaying: boolean;
  setIsGlobalPlaying: (v: boolean) => void;

  // ---- 试听模式（独立于 solo/mute，不污染轨道状态） ----
  auditioningStemId: string | null;
  setAuditioningStemId: (id: string | null) => void;

  // ---- 重置 ----
  resetPlayer: () => void;
}

export const usePlayerStore = create<PlayerState>((set) => ({
  playState: 'idle',
  setPlayState: (s) => set({ playState: s }),
  currentTime: 0,
  setCurrentTime: (t) => set({ currentTime: t }),
  duration: 0,
  setDuration: (d) => set({ duration: d }),

  tracks: [],
  initTracks: (items) =>
    set({
      tracks: items.map((it) => ({
        stemId: it.stemId,
        label: it.label,
        solo: false,
        mute: false,
        volume: 0.8,
      })),
    }),
  toggleSolo: (stemId) =>
    set((s) => {
      const tracks = s.tracks.map((t) =>
        t.stemId === stemId ? { ...t, solo: !t.solo, mute: false } : t,
      );
      return { tracks };
    }),
  toggleMute: (stemId) =>
    set((s) => {
      const tracks = s.tracks.map((t) =>
        t.stemId === stemId ? { ...t, mute: !t.mute, solo: false } : t,
      );
      return { tracks };
    }),
  setVolume: (stemId, vol) =>
    set((s) => ({
      tracks: s.tracks.map((t) => (t.stemId === stemId ? { ...t, volume: vol } : t)),
    })),

  isGlobalPlaying: false,
  setIsGlobalPlaying: (v) => set({ isGlobalPlaying: v }),

  auditioningStemId: null,
  setAuditioningStemId: (id) => set({ auditioningStemId: id }),

  resetPlayer: () =>
    set({
      playState: 'idle',
      currentTime: 0,
      duration: 0,
      tracks: [],
      isGlobalPlaying: false,
      auditioningStemId: null,
    }),
}));
