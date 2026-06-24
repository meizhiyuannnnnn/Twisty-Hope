/**
 * Unit tests for utility functions — file format/size validation, time formatting.
 */

import { describe, it, expect } from 'vitest';
import {
  formatDuration,
  formatFileSize,
  formatPercent,
  validateFileFormat,
  validateFileSize,
} from '@/utils/format';

// ═══════════════════════════════════════════════════════════════════════════
// validateFileFormat
// ═══════════════════════════════════════════════════════════════════════════

describe('validateFileFormat', () => {
  it('应识别 .mp3 格式', () => {
    expect(validateFileFormat('song.mp3')).toBe('mp3');
  });

  it('应识别 .wav 格式', () => {
    expect(validateFileFormat('track.wav')).toBe('wav');
  });

  it('应识别 .flac 格式', () => {
    expect(validateFileFormat('lossless.flac')).toBe('flac');
  });

  it('应识别 .m4a 格式', () => {
    expect(validateFileFormat('audio.m4a')).toBe('m4a');
  });

  it('应识别 .ogg 格式', () => {
    expect(validateFileFormat('sound.ogg')).toBe('ogg');
  });

  it('应识别大写扩展名', () => {
    expect(validateFileFormat('SONG.MP3')).toBe('mp3');
  });

  it('应拒绝 .txt 文件', () => {
    expect(validateFileFormat('notes.txt')).toBeNull();
  });

  it('应拒绝 .pdf 文件', () => {
    expect(validateFileFormat('doc.pdf')).toBeNull();
  });

  it('应拒绝无扩展名文件', () => {
    expect(validateFileFormat('audiofile')).toBeNull();
  });

  it('应识别多点的文件名', () => {
    expect(validateFileFormat('my.song.name.mp3')).toBe('mp3');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// validateFileSize
// ═══════════════════════════════════════════════════════════════════════════

describe('validateFileSize', () => {
  const MAX = 100 * 1024 * 1024; // 100MB

  it('应接受小于上限的文件', () => {
    expect(validateFileSize(1024, MAX)).toBe(true);
  });

  it('应接受恰好等于上限的文件', () => {
    expect(validateFileSize(MAX, MAX)).toBe(true);
  });

  it('应拒绝超出上限的文件', () => {
    expect(validateFileSize(MAX + 1, MAX)).toBe(false);
  });

  it('应默认上限为 100MB', () => {
    expect(validateFileSize(50 * 1024 * 1024)).toBe(true);
  });

  it('应接受 0 字节文件（由后端二次校验）', () => {
    expect(validateFileSize(0, MAX)).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// formatDuration
// ═══════════════════════════════════════════════════════════════════════════

describe('formatDuration', () => {
  it('0 秒应格式化为 "00:00"', () => {
    expect(formatDuration(0)).toBe('00:00');
  });

  it('59 秒应格式化为 "00:59"', () => {
    expect(formatDuration(59)).toBe('00:59');
  });

  it('60 秒应格式化为 "01:00"', () => {
    expect(formatDuration(60)).toBe('01:00');
  });

  it('61 秒应格式化为 "01:01"', () => {
    expect(formatDuration(61)).toBe('01:01');
  });

  it('3599 秒应格式化为 "59:59"', () => {
    expect(formatDuration(3599)).toBe('59:59');
  });

  it('3600 秒应格式化为 "01:00:00"', () => {
    expect(formatDuration(3600)).toBe('01:00:00');
  });

  it('3661 秒应格式化为 "01:01:01"', () => {
    expect(formatDuration(3661)).toBe('01:01:01');
  });

  it('典型歌曲长度（245 秒）应为 "04:05"', () => {
    expect(formatDuration(245)).toBe('04:05');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// formatFileSize
// ═══════════════════════════════════════════════════════════════════════════

describe('formatFileSize', () => {
  it('0 字节应为 "0 B"', () => {
    expect(formatFileSize(0)).toBe('0 B');
  });

  it('500 字节应为 "500 B"', () => {
    expect(formatFileSize(500)).toBe('500 B');
  });

  it('1024 字节应为 "1.0 KB"', () => {
    expect(formatFileSize(1024)).toBe('1.0 KB');
  });

  it('1536 字节应为 "1.5 KB"', () => {
    expect(formatFileSize(1536)).toBe('1.5 KB');
  });

  it('1048576 字节应为 "1.0 MB"', () => {
    expect(formatFileSize(1048576)).toBe('1.0 MB');
  });

  it('5MB 文件应正确格式化', () => {
    expect(formatFileSize(5 * 1024 * 1024)).toBe('5.0 MB');
  });

  it('50MB 文件应正确格式化', () => {
    expect(formatFileSize(50 * 1024 * 1024)).toBe('50.0 MB');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// formatPercent
// ═══════════════════════════════════════════════════════════════════════════

describe('formatPercent', () => {
  it('0 应为 "0%"', () => {
    expect(formatPercent(0)).toBe('0%');
  });

  it('50 应为 "50%"', () => {
    expect(formatPercent(50)).toBe('50%');
  });

  it('100 应为 "100%"', () => {
    expect(formatPercent(100)).toBe('100%');
  });

  it('33.3 应四舍五入为 "33%"', () => {
    expect(formatPercent(33.3)).toBe('33%');
  });
});
