"""FastAPI exception handler registration."""
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from notbehomeless.models.base_exception import AppException

logger = logging.getLogger(__name__)

def init_exceptions_handler(app: FastAPI) -> None:
    """Register application exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_error_handler(request, exc: AppException) -> JSONResponse:
        logger.error("AppException [%s] %s -> %s", exc.website, exc.status_code, exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc)},
        )
