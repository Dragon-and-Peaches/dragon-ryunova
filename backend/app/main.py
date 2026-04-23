from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.config import get_settings
from app.constants import DEFAULT_ORGANISATION_ID
from app.media_storage import ensure_org_media_folders
from app.routers import admin_users, auth, brands, categories, marketplaces, media_public, organisations, products, stats

settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
ensure_org_media_folders(DEFAULT_ORGANISATION_ID)

app = FastAPI(title="RyuNova Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI()
api.include_router(auth.router)
api.include_router(organisations.router)
api.include_router(admin_users.router)
api.include_router(stats.router)
api.include_router(brands.router)
api.include_router(categories.router)
api.include_router(marketplaces.router)
api.include_router(products.router)
api.include_router(media_public.router)

app.mount("/api/v1", api)


@app.api_route("/health", methods=["GET", "HEAD"], response_model=None)
def health(request: Request) -> dict[str, str] | Response:
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "ok"}
