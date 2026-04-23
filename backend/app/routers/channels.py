from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.listing_channel import RyunovaListingChannel
from app.schemas.listing_channel import ChannelRead, ChannelUpdate

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=list[ChannelRead])
def list_channels(
    db: Annotated[Session, Depends(get_db)],
    _user: CurrentUser,
    include_inactive: bool = False,
) -> list[ChannelRead]:
    """List all marketplace / e-commerce channels (global configuration)."""
    stmt = select(RyunovaListingChannel).order_by(RyunovaListingChannel.sort_order, RyunovaListingChannel.name)
    if not include_inactive:
        stmt = stmt.where(RyunovaListingChannel.active.is_(True))
    rows = db.scalars(stmt).all()
    return [ChannelRead.model_validate(r) for r in rows]


@router.get("/{channel_id}", response_model=ChannelRead)
def get_channel(
    channel_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _user: CurrentUser,
) -> ChannelRead:
    ch = db.get(RyunovaListingChannel, channel_id)
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return ChannelRead.model_validate(ch)


@router.patch("/{channel_id}", response_model=ChannelRead)
def update_channel(
    channel_id: uuid.UUID,
    body: ChannelUpdate,
    db: Annotated[Session, Depends(get_db)],
    _user: CurrentUser,
) -> ChannelRead:
    """Update channel metadata and integration requirements (JSON)."""
    ch = db.get(RyunovaListingChannel, channel_id)
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(ch, k, v)
    db.commit()
    db.refresh(ch)
    return ChannelRead.model_validate(ch)
