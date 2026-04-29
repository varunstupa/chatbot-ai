"""Structured logging configured from application settings."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config.settings import Settings


def configure_logging(s: "Settings") -> None:
    """Apply log level and optional JSON-ish structured formatter from config."""
    level = getattr(logging, s.logging.level.upper(), logging.INFO)
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    if s.logging.json_format:

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                payload = {
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    payload["exc_info"] = self.formatException(record.exc_info)
                for k, v in record.__dict__.items():
                    if k.startswith("_") or k in (
                        "args",
                        "msg",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "levelno",
                        "levelname",
                        "name",
                        "pathname",
                        "filename",
                        "module",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                        "lineno",
                        "funcName",
                        "process",
                        "processName",
                        "thread",
                        "threadName",
                    ):
                        continue
                    if k not in payload:
                        payload[k] = v
                import json

                return json.dumps(payload, default=str)

        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            )
        )
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
