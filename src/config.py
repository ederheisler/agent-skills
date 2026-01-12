"""Configuration and constants"""

import logging
from datetime import datetime
from pathlib import Path

# Setup logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"installer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
    ],
)

logger = logging.getLogger(__name__)

# Paths
SKILLS_DIR = Path("skills")
DEFAULT_BASE_DIR = Path.home() / "Code"
if not DEFAULT_BASE_DIR.exists():
    DEFAULT_BASE_DIR = Path.home()
DESTINATION = DEFAULT_BASE_DIR / ".config" / "opencode" / "skill"
