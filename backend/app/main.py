import os
import re
from pathlib import Path
from typing import ClassVar

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope

from app.api.routes import auth, health, lessons, reviews, slots, subjects, tutors, users
from app.core.config import get_settings

settings = get_settings()

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subjects.router)
api_router.include_router(tutors.router)
api_router.include_router(reviews.router)
api_router.include_router(slots.router)
api_router.include_router(lessons.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
BUILD_ID = os.getenv("BUILD_ID") or os.getenv("RAILWAY_GIT_COMMIT_SHA") or "dev"

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "CDN-Cache-Control": "no-store",
    "Surrogate-Control": "no-store",
    "Pragma": "no-cache",
    "Expires": "0",
    "Vary": "Accept-Encoding",
}
IMMUTABLE_ASSET_HEADERS = {"Cache-Control": "public, max-age=31536000, immutable"}

_BUILD_ID_META_RE = re.compile(r'<meta name="build-id" content="[^"]*"\s*/?>', re.IGNORECASE)


class CachedStaticFiles(StaticFiles):
    """StaticFiles with long-lived cache for content-hashed build assets."""

    cache_control: ClassVar[str] = IMMUTABLE_ASSET_HEADERS["Cache-Control"]

    def file_response(
        self,
        full_path,
        stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = self.cache_control
        return response


def inject_build_id(html: str) -> str:
    """Ensure index.html carries the deploy build id for debugging and CDN busting."""
    meta = f'<meta name="build-id" content="{BUILD_ID}" />'
    if _BUILD_ID_META_RE.search(html):
        return _BUILD_ID_META_RE.sub(meta, html, count=1)
    return html.replace("<head>", f"<head>\n    {meta}", 1)


def spa_index_response() -> HTMLResponse:
    """Serve index.html with runtime build id and strict no-cache headers."""
    index = STATIC_DIR / "index.html"
    html = inject_build_id(index.read_text(encoding="utf-8"))
    return HTMLResponse(html, headers=NO_CACHE_HEADERS)


def spa_file_response(path: Path) -> Response:
    """Serve index.html and other SPA shell files without browser or CDN caching."""
    if path.name == "index.html" or path.suffix == ".html":
        if path.name == "index.html":
            return spa_index_response()
        return FileResponse(path, headers=NO_CACHE_HEADERS)
    return FileResponse(path)


def create_app() -> FastAPI:
    app = FastAPI(title="Платформа репетиторства", version="1.0.0")

    @app.middleware("http")
    async def enforce_no_cache_html(request: Request, call_next):
        response = await call_next(request)
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("text/html"):
            for key, value in NO_CACHE_HEADERS.items():
                response.headers[key] = value
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    uploads_dir = STATIC_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

    if STATIC_DIR.exists() and (STATIC_DIR / "assets").exists():

        @app.get("/")
        async def spa_root():
            index = STATIC_DIR / "index.html"
            if index.exists():
                return spa_index_response()
            raise HTTPException(status_code=404, detail="Не найдено")

        app.mount(
            "/assets",
            CachedStaticFiles(directory=STATIC_DIR / "assets"),
            name="assets",
        )

        @app.get("/{full_path:path}")
        async def spa_fallback(request: Request, full_path: str):
            if full_path.startswith("api"):
                raise HTTPException(status_code=404, detail="Не найдено")
            file_path = STATIC_DIR / full_path
            if file_path.is_file():
                return spa_file_response(file_path)
            index = STATIC_DIR / "index.html"
            if index.exists():
                return spa_index_response()
            raise HTTPException(status_code=404, detail="Не найдено")

    return app


app = create_app()
