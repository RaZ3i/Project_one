"""Tests for SPA static file cache-control headers."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import BUILD_ID, IMMUTABLE_ASSET_HEADERS, NO_CACHE_HEADERS, create_app


class StaticCacheHeaderTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.static_dir = Path(self.temp_dir.name)
        (self.static_dir / "assets").mkdir()
        (self.static_dir / "index.html").write_text(
            "<html><head></head><body>app</body></html>",
            encoding="utf-8",
        )
        (self.static_dir / "assets" / "app-abc123.js").write_text("console.log(1)", encoding="utf-8")

        patcher = patch("app.main.STATIC_DIR", self.static_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.client = TestClient(create_app())

    def assert_no_cache_headers(self, response):
        for key, value in NO_CACHE_HEADERS.items():
            self.assertEqual(response.headers.get(key), value)

    def test_root_returns_no_cache_headers(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assert_no_cache_headers(response)

    def test_spa_route_returns_no_cache_headers(self):
        response = self.client.get("/tutors")
        self.assertEqual(response.status_code, 200)
        self.assert_no_cache_headers(response)

    def test_index_html_returns_no_cache_headers(self):
        response = self.client.get("/index.html")
        self.assertEqual(response.status_code, 200)
        self.assert_no_cache_headers(response)

    def test_index_html_includes_build_id_meta(self):
        response = self.client.get("/")
        self.assertIn(f'name="build-id" content="{BUILD_ID}"', response.text)

    def test_hashed_assets_return_immutable_cache_headers(self):
        response = self.client.get("/assets/app-abc123.js")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Cache-Control"),
            IMMUTABLE_ASSET_HEADERS["Cache-Control"],
        )


class BuildInfoTests(unittest.TestCase):
    def test_build_info_endpoint(self):
        client = TestClient(create_app())
        response = client.get("/api/build-info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["build_id"], BUILD_ID)
        self.assertEqual(data["status"], "ok")


if __name__ == "__main__":
    unittest.main()
