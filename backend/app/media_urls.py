"""Build public URLs for uploaded media (avatars, org logos, product images)."""

from __future__ import annotations

from app.config import get_settings


def public_media_url(s3_key: str | None) -> str | None:
    if not s3_key:
        return None
    s = get_settings()
    # Always use the API host + `/api/v1/media/...`. The handler streams from S3 with IAM
    # (USE_S3_MEDIA) or reads local disk. Sending browsers straight to MEDIA_PUBLIC_BASE_URL
    # (virtual-hosted S3) requires public object ACLs; a private bucket returns 403 and broken images.
    base = str(s.api_public_url).rstrip("/")
    prefix = s.media_url_prefix.rstrip("/")
    return f"{base}{prefix}/{s3_key}"
