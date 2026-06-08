"""Central logging configuration.

`configure_logging` is idempotent and safe to call from any entrypoint (Streamlit,
the index build script, or tests). Modules obtain a logger via `get_logger`.
"""

import logging

from support_agent.config import get_settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_configured = False


def configure_logging() -> None:
    """Attach a single stream handler to the package logger."""
    global _configured
    if _configured:
        return

    level = get_settings().log_level.upper()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger("support_agent")
    root.setLevel(level)
    root.addHandler(handler)
    root.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger, configuring logging on first use."""
    configure_logging()
    return logging.getLogger(f"support_agent.{name}")
