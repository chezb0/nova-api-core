import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional, Sequence

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from nova_api_core.core.abstraction.database_manager import DatabaseManager
from nova_api_core.core.abstraction.error_handler import ErrorHandler
from nova_api_core.core.abstraction.logger import Logger
from nova_api_core.core.application.exception.base import AppException
from nova_api_core.core.config.bootstrap import BootstrapConfig
from nova_api_core.infra.logger.base import setup_uvicorn_logging
from nova_api_core.presentation.utils.error_mapper import to_fastapi_response


def create_app(
    *,
    config: Any,
    bootstrap: BootstrapConfig,
    logger: Logger,
    db_manager: Optional[DatabaseManager] = None,
    routes: Optional[Sequence[APIRouter]] = None,
    error_handlers: Optional[Sequence[ErrorHandler]] = None,
    allow_origins: Sequence[str] | None = None,
    allow_credentials: bool = True,
    allow_methods: Sequence[str] | None = None,
    allow_headers: Sequence[str] | None = None,
) -> FastAPI:

    # =========================
    # Lifespan
    # =========================
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info("Starting Nova API")

        try:
            if db_manager:
                await db_manager.connect()

            yield

        except AppException as app_exception:
            logger.critical(
                app_exception.technical_details
                or "[APP EXCEPTION] STARTUP FAILED"
            )
            raise

        except Exception as e:
            logger.critical(str(e))
            raise

        finally:
            logger.info("Shutting down Nova API")

            if db_manager:
                await db_manager.disconnect()

    try:
        # =========================
        # FastAPI app
        # =========================
        app = FastAPI(
            title=bootstrap.APP_NAME,
            version=bootstrap.APP_VERSION,
            debug=getattr(config, "DEBUG", False),
            lifespan=lifespan,
        )

        # =========================
        # Attach dependencies
        # =========================
        app.state.config = config
        app.state.bootstrap = bootstrap
        app.state.logger = logger
        app.state.db = db_manager

        # ==========================
        # CORS MIDDLEWARE
        # ==========================
        origins = allow_origins or ["*"]
        methods = allow_methods or ["*"]
        headers = allow_headers or ["*"]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=allow_credentials,
            allow_methods=methods,
            allow_headers=headers,
        )

        # =========================
        # Routes
        # =========================
        if routes:
            for router in routes:
                app.include_router(router)

        # ROOT ENDPOINT API...
        @app.get("/")
        def root() -> dict[str, Any]:
            return {
                "message": "API running...",
                "docs": "/docs",
            }

        # =========================
        # Error handlers
        # =========================
        def build_exception_handler(handler: ErrorHandler):

            async def _handler(
                request: Request,
                exc: Exception,
            ) -> JSONResponse:
                err = handler.handle(exc, logger)
                return to_fastapi_response(err)

            return _handler


        if error_handlers:
            for handler in error_handlers:
                app.add_exception_handler(
                    handler.exception,
                    build_exception_handler(handler),
                )

        # =========================
        # Logging (uvicorn/starlette)
        # =========================
        setup_uvicorn_logging(
            logger=logger,
            log_level=bootstrap.LOG_LEVEL,
        )

        return app
    except AppException as app_exception:
        logger.critical(
            msg=app_exception.technical_details or "[APP EXCEPTION] CAN'T START"
        )
        sys.exit(1)
    except Exception as e:
        logger.critical(msg=str(e))
        sys.exit(1)
