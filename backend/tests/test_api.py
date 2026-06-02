"""Integration tests for the FastAPI backend.

Run with: pytest tests/ -v
Requires PostgreSQL and Redis services to be running (docker-compose up db redis).
"""

from __future__ import annotations

import io
import os

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
