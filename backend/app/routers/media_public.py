"""Serve GET /media/... from local disk or S3 (see USE_S3_MEDIA)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.config import get_settings
from app.media_storage import (
    guess_content_type_for_local,
    iter_s3_media_chunks,
    key_uses_object_storage,
    resolved_local_media_file,
)

router = APIRouter()

_CACHE = "public, max-age=3600"


@router.get("/media/{file_path:path}", response_model=None)
def serve_public_media(file_path: str) -> FileResponse | StreamingResponse:
    if not file_path or ".." in file_path.split("/"):
        raise HTTPException(status_code=404, detail="Not found")
    key = file_path.lstrip("/")

    s = get_settings()
    if s.use_s3_media and key_uses_object_storage(key):
        s3_out = iter_s3_media_chunks(key)
        if s3_out:
            body_iter, content_type = s3_out
            return StreamingResponse(
                body_iter,
                media_type=content_type,
                headers={"Cache-Control": _CACHE},
            )

    local = resolved_local_media_file(key)
    if local is not None:
        return FileResponse(
            local,
            media_type=guess_content_type_for_local(local),
            headers={"Cache-Control": _CACHE},
        )
    raise HTTPException(status_code=404, detail="Not found")
