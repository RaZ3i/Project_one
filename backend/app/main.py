from pathlib import Path
from typing import ClassVar

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}
IMMUTABLE_ASSET_HEADERS = {"Cache-Control": "public, max-age=31536000, immutable"}


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


def spa_file_response(path: Path) -> FileResponse:
    """Serve index.html and other SPA shell files without browser caching."""
    if path.name == "index.html" or path.suffix == ".html":
        return FileResponse(path, headers=NO_CACHE_HEADERS)
    return FileResponse(path)


def create_app() -> FastAPI:
    app = FastAPI(title="Платформа репетиторства", version="1.0.0")

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
                return spa_file_response(index)
            raise HTTPException(status_code=404, detail="Не найдено")

    return app


app = create_app()
