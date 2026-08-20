"""Divine Astro — Vedic chart analysis and readings.

Configuration is read from the environment. A local `.env` file (never
committed — see .gitignore) is loaded here, before any submodule imports, so
that every module can simply read `os.environ` at import time without caring
where the value came from.
"""

from __future__ import annotations

import os
from pathlib import Path

__version__ = "2.0.0"

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _load_env() -> None:
    """Load .env without clobbering variables already set in the real environment.

    Real environment variables always win — that is what makes the same image
    deployable to GCP, where secrets arrive from Secret Manager rather than a file.
    """
    if not _ENV_FILE.exists():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(_ENV_FILE, override=False)
        return
    except ImportError:
        pass

    # Minimal fallback so the app still boots if python-dotenv is absent.
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env()
