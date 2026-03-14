"""Standalone entry point for the A.L.F.R.E.D API server."""

from __future__ import annotations

import argparse
import sys

import uvicorn

from memory.database import check_connection
from utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="A.L.F.R.E.D API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    logger.info("Checking Supabase connection...")
    if check_connection():
        logger.info("Supabase connection verified")
    else:
        logger.error("Supabase connection failed — check .env credentials")
        sys.exit(1)

    logger.info(f"Starting A.L.F.R.E.D API on {args.host}:{args.port}")
    uvicorn.run("api.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
