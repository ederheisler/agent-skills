"""
Persistence layer for storing app state.
"""

import json
from pathlib import Path
from typing import Any

from .config import logger

DB_FILE = Path("db.json")


def load_state() -> dict[str, Any]:
    """Load application state from db.json"""
    if not DB_FILE.exists():
        logger.info("db.json not found, returning default state")
        return {}

    try:
        with open(DB_FILE, "r") as f:
            state = json.load(f)
            logger.info(f"Loaded state from db.json: {state}")
            return state
    except Exception as e:
        logger.error(f"Failed to load db.json: {e}")
        return {}


def save_state(state: dict[str, Any]) -> None:
    """Save application state to db.json"""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(state, f, indent=2)
            logger.info(f"Saved state to db.json: {state}")
    except Exception as e:
        logger.error(f"Failed to save db.json: {e}")


def get_last_destination() -> Path | None:
    """Get the last selected destination directory"""
    state = load_state()
    dest = state.get("last_destination")
    if dest:
        logger.info(f"Retrieved last_destination: {dest}")
        return Path(dest)
    logger.info("No last_destination found in state")
    return None


def set_last_destination(path: Path) -> None:
    """Save the last selected destination directory"""
    state = load_state()
    state["last_destination"] = str(path)
    save_state(state)
    logger.info(f"Set last_destination to: {path}")
