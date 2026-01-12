"""Main application class"""
import logging

from textual.app import App
from textual.binding import Binding

from .ui.screens import SkillListScreen

logger = logging.getLogger(__name__)


class InstallerApp(App):
    """Main installer application"""

    BINDINGS = [Binding("ctrl+c", "quit")]

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def on_mount(self) -> None:
        logger.info("=== InstallerApp mounted ===")
        self.push_screen(SkillListScreen())
