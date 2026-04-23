"""Serve GET/HEAD /media/... from local disk or S3 (see USE_S3_MEDIA)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response, StreamingResponse

from app.config import get_settings
from app.media_storage import (
    guess_content_type_for_local,
    head_s3_media_meta,
    iter_s3_media_chunks,
    key_uses_object_storage,
    resolved_local_media_file,
)

router = APIRouter()

_CACHE = "public, max-age=3600"


@router.api_route("/media/{file_path:path}", methods=["GET", "HEAD"], response_model=None)
def serve_public_media(request: Request, file_path: str) -> FileResponse | StreamingResponse | Response:
    if not file_path or ".." in file_path.split("/"):
        raise HTTPException(status_code=404, detail="Not found")
    key = file_path.lstrip("/")

    s = get_settings()
    if request.method == "HEAD":
        if s.use_s3_media and key_uses_object_storage(key):
            meta = head_s3_media_meta(key)
            if meta:
                length, content_type = meta
                return Response(
                    content=b"",
                    media_type=content_type,
                    headers={"content-length": str(length), "Cache-Control": _CACHE},
                )
        local_head = resolved_local_media_file(key)
        if local_head is not None:
            length = local_head.stat().st_size
            return Response(
                content=b"",
                media_type=guess_content_type_for_local(local_head),
                headers={"content-length": str(length), "Cache-Control": _CACHE},
            )
        raise HTTPException(status_code=404, detail="Not found")

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
