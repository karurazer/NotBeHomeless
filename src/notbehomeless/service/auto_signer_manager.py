"""Keeps running auto-signers alive for the lifetime of the application."""
import asyncio
import logging
from contextlib import suppress

from notbehomeless.models.website import Website
from notbehomeless.service.exceptions import (
    AutoSignerAlreadyRunning,
    AutoSignerNotRunning,
)
from notbehomeless.service.room_auto_signer import RoomAutoSigner

logger = logging.getLogger(__name__)


class AutoSignerManager:
    """
        Owns one auto-signer asyncio task per site.

        Lives in ``app.state`` (not in a per-request service) because a signer
        must outlive the request that started it.
    """

    def __init__(self):
        self._signers: dict[Website, RoomAutoSigner] = {}
        self._tasks: dict[Website, asyncio.Task] = {}

    def start(self, site: Website, signer: RoomAutoSigner) -> None:
        task = self._tasks.get(site)
        if task is not None and not task.done():
            raise AutoSignerAlreadyRunning(site)

        self._signers[site] = signer
        self._tasks[site] = asyncio.create_task(
            signer.start(), name=f"autosigner-{site.value}"
        )
        logger.info("Auto-signer started for %s", site.value)

    async def stop(self, site: Website) -> None:
        task = self._tasks.get(site)
        if task is None or task.done():
            raise AutoSignerNotRunning(site)

        self._tasks.pop(site, None)
        self._signers.pop(site, None)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        logger.info("Auto-signer stopped for %s", site.value)

    def status(self) -> list[dict]:
        return [
            {
                "site": site.value,
                "running": not task.done(),
                "period_ms": self._signers[site].period,
            }
            for site, task in self._tasks.items()
        ]

    async def stop_all(self) -> None:
        tasks = list(self._tasks.values())
        self._tasks.clear()
        self._signers.clear()

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("All auto-signers stopped (%d)", len(tasks))
