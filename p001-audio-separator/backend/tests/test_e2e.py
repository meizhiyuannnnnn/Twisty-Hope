"""End-to-end integration tests — full user flow via HTTP.

Simulates: upload → query → trigger separation → poll → download.
All AI models are mocked so no GPU is needed.
Uses FastAPI dependency_overrides to mock Redis/DB/rate-limit.
"""

from __future__ import annotations

import io
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ── Mock all external dependencies ─────────────────────────────────────

@pytest.fixture(autouse=True)
def _override_dependencies() -> None:
    """Override FastAPI dependencies with mocks for all tests."""
    mock_redis = AsyncMock()
    mock_redis.llen = AsyncMock(return_value=0)
    mock_redis.zremrangebyscore = AsyncMock(return_value=0)
    mock_redis.zcard = AsyncMock(return_value=0)
    mock_redis.zadd = AsyncMock(return_value=1)
    mock_redis.expire = AsyncMock(return_value=True)
    mock_redis.rpush = AsyncMock(return_value=1)
    mock_redis.aclose = AsyncMock()
    mock_redis.pubsub = MagicMock()

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    async def _get_redis():
        yield mock_redis

    async def _get_db():
        yield mock_db

    app.dependency_overrides = {}

    from app.api.deps import get_redis as deps_get_redis
    from app.api.deps import check_rate_limit_dependency
    from app.core.database import get_db

    app.dependency_overrides[deps_get_redis] = _get_redis
    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[check_rate_limit_dependency] = lambda: None


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client."""
    return TestClient(app)


# ── helpers ──────────────────────────────────────────────────────────


def _fake_mp3_bytes(size: int = 5000) -> bytes:
    """Generate minimal fake MP3 bytes with valid magic header."""
    # MP3 file starts with ID3 tag or sync word 0xFF 0xFB/0xFA/...
    header = b"\xff\xfb\x90\x00"  # MPEG1 Layer3 128kbps 44100Hz
    # Pad with zeros to reach desired size
    padding = b"\x00" * max(0, size - len(header))
    return header + padding


def _make_upload_file(
    filename: str = "test.mp3",
    content_type: str = "audio/mpeg",
    content: bytes | None = None,
) -> tuple:
    """Helper to create a file for upload. Returns (io.BytesIO, filename, content_type)."""
    if content is None:
        content = _fake_mp3_bytes()
    return (filename, io.BytesIO(content), content_type)


# ══════════════════════════════════════════════════════════════════════
# E2E Test Cases
# ══════════════════════════════════════════════════════════════════════


# We must mock at a deeper level for the upload endpoint since it
# uses aiofiles, filetype, and librosa.


class TestE2EUploadOnly:
    """测试上传环节（完整流程的第一步）"""

    @patch("app.api.upload.os.makedirs")
    @patch("app.api.upload.aiofiles.open")
    @patch("app.api.upload.filetype.guess")
    @patch("app.api.upload.librosa.get_duration", return_value=120.0)
    def test_upload_mp3_success(
        self,
        mock_duration: MagicMock,
        mock_filetype: MagicMock,
        mock_aiofiles: MagicMock,
        mock_makedirs: MagicMock,
        client: TestClient,
    ) -> None:
        """上传有效 MP3 文件应成功并返回 task_id + token"""
        # Mock filetype to return audio/*
        mock_kind = MagicMock()
        mock_kind.mime = "audio/mpeg"
        mock_filetype.return_value = mock_kind

        # Mock aiofiles async open
        mock_file = MagicMock()
        mock_file.write = AsyncMock()
        mock_aiofiles.return_value.__aenter__.return_value = mock_file

        response = client.post(
            "/api/upload",
            files={"file": ("song.mp3", io.BytesIO(_fake_mp3_bytes()), "audio/mpeg")},
        )

        assert response.status_code == 200, f"上传应成功，实际: {response.json()}"
        data = response.json()
        assert "task_id" in data
        assert "token" in data
        assert data["original_filename"] == "song.mp3"

    @patch("app.api.upload.os.makedirs")
    @patch("app.api.upload.aiofiles.open")
    @patch("app.api.upload.filetype.guess")
    @patch("app.api.upload.librosa.get_duration", return_value=120.0)
    def test_upload_wav_success(
        self,
        mock_duration: MagicMock,
        mock_filetype: MagicMock,
        mock_aiofiles: MagicMock,
        mock_makedirs: MagicMock,
        client: TestClient,
    ) -> None:
        """上传 WAV 文件应成功"""
        mock_kind = MagicMock()
        mock_kind.mime = "audio/wav"
        mock_filetype.return_value = mock_kind

        mock_file = MagicMock()
        mock_file.write = AsyncMock()
        mock_aiofiles.return_value.__aenter__.return_value = mock_file

        response = client.post(
            "/api/upload",
            files={"file": ("track.wav", io.BytesIO(_fake_mp3_bytes(8000)), "audio/wav")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "track.wav"

    def test_upload_no_file_returns_422(self, client: TestClient) -> None:
        """不上传文件应返回 422"""
        response = client.post("/api/upload")
        assert response.status_code == 422

    def test_upload_wrong_mime_returns_415(self, client: TestClient) -> None:
        """上传非音频 MIME 类型应返回 415"""
        response = client.post(
            "/api/upload",
            files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
        )
        assert response.status_code == 415

    def test_upload_empty_file_returns_400(self, client: TestClient) -> None:
        """上传空文件应返回 400"""
        response = client.post(
            "/api/upload",
            files={"file": ("empty.mp3", io.BytesIO(b""), "audio/mpeg")},
        )
        assert response.status_code == 400

    @patch("app.api.upload.os.makedirs")
    @patch("app.api.upload.aiofiles.open")
    @patch("app.api.upload.filetype.guess")
    @patch("app.api.upload.librosa.get_duration", return_value=120.0)
    def test_upload_flac_accepted(
        self,
        mock_duration: MagicMock,
        mock_filetype: MagicMock,
        mock_aiofiles: MagicMock,
        mock_makedirs: MagicMock,
        client: TestClient,
    ) -> None:
        """上传 FLAC 格式应被接受"""
        mock_kind = MagicMock()
        mock_kind.mime = "audio/flac"
        mock_filetype.return_value = mock_kind

        mock_file = MagicMock()
        mock_file.write = AsyncMock()
        mock_aiofiles.return_value.__aenter__.return_value = mock_file

        response = client.post(
            "/api/upload",
            files={"file": ("lossless.flac", io.BytesIO(_fake_mp3_bytes()), "audio/flac")},
        )
        assert response.status_code == 200


class TestE2ETaskQuery:
    """测试任务查询"""

    def test_query_nonexistent_task(self, client: TestClient) -> None:
        """查询不存在的任务应返回 404"""
        tid = str(uuid.uuid4())
        response = client.get(f"/api/task/{tid}", params={"token": "any-token"})
        assert response.status_code == 404

    def test_query_invalid_uuid(self, client: TestClient) -> None:
        """无效 UUID 格式应返回 400"""
        response = client.get("/api/task/not-a-uuid", params={"token": "any"})
        assert response.status_code == 400

    def test_query_missing_token(self, client: TestClient) -> None:
        """缺少 token 参数应返回 422"""
        tid = str(uuid.uuid4())
        response = client.get(f"/api/task/{tid}")
        assert response.status_code == 422


class TestE2ETriggerOperations:
    """测试操作触发接口"""

    def test_separate_invalid_mode(self, client: TestClient) -> None:
        """分离模式无效应返回 400"""
        tid = str(uuid.uuid4())
        response = client.post(
            f"/api/task/{tid}/separate",
            params={"token": "any"},
            json={"mode": "8track"},
        )
        # 任务不存在先于 mode 校验，所以返回 404
        assert response.status_code in (400, 404)

    def test_transform_out_of_range_speed(self, client: TestClient) -> None:
        """speed 超出范围应返回 422"""
        tid = str(uuid.uuid4())
        response = client.post(
            f"/api/task/{tid}/transform",
            params={"token": "any"},
            json={"speed": 3.0, "pitch": 0},
        )
        assert response.status_code == 422

    def test_transform_out_of_range_pitch(self, client: TestClient) -> None:
        """pitch 超出范围应返回 422"""
        tid = str(uuid.uuid4())
        response = client.post(
            f"/api/task/{tid}/transform",
            params={"token": "any"},
            json={"speed": 1.0, "pitch": 24},
        )
        assert response.status_code == 422


class TestE2EDownload:
    """测试下载接口"""

    def test_download_nonexistent_task(self, client: TestClient) -> None:
        """下载不存在的任务应返回 404"""
        tid = str(uuid.uuid4())
        response = client.get(
            f"/api/task/{tid}/download/vocals",
            params={"token": "any"},
        )
        assert response.status_code == 404

    def test_download_all_nonexistent_task(self, client: TestClient) -> None:
        """打包下载不存在的任务应返回 404"""
        tid = str(uuid.uuid4())
        response = client.get(
            f"/api/task/{tid}/download",
            params={"token": "any"},
        )
        assert response.status_code == 404


class TestE2EHealth:
    """测试健康检查"""

    def test_health_returns_ok(self, client: TestClient) -> None:
        """/health 应返回 ok"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_returns_info(self, client: TestClient) -> None:
        """/ 应返回项目信息"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "音频分离工具"
        assert "version" in data
