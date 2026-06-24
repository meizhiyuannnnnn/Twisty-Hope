"""Integration tests for the FastAPI backend.

Run with: pytest tests/ -v
Uses FastAPI dependency_overrides to mock Redis, DB, and rate limiting.
No external services required.
"""

from __future__ import annotations

import io
import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


# ── Mock dependencies ──────────────────────────────────────────────────

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
    # rate limit check passes silently when Redis mock returns under-limit
    app.dependency_overrides[check_rate_limit_dependency] = lambda: None


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    """Tests for /health and / endpoints."""

    def test_health_returns_ok(self, client: TestClient) -> None:
        """Health endpoint should return status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "queue_length" in data

    def test_root_returns_info(self, client: TestClient) -> None:
        """Root endpoint should return app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "音频分离工具"
        assert "version" in data
        assert data["docs"] == "/docs"


class TestUploadValidation:
    """Tests for file upload validation logic."""

    def test_upload_no_file(self, client: TestClient) -> None:
        """Upload without file should return 422."""
        response = client.post("/api/upload")
        assert response.status_code == 422

    def test_upload_empty_file(self, client: TestClient) -> None:
        """Upload empty file should return 400."""
        fake_file = io.BytesIO(b"")
        response = client.post(
            "/api/upload",
            files={"file": ("test.mp3", fake_file, "audio/mpeg")},
        )
        assert response.status_code == 400

    def test_upload_wrong_mime(self, client: TestClient) -> None:
        """Upload with wrong MIME type should return 415."""
        fake_content = b"not audio data" * 100
        fake_file = io.BytesIO(fake_content)
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", fake_file, "text/plain")},
        )
        assert response.status_code == 415

    def test_upload_invalid_audio(self, client: TestClient) -> None:
        """Upload non-audio data claiming to be MP3 should be rejected."""
        fake_content = b"this is not real audio" * 1000
        fake_file = io.BytesIO(fake_content)
        response = client.post(
            "/api/upload",
            files={"file": ("fake.mp3", fake_file, "audio/mpeg")},
        )
        # Should be rejected by magic bytes check
        assert response.status_code in (415, 500)


class TestTaskEndpoints:
    """Tests for task query endpoints."""

    def test_get_nonexistent_task(self, client: TestClient) -> None:
        """Querying a non-existent task should return 404."""
        response = client.get(
            "/api/task/00000000-0000-0000-0000-000000000000",
            params={"token": "invalid"},
        )
        assert response.status_code == 404

    def test_get_task_invalid_uuid(self, client: TestClient) -> None:
        """Querying with invalid UUID should return 400."""
        response = client.get(
            "/api/task/not-a-uuid",
            params={"token": "any"},
        )
        assert response.status_code == 400

    def test_get_task_missing_token(self, client: TestClient) -> None:
        """Querying without token should return 422."""
        response = client.get("/api/task/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 422


class TestTaskTriggerEndpoints:
    """Tests for task operation trigger endpoints."""

    def test_separate_invalid_mode(self, client: TestClient) -> None:
        """Trigger separation with invalid mode should return 400."""
        response = client.post(
            "/api/task/00000000-0000-0000-0000-000000000000/separate",
            params={"token": "any"},
            json={"mode": "5track"},
        )
        assert response.status_code == 400

    def test_transform_invalid_pitch(self, client: TestClient) -> None:
        """Transform with out-of-range pitch should return 422."""
        response = client.post(
            "/api/task/00000000-0000-0000-0000-000000000000/transform",
            params={"token": "any"},
            json={"speed": 1.0, "pitch": 24},
        )
        assert response.status_code == 422

    def test_transform_invalid_speed(self, client: TestClient) -> None:
        """Transform with out-of-range speed should return 422."""
        response = client.post(
            "/api/task/00000000-0000-0000-0000-000000000000/transform",
            params={"token": "any"},
            json={"speed": 3.0, "pitch": 0},
        )
        assert response.status_code == 422


class TestDownloadEndpoints:
    """Tests for download endpoints."""

    def test_download_nonexistent_task(self, client: TestClient) -> None:
        """Download from non-existent task should return 404."""
        response = client.get(
            "/api/task/00000000-0000-0000-0000-000000000000/download/vocals",
            params={"token": "any"},
        )
        assert response.status_code == 404

    def test_download_invalid_stem(self, client: TestClient) -> None:
        """Download request with missing stem should trigger 404."""
        # This test is for a non-existent task, so 404 is correct
        response = client.get(
            "/api/task/00000000-0000-0000-0000-000000000000/download/nonexistent",
            params={"token": "any"},
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# WebSocket helper tests (_build_stems / _enrich_message)
# ═══════════════════════════════════════════════════════════════════════════


class TestBuildStems:
    """Tests for _build_stems helper in websocket.py."""

    def test_builds_stems_from_result_paths(self) -> None:
        """Should build stems array with download URLs from result_paths dict."""
        from unittest.mock import MagicMock

        from app.api.websocket import _build_stems

        task = MagicMock()
        task.id = "test-id-1234"
        task.result_paths = {"vocals": "/tmp/vocals.wav", "drums": "/tmp/drums.wav"}

        stems = _build_stems(task, "secret-token")
        assert len(stems) == 2
        assert stems[0]["stem_id"] == "vocals"
        assert stems[0]["label"] == "人声"
        assert "/download/vocals?token=secret-token" in stems[0]["url"]

        assert stems[1]["stem_id"] == "drums"
        assert stems[1]["label"] == "鼓"

    def test_empty_result_paths_returns_empty_list(self) -> None:
        """Should return empty list when result_paths is None or empty."""
        from unittest.mock import MagicMock

        from app.api.websocket import _build_stems

        task = MagicMock()
        task.result_paths = None
        assert _build_stems(task, "token") == []

        task.result_paths = {}
        assert _build_stems(task, "token") == []

    def test_unknown_stem_name_uses_raw_name_as_label(self) -> None:
        """Should fall back to raw stem name when no Chinese label exists."""
        from unittest.mock import MagicMock

        from app.api.websocket import _build_stems

        task = MagicMock()
        task.id = "xyz"
        task.result_paths = {"guitar": "/tmp/guitar.wav"}

        stems = _build_stems(task, "tok")
        assert stems[0]["label"] == "guitar"

    def test_url_includes_task_id_and_token(self) -> None:
        """Download URL should contain task ID, stem name, and token."""
        from unittest.mock import MagicMock

        from app.api.websocket import _build_stems

        task = MagicMock()
        task.id = "abc-def-123"
        task.result_paths = {"bass": "/tmp/bass.wav"}

        stems = _build_stems(task, "my-token-456")
        expected_url = "/api/task/abc-def-123/download/bass?token=my-token-456"
        assert stems[0]["url"] == expected_url


class TestEnrichMessage:
    """Tests for _enrich_message helper in websocket.py."""

    @pytest.mark.asyncio
    async def test_non_completed_status_passes_through(self) -> None:
        """Messages with status != 'completed' should be returned unchanged."""
        from app.api.websocket import _enrich_message

        data = {"status": "processing", "progress": 50}
        result = await _enrich_message(data, "any-task", "any-token")
        assert result == data
        assert "stems" not in result

    @pytest.mark.asyncio
    async def test_pending_status_passes_through(self) -> None:
        """Pending status should also pass through without enrichment."""
        from app.api.websocket import _enrich_message

        data = {"status": "pending", "progress": 0}
        result = await _enrich_message(data, "any-task", "any-token")
        assert result == data

    @pytest.mark.asyncio
    async def test_failed_status_passes_through(self) -> None:
        """Failed status should pass through without enrichment."""
        from app.api.websocket import _enrich_message

        data = {"status": "failed", "progress": 0, "error": "something went wrong"}
        result = await _enrich_message(data, "any-task", "any-token")
        assert result == data

    @pytest.mark.asyncio
    async def test_completed_but_no_result_paths(self) -> None:
        """Completed task without result_paths should not add stems."""
        import uuid
        from unittest.mock import AsyncMock, MagicMock, patch

        task = MagicMock()
        task.id = uuid.uuid4()
        task.result_paths = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=task)

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)

        with patch("app.api.websocket.async_session_factory", mock_session_factory):
            from app.api.websocket import _enrich_message

            data = {"status": "completed", "progress": 100}
            result = await _enrich_message(data, str(task.id), "tok")
            assert "stems" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
