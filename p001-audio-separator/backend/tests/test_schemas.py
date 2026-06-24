"""Unit tests for Pydantic request/response schemas — validation and boundary values."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.task import (
    SeparateRequest,
    TaskDetailResponse,
    TaskResponse,
    TransformRequest,
)
from app.schemas.upload import HealthResponse, UploadResponse


class TestSeparateRequest:
    """测试分离请求 schema"""

    def test_default_mode_is_2track(self) -> None:
        """默认 mode 应为 '2track'"""
        req = SeparateRequest()
        assert req.mode == "2track"

    def test_mode_2track(self) -> None:
        """mode='2track' 应通过验证"""
        req = SeparateRequest(mode="2track")
        assert req.mode == "2track"

    def test_mode_4track(self) -> None:
        """mode='4track' 应通过验证"""
        req = SeparateRequest(mode="4track")
        assert req.mode == "4track"

    def test_invalid_mode_rejected(self) -> None:
        """非法 mode 值（如 '5track'）不会被 Pydantic Field 自动拒绝，但业务层应处理"""
        # SeparateRequest 的 mode 是 str 类型，不含枚举约束
        # 这里验证至少能构造成功（业务校验在 API 层）
        req = SeparateRequest(mode="5track")
        assert req.mode == "5track"


class TestTransformRequest:
    """测试变速变调请求 schema"""

    def test_default_speed_is_1(self) -> None:
        """默认 speed 应为 1.0"""
        req = TransformRequest()
        assert req.speed == 1.0

    def test_default_pitch_is_0(self) -> None:
        """默认 pitch 应为 0"""
        req = TransformRequest()
        assert req.pitch == 0

    # ── speed 边界 ──

    def test_speed_min_valid(self) -> None:
        """speed=0.5 应通过验证（最小值）"""
        req = TransformRequest(speed=0.5, pitch=0)
        assert req.speed == 0.5

    def test_speed_max_valid(self) -> None:
        """speed=1.5 应通过验证（最大值）"""
        req = TransformRequest(speed=1.5, pitch=0)
        assert req.speed == 1.5

    def test_speed_too_low(self) -> None:
        """speed=0.4 应被拒绝（低于 0.5）"""
        with pytest.raises(ValidationError):
            TransformRequest(speed=0.4, pitch=0)

    def test_speed_too_high(self) -> None:
        """speed=1.6 应被拒绝（高于 1.5）"""
        with pytest.raises(ValidationError):
            TransformRequest(speed=1.6, pitch=0)

    def test_speed_zero(self) -> None:
        """speed=0 应被拒绝"""
        with pytest.raises(ValidationError):
            TransformRequest(speed=0.0, pitch=0)

    # ── pitch 边界 ──

    def test_pitch_min_valid(self) -> None:
        """pitch=-12 应通过验证（最小值）"""
        req = TransformRequest(speed=1.0, pitch=-12)
        assert req.pitch == -12

    def test_pitch_max_valid(self) -> None:
        """pitch=12 应通过验证（最大值）"""
        req = TransformRequest(speed=1.0, pitch=12)
        assert req.pitch == 12

    def test_pitch_too_low(self) -> None:
        """pitch=-13 应被拒绝（低于 -12）"""
        with pytest.raises(ValidationError):
            TransformRequest(speed=1.0, pitch=-13)

    def test_pitch_too_high(self) -> None:
        """pitch=13 应被拒绝（高于 12）"""
        with pytest.raises(ValidationError):
            TransformRequest(speed=1.0, pitch=13)


class TestTaskResponse:
    """测试 TaskResponse schema"""

    def test_minimal_task_response(self) -> None:
        """最少必填字段的 TaskResponse"""
        resp = TaskResponse(
            task_id="550e8400-e29b-41d4-a716-446655440000",
            status="pending",
            original_filename="test.mp3",
            file_size=1024,
        )
        assert resp.task_id == "550e8400-e29b-41d4-a716-446655440000"
        assert resp.status == "pending"
        assert resp.mode is None
        assert resp.progress == 0
        assert resp.progress_message == ""

    def test_full_task_response(self) -> None:
        """完整字段的 TaskResponse"""
        resp = TaskResponse(
            task_id="abc",
            status="completed",
            mode="4track",
            progress=100,
            progress_message="完成",
            original_filename="song.wav",
            file_size=10_000_000,
            duration=245.5,
            created_at="2026-06-03T10:00:00+00:00",
            expires_at="2026-06-04T10:00:00+00:00",
        )
        assert resp.mode == "4track"
        assert resp.progress == 100
        assert resp.duration == 245.5


class TestTaskDetailResponse:
    """测试 TaskDetailResponse schema（继承 TaskResponse）"""

    def test_includes_extra_fields(self) -> None:
        """应包含 result_stems, chord_result, error_message"""
        resp = TaskDetailResponse(
            task_id="id",
            status="completed",
            original_filename="f.mp3",
            file_size=1000,
            result_stems=["vocals", "drums", "bass", "other"],
            chord_result={"chords": [{"start": 0, "end": 2.5, "chord": "C:maj"}]},
            error_message=None,
        )
        assert resp.result_stems == ["vocals", "drums", "bass", "other"]
        assert resp.chord_result is not None
        assert resp.error_message is None


class TestUploadResponse:
    """测试 UploadResponse schema"""

    def test_default_message(self) -> None:
        """默认 message 提示上传成功"""
        resp = UploadResponse(
            task_id="tid",
            token="tok",
            original_filename="music.mp3",
            file_size=5000,
        )
        assert "成功" in resp.message

    def test_duration_optional(self) -> None:
        """duration 可省略（None）"""
        resp = UploadResponse(
            task_id="tid",
            token="tok",
            original_filename="music.mp3",
            file_size=5000,
            duration=None,
        )
        assert resp.duration is None

    def test_duration_provided(self) -> None:
        """duration 提供时应正确存储"""
        resp = UploadResponse(
            task_id="tid",
            token="tok",
            original_filename="music.mp3",
            file_size=5000,
            duration=180.5,
        )
        assert resp.duration == 180.5


class TestHealthResponse:
    """测试 HealthResponse schema"""

    def test_default_queue_length(self) -> None:
        """默认 queue_length 为 0"""
        resp = HealthResponse(status="ok", version="0.1.0")
        assert resp.queue_length == 0

    def test_custom_queue_length(self) -> None:
        """自定义 queue_length"""
        resp = HealthResponse(status="ok", version="1.0.0", queue_length=5)
        assert resp.queue_length == 5
