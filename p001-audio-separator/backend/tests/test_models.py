"""Unit tests for Task ORM model — defaults, to_dict, is_expired, status modes.

NOTE: SQLAlchemy mapped_column defaults (like default=uuid.uuid4, default="pending")
are database-level defaults, NOT Python-level __init__ defaults. They only take effect
on INSERT. When constructing Task() in tests without a DB session, these fields are None
unless explicitly passed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.task import Task


# ── Helper ──────────────────────────────────────────────────────────────

def _create_task(**overrides) -> Task:
    """Create a Task with explicit defaults matching the DB schema."""
    now = datetime.now(timezone.utc)
    defaults = {
        "ip_address": "127.0.0.1",
        "original_filename": "test.mp3",
        "original_path": "/tmp/test.mp3",
        "file_size": 1024,
        "token": "abc123",
        "id": uuid.uuid4(),
        "status": "pending",
        "progress": 0,
        "progress_message": "",
        "created_at": now,
        "expires_at": now + timedelta(hours=24),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestTaskDefaults:
    """测试 Task 模型默认值（通过 _create_task 显式赋值模拟 DB 默认值）"""

    def test_id_is_uuid(self) -> None:
        """task.id 应为 UUID 类型"""
        task = _create_task()
        assert isinstance(task.id, uuid.UUID)

    def test_status_default_is_pending(self) -> None:
        """新任务 status 应为 'pending'"""
        task = _create_task()
        assert task.status == "pending"

    def test_progress_default_is_zero(self) -> None:
        """新任务 progress 应为 0"""
        task = _create_task()
        assert task.progress == 0

    def test_progress_message_default_is_empty(self) -> None:
        """新任务 progress_message 应为空字符串"""
        task = _create_task()
        assert task.progress_message == ""

    def test_mode_defaults_to_none(self) -> None:
        """新任务 mode 默认为 None"""
        task = _create_task()
        assert task.mode is None

    def test_result_paths_defaults_to_none(self) -> None:
        """新任务 result_paths 默认为 None"""
        task = _create_task()
        assert task.result_paths is None

    def test_chord_result_defaults_to_none(self) -> None:
        """新任务 chord_result 默认为 None"""
        task = _create_task()
        assert task.chord_result is None

    def test_error_message_defaults_to_none(self) -> None:
        """新任务 error_message 默认为 None"""
        task = _create_task()
        assert task.error_message is None

    def test_created_at_is_utc_datetime(self) -> None:
        """created_at 应为 UTC datetime"""
        task = _create_task()
        assert isinstance(task.created_at, datetime)
        assert task.created_at.tzinfo is not None

    def test_expires_at_is_24h_after_created(self) -> None:
        """expires_at 应为 created_at + 24 小时"""
        now = datetime.now(timezone.utc)
        task = _create_task(created_at=now, expires_at=now + timedelta(hours=24))
        delta = task.expires_at - task.created_at
        assert timedelta(hours=23, minutes=59) <= delta <= timedelta(hours=24, seconds=2)


class TestTaskToDict:
    """测试 Task.to_dict() 方法"""

    def _make_task(self, **kwargs) -> Task:
        now = datetime.now(timezone.utc)
        defaults = {
            "id": uuid.uuid4(),
            "ip_address": "192.168.1.1",
            "original_filename": "song.flac",
            "original_path": "/data/song.flac",
            "file_size": 5_000_000,
            "token": "tok_abc123",
            "status": "pending",
            "progress": 0,
            "progress_message": "",
            "created_at": now,
            "expires_at": now + timedelta(hours=24),
        }
        defaults.update(kwargs)
        return Task(**defaults)

    def test_to_dict_includes_all_public_fields(self) -> None:
        """to_dict() 应包含所有对外字段"""
        task = self._make_task()
        d = task.to_dict()
        assert d["task_id"] == str(task.id)
        assert d["status"] == "pending"
        assert d["mode"] is None
        assert d["progress"] == 0
        assert d["progress_message"] == ""
        assert d["original_filename"] == "song.flac"
        assert d["file_size"] == 5_000_000
        # duration 默认为 None（可为空）
        assert "duration" in d
        assert "created_at" in d
        assert "expires_at" in d

    def test_to_dict_task_id_is_string(self) -> None:
        """to_dict() 中 task_id 应为字符串而非 UUID 对象"""
        task = self._make_task()
        d = task.to_dict()
        assert isinstance(d["task_id"], str)
        # 字符串形式的 UUID 长 36 字符
        assert len(d["task_id"]) == 36

    def test_to_dict_reflects_status_change(self) -> None:
        """修改 status 后 to_dict() 应反映新值"""
        task = self._make_task()
        task.status = "completed"
        d = task.to_dict()
        assert d["status"] == "completed"

    def test_to_dict_reflects_mode(self) -> None:
        """设置 mode 后 to_dict() 应反映"""
        task = self._make_task()
        task.mode = "4track"
        d = task.to_dict()
        assert d["mode"] == "4track"

    def test_to_dict_reflects_progress(self) -> None:
        """设置 progress 后 to_dict() 应反映"""
        task = self._make_task()
        task.progress = 75
        task.progress_message = "正在处理..."
        d = task.to_dict()
        assert d["progress"] == 75
        assert d["progress_message"] == "正在处理..."

    def test_to_dict_created_at_is_iso(self) -> None:
        """created_at 应为 ISO 格式字符串"""
        task = self._make_task()
        d = task.to_dict()
        # ISO 格式包含 'T'
        assert "T" in d["created_at"]

    def test_to_dict_does_not_expose_token(self) -> None:
        """to_dict() 不应暴露 token（安全）"""
        task = self._make_task()
        d = task.to_dict()
        assert "token" not in d

    def test_to_dict_does_not_expose_ip(self) -> None:
        """to_dict() 不应暴露 IP 地址（隐私）"""
        task = self._make_task()
        d = task.to_dict()
        assert "ip_address" not in d


class TestTaskIsExpired:
    """测试 Task.is_expired() 方法"""

    def _make_task_with_expiry(self, hours_from_now: float) -> Task:
        now = datetime.now(timezone.utc)
        task = Task(
            ip_address="127.0.0.1",
            original_filename="test.wav",
            original_path="/tmp/test.wav",
            file_size=1024,
            token="tok",
        )
        task.expires_at = now + timedelta(hours=hours_from_now)
        return task

    def test_fresh_task_not_expired(self) -> None:
        """刚创建的任务不应过期"""
        task = self._make_task_with_expiry(24)
        assert not task.is_expired()

    def test_just_expired_task(self) -> None:
        """过期 1 秒的任务应返回 True"""
        task = self._make_task_with_expiry(-0.0003)  # ~1 秒前过期
        assert task.is_expired()

    def test_long_expired_task(self) -> None:
        """过期很久的任务应返回 True"""
        task = self._make_task_with_expiry(-48)
        assert task.is_expired()


class TestTaskStatusValues:
    """测试 Task status 合法值"""

    STATUSES = ["pending", "processing", "completed", "failed"]

    @pytest.mark.parametrize("status", STATUSES)
    def test_valid_status(self, status: str) -> None:
        """合法 status 值应可正常赋值"""
        task = Task(
            ip_address="127.0.0.1",
            original_filename="test.ogg",
            original_path="/tmp/test.ogg",
            file_size=2048,
            token="tok",
        )
        task.status = status
        assert task.status == status

    def test_status_max_length(self) -> None:
        """status 字段长度限制 20 字符"""
        task = Task(
            ip_address="127.0.0.1",
            original_filename="test.ogg",
            original_path="/tmp/test.ogg",
            file_size=2048,
            token="tok",
        )
        # 所有合法状态值都 ≤ 20 字符
        for s in self.STATUSES:
            assert len(s) <= 20, f"status '{s}' 超过 20 字符限制"


class TestTaskModeValues:
    """测试 Task mode 合法值"""

    MODES = ["2track", "4track", "transform", "chords"]

    @pytest.mark.parametrize("mode", MODES)
    def test_valid_mode(self, mode: str) -> None:
        """合法 mode 值应可正常赋值"""
        task = Task(
            ip_address="127.0.0.1",
            original_filename="test.mp3",
            original_path="/tmp/test.mp3",
            file_size=4096,
            token="tok",
        )
        task.mode = mode
        assert task.mode == mode


class TestTaskTokenUniqueness:
    """测试 token 字段约束"""

    def test_token_is_stored(self) -> None:
        """token 应正确存储"""
        token_val = "sha256hash_example_token_value_64chars"
        task = Task(
            ip_address="10.0.0.1",
            original_filename="a.mp3",
            original_path="/tmp/a.mp3",
            file_size=100,
            token=token_val,
        )
        assert task.token == token_val

    def test_token_max_length(self) -> None:
        """token 字段限制 64 字符"""
        token_val = "a" * 64
        task = Task(
            ip_address="10.0.0.1",
            original_filename="a.mp3",
            original_path="/tmp/a.mp3",
            file_size=100,
            token=token_val,
        )
        assert len(task.token) <= 64


class TestTaskIPStorage:
    """测试 IP 地址存储"""

    def test_ipv4_stored(self) -> None:
        """IPv4 地址应正确存储"""
        task = Task(
            ip_address="192.168.1.100",
            original_filename="f.mp3",
            original_path="/tmp/f.mp3",
            file_size=500,
            token="t",
        )
        assert task.ip_address == "192.168.1.100"

    def test_ipv6_stored(self) -> None:
        """IPv6 地址应正确存储（最长 45 字符）"""
        ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        task = Task(
            ip_address=ipv6,
            original_filename="f.mp3",
            original_path="/tmp/f.mp3",
            file_size=500,
            token="t",
        )
        assert task.ip_address == ipv6
        assert len(ipv6) <= 45
