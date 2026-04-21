from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, message: str, *, status_code: int, error_code: str) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class ClientInputError(AppError):
    def __init__(self, message: str, *, error_code: str = "client_input_error") -> None:
        super().__init__(message, status_code=400, error_code=error_code)


class StorageError(AppError):
    def __init__(self, message: str, *, error_code: str = "storage_error") -> None:
        super().__init__(message, status_code=503, error_code=error_code)


class UpstreamServiceError(AppError):
    def __init__(self, message: str, *, error_code: str = "upstream_service_error") -> None:
        super().__init__(message, status_code=502, error_code=error_code)


class ServiceConfigurationError(AppError):
    def __init__(
        self,
        message: str,
        *,
        error_code: str = "service_configuration_error",
    ) -> None:
        super().__init__(message, status_code=500, error_code=error_code)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.warning("Handled app error | code=%s | message=%s", exc.error_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled server error | method=%s | path=%s",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "Unexpected server error. Please check server logs.",
                }
            },
        )
