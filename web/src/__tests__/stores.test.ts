/**
 * Unit tests for Zustand stores — useAppStore and usePlayerStore.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useAppStore } from '@/stores/useAppStore';
import { usePlayerStore } from '@/stores/usePlayerStore';
import type { AudioFile } from '@/types';

// ═══════════════════════════════════════════════════════════════════════════
// useAppStore
// ═══════════════════════════════════════════════════════════════════════════

describe('useAppStore — 初始状态', () => {
  beforeEach(() => {
    useAppStore.getState().resetAll();
  });

  it('currentFile 默认为 null', () => {
    expect(useAppStore.getState().currentFile).toBeNull();
  });

  it('uploadProgress 默认为 0', () => {
    expect(useAppStore.getState().uploadProgress).toBe(0);
  });

  it('isUploading 默认为 false', () => {
    expect(useAppStore.getState().isUploading).toBe(false);
  });

  it('separationMode 默认为 "2track"', () => {
    expect(useAppStore.getState().separationMode).toBe('2track');
  });

  it('taskId 默认为 null', () => {
    expect(useAppStore.getState().taskId).toBeNull();
  });

  it('token 默认为 null', () => {
    expect(useAppStore.getState().token).toBeNull();
  });

  it('taskProgress 默认为 null', () => {
    expect(useAppStore.getState().taskProgress).toBeNull();
  });

  it('stems 默认为空数组', () => {
    expect(useAppStore.getState().stems).toEqual([]);
  });

  it('transformParams 默认为 speed=1.0, pitch=0', () => {
    const { transformParams } = useAppStore.getState();
    expect(transformParams.speed).toBe(1.0);
    expect(transformParams.pitch).toBe(0);
  });

  it('isTransformDirty 默认为 false', () => {
    expect(useAppStore.getState().isTransformDirty).toBe(false);
  });

  it('chords 默认为空数组', () => {
    expect(useAppStore.getState().chords).toEqual([]);
  });

  it('chordNotation 默认为 "name"', () => {
    expect(useAppStore.getState().chordNotation).toBe('name');
  });

  it('isChordLoading 默认为 false', () => {
    expect(useAppStore.getState().isChordLoading).toBe(false);
  });

  it('activeTab 默认为 "separate"', () => {
    expect(useAppStore.getState().activeTab).toBe('separate');
  });
});

describe('useAppStore — 状态更新', () => {
  beforeEach(() => {
    useAppStore.getState().resetAll();
  });

  it('setCurrentFile 应更新 currentFile', () => {
    const mockFile: AudioFile = {
      id: 'file-1',
      name: 'test.mp3',
      size: 5000,
      format: 'mp3',
      file: new File([], 'test.mp3'),
      url: 'blob:test',
    };
    useAppStore.getState().setCurrentFile(mockFile);
    expect(useAppStore.getState().currentFile).toBe(mockFile);
  });

  it('setCurrentFile(null) 应清空文件', () => {
    const mockFile: AudioFile = {
      id: 'f1', name: 't.mp3', size: 100, format: 'mp3',
      file: new File([], 't.mp3'), url: 'blob:x',
    };
    useAppStore.getState().setCurrentFile(mockFile);
    useAppStore.getState().setCurrentFile(null);
    expect(useAppStore.getState().currentFile).toBeNull();
  });

  it('setSeparationMode 应切换到 4track', () => {
    useAppStore.getState().setSeparationMode('4track');
    expect(useAppStore.getState().separationMode).toBe('4track');
  });

  it('setTaskId 应更新 taskId', () => {
    useAppStore.getState().setTaskId('task-abc-123');
    expect(useAppStore.getState().taskId).toBe('task-abc-123');
  });

  it('setUploadProgress 应更新进度', () => {
    useAppStore.getState().setUploadProgress(75);
    expect(useAppStore.getState().uploadProgress).toBe(75);
  });

  it('setStems 应更新音轨列表', () => {
    const stems = [
      { stem_id: 'vocals' as const, label: '人声', url: '/a.mp3' },
      { stem_id: 'drums' as const, label: '鼓', url: '/b.mp3' },
    ];
    useAppStore.getState().setStems(stems);
    expect(useAppStore.getState().stems).toHaveLength(2);
  });

  it('setTransformParams 应支持部分更新', () => {
    useAppStore.getState().setTransformParams({ speed: 1.5 });
    const { transformParams } = useAppStore.getState();
    expect(transformParams.speed).toBe(1.5);
    // pitch 应保持默认值
    expect(transformParams.pitch).toBe(0);
  });

  it('setTransformParams 应可同时更新多个字段', () => {
    useAppStore.getState().setTransformParams({ speed: 0.75, pitch: -3 });
    const { transformParams } = useAppStore.getState();
    expect(transformParams.speed).toBe(0.75);
    expect(transformParams.pitch).toBe(-3);
  });

  it('setChordNotation 应切换到 degree', () => {
    useAppStore.getState().setChordNotation('degree');
    expect(useAppStore.getState().chordNotation).toBe('degree');
  });

  it('setActiveTab 应切换到 chords', () => {
    useAppStore.getState().setActiveTab('chords');
    expect(useAppStore.getState().activeTab).toBe('chords');
  });

  it('setToken 应更新 token', () => {
    useAppStore.getState().setToken('my-token-abc');
    expect(useAppStore.getState().token).toBe('my-token-abc');
  });

  it('resetAll 应恢复大多数默认值', () => {
    // 先设置一些值
    useAppStore.getState().setTaskId('task-x');
    useAppStore.getState().setToken('some-token');
    useAppStore.getState().setSeparationMode('4track');
    useAppStore.getState().setUploadProgress(50);
    useAppStore.getState().setTransformParams({ speed: 1.5, pitch: 5 });

    // 重置
    useAppStore.getState().resetAll();

    expect(useAppStore.getState().taskId).toBeNull();
    expect(useAppStore.getState().token).toBeNull();
    expect(useAppStore.getState().uploadProgress).toBe(0);
    expect(useAppStore.getState().transformParams.speed).toBe(1.0);
    expect(useAppStore.getState().transformParams.pitch).toBe(0);
    expect(useAppStore.getState().separationMode).toBe('2track');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// usePlayerStore
// ═══════════════════════════════════════════════════════════════════════════

describe('usePlayerStore — 初始状态', () => {
  beforeEach(() => {
    usePlayerStore.getState().resetPlayer();
  });

  it('playState 默认为 "idle"', () => {
    expect(usePlayerStore.getState().playState).toBe('idle');
  });

  it('currentTime 默认为 0', () => {
    expect(usePlayerStore.getState().currentTime).toBe(0);
  });

  it('duration 默认为 0', () => {
    expect(usePlayerStore.getState().duration).toBe(0);
  });

  it('tracks 默认为空数组', () => {
    expect(usePlayerStore.getState().tracks).toEqual([]);
  });

  it('isGlobalPlaying 默认为 false', () => {
    expect(usePlayerStore.getState().isGlobalPlaying).toBe(false);
  });
});

describe('usePlayerStore — 音轨初始化', () => {
  beforeEach(() => {
    usePlayerStore.getState().resetPlayer();
  });

  it('initTracks 应创建音轨列表', () => {
    usePlayerStore.getState().initTracks([
      { stemId: 'vocals', label: '人声' },
      { stemId: 'drums', label: '鼓' },
    ]);

    const { tracks } = usePlayerStore.getState();
    expect(tracks).toHaveLength(2);
    expect(tracks[0].stemId).toBe('vocals');
    expect(tracks[0].label).toBe('人声');
    expect(tracks[1].stemId).toBe('drums');
    expect(tracks[1].label).toBe('鼓');
  });

  it('initTracks 应设置默认音量 0.8', () => {
    usePlayerStore.getState().initTracks([{ stemId: 'vocals', label: '人声' }]);
    expect(usePlayerStore.getState().tracks[0].volume).toBe(0.8);
  });

  it('initTracks 应设置 solo 和 mute 为 false', () => {
    usePlayerStore.getState().initTracks([{ stemId: 'bass', label: '贝斯' }]);
    const t = usePlayerStore.getState().tracks[0];
    expect(t.solo).toBe(false);
    expect(t.mute).toBe(false);
  });

  it('initTracks 空数组应正常', () => {
    usePlayerStore.getState().initTracks([]);
    expect(usePlayerStore.getState().tracks).toEqual([]);
  });
});

describe('usePlayerStore — 音轨控制', () => {
  beforeEach(() => {
    usePlayerStore.getState().resetPlayer();
    usePlayerStore.getState().initTracks([
      { stemId: 'vocals', label: '人声' },
      { stemId: 'drums', label: '鼓' },
      { stemId: 'bass', label: '贝斯' },
    ]);
  });

  it('toggleSolo 应切换 solo 状态', () => {
    usePlayerStore.getState().toggleSolo('vocals');
    expect(usePlayerStore.getState().tracks[0].solo).toBe(true);

    usePlayerStore.getState().toggleSolo('vocals');
    expect(usePlayerStore.getState().tracks[0].solo).toBe(false);
  });

  it('solo 时应取消 mute', () => {
    // 先 mute
    usePlayerStore.getState().toggleMute('vocals');
    expect(usePlayerStore.getState().tracks[0].mute).toBe(true);
    // 再 solo — 应取消 mute
    usePlayerStore.getState().toggleSolo('vocals');
    expect(usePlayerStore.getState().tracks[0].solo).toBe(true);
    expect(usePlayerStore.getState().tracks[0].mute).toBe(false);
  });

  it('toggleMute 应切换 mute 状态', () => {
    usePlayerStore.getState().toggleMute('drums');
    expect(usePlayerStore.getState().tracks[1].mute).toBe(true);

    usePlayerStore.getState().toggleMute('drums');
    expect(usePlayerStore.getState().tracks[1].mute).toBe(false);
  });

  it('mute 时应取消 solo', () => {
    // 先 solo
    usePlayerStore.getState().toggleSolo('bass');
    expect(usePlayerStore.getState().tracks[2].solo).toBe(true);
    // 再 mute — 应取消 solo
    usePlayerStore.getState().toggleMute('bass');
    expect(usePlayerStore.getState().tracks[2].mute).toBe(true);
    expect(usePlayerStore.getState().tracks[2].solo).toBe(false);
  });

  it('setVolume 应在 0-1 范围内', () => {
    usePlayerStore.getState().setVolume('vocals', 0.5);
    expect(usePlayerStore.getState().tracks[0].volume).toBe(0.5);
  });

  it('setVolume 边界值 0', () => {
    usePlayerStore.getState().setVolume('drums', 0);
    expect(usePlayerStore.getState().tracks[1].volume).toBe(0);
  });

  it('setVolume 边界值 1', () => {
    usePlayerStore.getState().setVolume('bass', 1);
    expect(usePlayerStore.getState().tracks[2].volume).toBe(1);
  });

  it('resetPlayer 应恢复默认值', () => {
    usePlayerStore.getState().toggleSolo('vocals');
    usePlayerStore.getState().setVolume('drums', 0.3);
    usePlayerStore.getState().setPlayState('idle');
    usePlayerStore.getState().setCurrentTime(120);

    usePlayerStore.getState().resetPlayer();

    expect(usePlayerStore.getState().tracks).toEqual([]);
    expect(usePlayerStore.getState().playState).toBe('idle');
    expect(usePlayerStore.getState().currentTime).toBe(0);
    expect(usePlayerStore.getState().duration).toBe(0);
    expect(usePlayerStore.getState().isGlobalPlaying).toBe(false);
  });
});

describe('usePlayerStore — 播放状态', () => {
  beforeEach(() => {
    usePlayerStore.getState().resetPlayer();
  });

  it('setPlayState 应更新播放状态', () => {
    usePlayerStore.getState().setPlayState('playing');
    expect(usePlayerStore.getState().playState).toBe('playing');
  });

  it('setCurrentTime 应更新当前时间', () => {
    usePlayerStore.getState().setCurrentTime(45.5);
    expect(usePlayerStore.getState().currentTime).toBe(45.5);
  });

  it('setDuration 应更新时长', () => {
    usePlayerStore.getState().setDuration(245);
    expect(usePlayerStore.getState().duration).toBe(245);
  });

  it('setIsGlobalPlaying 应更新全局播放', () => {
    usePlayerStore.getState().setIsGlobalPlaying(true);
    expect(usePlayerStore.getState().isGlobalPlaying).toBe(true);
  });
});
