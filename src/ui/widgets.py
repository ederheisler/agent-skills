"""UI widgets for skills manager"""

import logging

from textual.binding import Binding
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, ListItem, Static

from ..models import SkillInfo

logger = logging.getLogger(__name__)


class SkillItem(ListItem):
    """A skill in the list with selection state"""

    def __init__(self, skill: SkillInfo, is_installed: bool):
        self.skill = skill
        self.is_installed = is_installed
        self.selected = False
        self.is_reinstall = False
        self.is_plugin = skill.is_plugin

        text = self._format_skill_text()
        super().__init__(Label(text))

    def _format_skill_text(self) -> str:
        """Format skill as aligned columns: MARKER | TITLE | DESCRIPTION"""
        if not self.skill.name:
            return ""

        # Column 1: Marker (3 chars wide)
        if self.selected:
            if self.is_installed:
                if self.is_reinstall:
                    marker = "[green]↻[/green]"
                else:
                    marker = "[red]✖[/red]"
            else:
                marker = "[white]✓[/white]"
        else:
            if self.is_installed:
                marker = "[yellow]o[/yellow]"
            else:
                marker = " "

        if self.selected:
            marker_col = f"{marker} "
        else:
            marker_col = f"{marker}  "

        title_col = f"{self.skill.name:<32}"
        desc_col = f"  {self.skill.description}" if self.skill.description else ""

        return f"{marker_col}{title_col}{desc_col}"

    def refresh_display(self) -> None:
        """Update the label text based on current state"""
        text = self._format_skill_text()
        label = self.query_one(Label)
        label.update(text)


class DescriptionModal(Screen):
    """Modal overlay to show full skill description"""

    BINDINGS = [Binding("e", "close_modal", "Close", show=True)]
    MODAL = True

    CSS = """
    DescriptionModal {
        align: center middle;
        background: rgba(0,0,0,0.7);
    }

    #modal-container {
        width: 80;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }

    #title {
        text-align: center;
        margin-bottom: 1;
        text-style: bold;
        color: $text;
    }

    #description {
        width: 100%;
        height: auto;
    }

    #close_btn {
        margin-top: 2;
        align: center middle;
    }
    """

    def __init__(self, skill: SkillInfo):
        super().__init__()
        self.skill = skill

    def compose(self):
        """Show skill title and full description in centered modal"""
        with Vertical(id="modal-container"):
            yield Label(f"[bold]{self.skill.name}[/bold]", id="title")
            yield Static(
                self.skill.description or "No description available", id="description"
            )
            with Center():
                yield Button("Close (e)", id="close_btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close modal on button press"""
        self.app.pop_screen()

    def action_close_modal(self):
        """Close the modal"""
        self.app.pop_screen()


class LogModal(Screen):
    """Modal to display log output"""

    BINDINGS = [
        Binding("escape", "close_modal", "Close", show=True),
        Binding("l", "close_modal", "Close", show=True),
    ]
    MODAL = True

    CSS = """
    LogModal {
        align: center middle;
        background: rgba(0,0,0,0.8);
    }

    #log-container {
        width: 90%;
        height: 80%;
        background: $surface;
        border: solid $primary;
        padding: 2;
        layout: vertical;
    }

    #log-title {
        text-align: center;
        margin-bottom: 1;
        text-style: bold;
        color: $text;
    }

    #log-content {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        margin-bottom: 1;
    }

    #close_btn {
        margin-top: 1;
    }
    """

    def __init__(self, log_content: str):
        super().__init__()
        self.log_content = log_content

    def compose(self):
        """Show log content"""
        with Container(id="log-container"):
            yield Label("[bold]Installation Logs[/bold]", id="log-title")
            yield Static(self.log_content, id="log-content")
            with Center():
                yield Button("Close (l)", id="close_btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Close modal on button press"""
        self.app.pop_screen()

    def action_close_modal(self):
        """Close the modal"""
        self.app.pop_screen()
