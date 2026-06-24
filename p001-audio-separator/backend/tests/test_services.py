"""Unit tests for service layer — separator, transformer, cleaner, security.

All external dependencies (ffmpeg, Demucs model, DB, filesystem) are mocked.
"""

from __future__ import annotations

import os
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.separator import convert_stems_to_mp3, convert_to_mp3, get_separator
from app.core.security import check_rate_limit, generate_task_token


# ══════════════════════════════════════════════════════════════════════
# Token & Rate Limit Tests
# ══════════════════════════════════════════════════════════════════════


class TestGenerateTaskToken:
    """测试 token 生成"""

    def test_token_is_64_char_hex(self) -> None:
        """token 应为 64 字符的十六进制字符串（SHA-256）"""
        token = generate_task_token("some-task-id")
        assert len(token) == 64
        assert all(c in "0123456789abcdef" for c in token)

    def test_same_id_produces_different_tokens(self) -> None:
        """同一 task_id 每次生成不同的 token（因为有随机盐）"""
        t1 = generate_task_token("task-1")
        t2 = generate_task_token("task-1")
        assert t1 != t2, "同一 task_id 应产生不同 token（随机盐）"

    def test_different_ids_produce_different_tokens(self) -> None:
        """不同 task_id 产生不同 token"""
        t1 = generate_task_token("task-a")
        t2 = generate_task_token("task-b")
        assert t1 != t2


class TestCheckRateLimit:
    """测试速率限制逻辑（mock Redis）"""

    @pytest.fixture
    def redis_mock(self) -> MagicMock:
        """创建模拟的 Redis 客户端"""
        mock = MagicMock()
        # zremrangebyscore 返回移除的数量
        mock.zremrangebyscore = AsyncMock(return_value=0)
        # zcard 返回当前窗口内请求数
        mock.zcard = AsyncMock(return_value=0)
        # zadd 返回新增数量
        mock.zadd = AsyncMock(return_value=1)
        # expire 返回 True
        mock.expire = AsyncMock(return_value=True)
        return mock

    @pytest.mark.asyncio
    async def test_under_limit_allowed(self, redis_mock: MagicMock) -> None:
        """请求数未达上限时应允许"""
        redis_mock.zcard = AsyncMock(return_value=5)  # 5 次，未达 20
        allowed, remaining = await check_rate_limit("192.168.1.1", redis_mock)
        assert allowed is True
        assert remaining == 14  # 20 - 5 - 1

    @pytest.mark.asyncio
    async def test_at_limit_blocked(self, redis_mock: MagicMock) -> None:
        """请求数达到上限时应拒绝"""
        redis_mock.zcard = AsyncMock(return_value=20)
        allowed, remaining = await check_rate_limit("10.0.0.1", redis_mock)
        assert allowed is False
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_over_limit_blocked(self, redis_mock: MagicMock) -> None:
        """请求数超过上限时应拒绝"""
        redis_mock.zcard = AsyncMock(return_value=25)
        allowed, remaining = await check_rate_limit("10.0.0.2", redis_mock)
        assert allowed is False
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, redis_mock: MagicMock) -> None:
        """第一次请求应被允许且剩余 19 次"""
        redis_mock.zcard = AsyncMock(return_value=0)
        allowed, remaining = await check_rate_limit("172.16.0.1", redis_mock)
        assert allowed is True
        assert remaining == 19  # 20 - 0 - 1


# ══════════════════════════════════════════════════════════════════════
# ffmpeg / MP3 Conversion Tests
# ══════════════════════════════════════════════════════════════════════


class TestConvertToMp3:
    """测试 convert_to_mp3 函数（mock subprocess）"""

    def test_convert_calls_ffmpeg(self) -> None:
        """convert_to_mp3 应调用 ffmpeg 子进程"""
        with patch("app.services.separator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = convert_to_mp3("/tmp/input.wav", "/tmp/output.mp3")
            assert result == "/tmp/output.mp3"
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "ffmpeg"
            assert "-i" in cmd
            assert "/tmp/input.wav" in cmd
            assert "/tmp/output.mp3" in cmd

    def test_convert_default_bitrate(self) -> None:
        """默认比特率应为 320k"""
        with patch("app.services.separator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            convert_to_mp3("/t.wav", "/t.mp3")
            cmd = mock_run.call_args[0][0]
            # 查找 bitrate 参数
            b_index = cmd.index("-b:a")
            assert cmd[b_index + 1] == "320k"

    def test_convert_custom_bitrate(self) -> None:
        """自定义比特率"""
        with patch("app.services.separator.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            convert_to_mp3("/t.wav", "/t.mp3", bitrate="128k")
            cmd = mock_run.call_args[0][0]
            b_index = cmd.index("-b:a")
            assert cmd[b_index + 1] == "128k"

    def test_convert_ffmpeg_error_raises(self) -> None:
        """ffmpeg 失败时应抛出 CalledProcessError"""
        with patch("app.services.separator.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
            with pytest.raises(subprocess.CalledProcessError):
                convert_to_mp3("/t.wav", "/t.mp3")


class TestConvertStemsToMp3:
    """测试批量 WAV→MP3 转换"""

    @patch("app.services.separator.convert_to_mp3")
    def test_converts_all_stems(self, mock_convert: MagicMock) -> None:
        """应遍历所有 stem 并调用 convert_to_mp3"""
        mock_convert.return_value = "/out/stem.mp3"
        stems = {
            "vocals": "/tmp/vocals.wav",
            "drums": "/tmp/drums.wav",
            "bass": "/tmp/bass.wav",
            "other": "/tmp/other.wav",
        }
        result = convert_stems_to_mp3(stems, "/out")
        assert len(result) == 4
        assert set(result.keys()) == {"vocals", "drums", "bass", "other"}
        assert mock_convert.call_count == 4

    @patch("app.services.separator.convert_to_mp3")
    def test_empty_stems(self, mock_convert: MagicMock) -> None:
        """空 stems 应返回空 dict"""
        result = convert_stems_to_mp3({}, "/out")
        assert result == {}
        mock_convert.assert_not_called()


# ══════════════════════════════════════════════════════════════════════
# Separator Service Tests
# ══════════════════════════════════════════════════════════════════════


class TestGetSeparator:
    """测试 Demucs separator 单例获取"""

    def test_first_call_creates_instance(self) -> None:
        """首次调用应创建 DemucsSeparator 实例"""
        import app.services.separator as sep_mod

        sep_mod._separator = None
        # DemucsSeparator 现在是惰性导入，mock 必须在 app.ai.demucs 源头
        with patch("app.ai.demucs.DemucsSeparator") as MockDemucs:
            mock_instance = MagicMock()
            MockDemucs.return_value = mock_instance
            result = get_separator()
            MockDemucs.assert_called_once()
            assert result is mock_instance

    def test_second_call_reuses_instance(self) -> None:
        """再次调用应复用已有实例"""
        import app.services.separator as sep_mod

        sep_mod._separator = None
        with patch("app.ai.demucs.DemucsSeparator") as MockDemucs:
            mock_instance = MagicMock()
            MockDemucs.return_value = mock_instance
            first = get_separator()
            second = get_separator()
            assert first is second
            MockDemucs.assert_called_once()


# ══════════════════════════════════════════════════════════════════════
# Cleaner Service Tests
# ══════════════════════════════════════════════════════════════════════


class TestGetTotalUploadSize:
    """测试磁盘用量统计"""

    @patch("app.services.cleaner.os.path.exists", return_value=False)
    def test_no_upload_dir_returns_zero(self, _mock_exists: MagicMock) -> None:
        """上传目录不存在时返回 0"""
        import asyncio
        from app.services.cleaner import get_total_upload_size

        result = asyncio.run(get_total_upload_size())
        assert result == 0

    @patch("app.services.cleaner.os.path.exists", return_value=True)
    @patch("app.services.cleaner.os.walk")
    def test_with_files(self, mock_walk: MagicMock, _mock_exists: MagicMock) -> None:
        """有文件时应正确统计大小"""
        import asyncio
        from app.services.cleaner import get_total_upload_size

        mock_walk.return_value = [
            ("/uploads", [], ["file1.mp3", "file2.wav"]),
            ("/uploads/sub", [], ["file3.mp3"]),
        ]

        def mock_getsize(fp: str) -> int:
            # Use os.path.basename for cross-platform path handling
            name = os.path.basename(fp)
            return {"file1.mp3": 1000, "file2.wav": 2000, "file3.mp3": 500}[name]

        with patch("os.path.getsize", side_effect=mock_getsize):
            with patch("os.path.exists", return_value=True):
                result = asyncio.run(get_total_upload_size())
                assert result == 3500
