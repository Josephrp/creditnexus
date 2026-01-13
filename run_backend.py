"""Executable entry point for bundling the CreditNexus backend."""

from __future__ import annotations

import logging
import os
from typing import Final

import uvicorn

from server import app

logger = logging.getLogger("creditnexus.backend")
logging.basicConfig(level=logging.INFO)

DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 8000


def main() -> None:
    host = os.getenv("CREDITNEXUS_BACKEND_HOST", DEFAULT_HOST)
    port = int(os.getenv("CREDITNEXUS_BACKEND_PORT", DEFAULT_PORT))

    logger.info("Starting CreditNexus backend", extra={"host": host, "port": port})

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.getenv("CREDITNEXUS_BACKEND_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
