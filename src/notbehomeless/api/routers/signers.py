"""Auto-signer control endpoints."""
from typing import Annotated

from fastapi import APIRouter, Query

from notbehomeless.api.dependencies import (
    AutoSignerManagerDep,
    RoomFilterDep,
    RoomspotDep,
    SessionDep,
)
from notbehomeless.models.website import Website
from notbehomeless.service.room_auto_signer import RoomAutoSigner

router = APIRouter(prefix="/signers", tags=["signers"])


@router.get("")
async def list_signers(manager: AutoSignerManagerDep) -> list[dict]:
    """List auto-signers and whether they are running."""
    return manager.status()


@router.post(
    "/roomspot",
    status_code=201,
    responses={409: {"description": "Auto-signer is already running"}},
)
async def start_roomspot_auto_signer(
    api: RoomspotDep,
    session: SessionDep,
    room_filter: RoomFilterDep,
    manager: AutoSignerManagerDep,
    period_seconds: Annotated[float, Query(gt=0, description="Seconds between check cycles")] = 60,
) -> dict[str, str]:
    """Start the Roomspot auto-signer with the given filter (query params)."""
    signer = RoomAutoSigner(
        room_filter=room_filter,
        api=api,
        session=session,
        period=int(period_seconds * 1000),
    )
    manager.start(Website.ROOMSPOT, signer)
    return {"detail": "Roomspot auto-signer started"}


@router.delete(
    "/roomspot",
    responses={404: {"description": "Auto-signer is not running"}},
)
async def stop_roomspot_auto_signer(manager: AutoSignerManagerDep) -> dict[str, str]:
    """Stop the Roomspot auto-signer."""
    await manager.stop(Website.ROOMSPOT)
    return {"detail": "Roomspot auto-signer stopped"}
