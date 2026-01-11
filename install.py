#!/usr/bin/env python3
"""
Interactive TUI installer for OpenCode skills using Textual.

Run with: python3 -m textual run install.py:app
Or: uv run --with textual python3 install.py

Keyboard controls:
- Arrow Up/Down: Navigate
- Space: Toggle selection
- Enter: Apply selections
- Esc: Clear selections
- Q: Quit
- Tab: Navigate between screens
"""

import shutil
from pathlib import Path
from typing import Set, List
from dataclasses import dataclass

from textual.app import ComposeResult, on
from textual.containers import Container, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, SelectionList
from textual.binding import Binding

SKILLS_DIR = Path("skills")
DEFAULT_BASE_DIR = Path.home() / "Code"
if not DEFAULT_BASE_DIR.exists():
    DEFAULT_BASE_DIR = Path.home()

GLOBAL_SKILLS_DIR = DEFAULT_BASE_DIR / ".config" / "opencode" / "skill"
OPENCODE_SKILLS_DIR = Path.cwd() / ".opencode" / "skill"
CLAUDE_SKILLS_DIR = Path.cwd() / ".claude" / "skills"


@dataclass
class SkillInfo:
    """Skill metadata"""
    name: str
    description: str
    path: Path
    dir_name: str


def get_skill_info(skill_dir: Path) -> SkillInfo:
    """Extract skill name and description from SKILL.md frontmatter"""
    skill_file = skill_dir / "SKILL.md"
    name = skill_dir.name
    description = "No description"

    if skill_file.exists():
        try:
            with open(skill_file, "r") as f:
                content = f.read()

            lines = content.split("\n")
            in_frontmatter = False
            for line in lines:
                if line.strip() == "---":
                    in_frontmatter = not in_frontmatter
                    continue

                if in_frontmatter:
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.startswith("description:"):
                        description = line.split(":", 1)[1].strip()
        except Exception:
            pass

    return SkillInfo(
        name=name,
        description=description,
        path=skill_dir,
        dir_name=skill_dir.name,
    )


def list_skills() -> List[SkillInfo]:
    """List all available skills in repository, sorted by name"""
    if not SKILLS_DIR.exists():
        return []

    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            skill_info = get_skill_info(skill_dir)
            skills.append(skill_info)

    return sorted(skills, key=lambda s: s.name)


def get_installed_skills(destination: Path) -> Set[str]:
    """Get set of already installed skill names"""
    if not destination.exists():
        return set()

    installed = set()
    for skill_dir in destination.iterdir():
        if skill_dir.is_dir():
            installed.add(skill_dir.name)

    return installed


class SkillListScreen(Screen):
    """Screen for selecting and installing skills"""

    BINDINGS = [
        Binding("escape", "clear_selections", "Clear"),
        Binding("enter", "execute_install", "Apply"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    SkillListScreen {
        layout: vertical;
    }

    #title {
        height: 1;
        background: $boost;
        color: $text;
        text-align: center;
        text-style: bold;
    }

    #info {
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 1;
    }

    #selection-container {
        height: 1fr;
    }

    #status {
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }
    """

    def __init__(self, destination: Path, available_skills: List[SkillInfo]):
        super().__init__()
        self.destination = destination
        self.available_skills = available_skills
        self.installed = get_installed_skills(destination)
        self.selected: Set[str] = set()

    def compose(self) -> ComposeResult:
        """Compose the screen"""
        yield Static(self._get_destination_title(), id="title")
        yield Static(self._get_info_text(), id="info")
        
        items = []
        for skill in self.available_skills:
            label = self._format_skill_label(skill)
            items.append((label, skill.dir_name))

        with ScrollableContainer(id="selection-container"):
            yield SelectionList[str](*items, id="selection-list")
        
        yield Static(self._get_status_text(), id="status")

    def _get_destination_title(self) -> str:
        """Get destination title"""
        if self.destination == GLOBAL_SKILLS_DIR:
            return "📦 Skills Installer - Global (~/.config/opencode/skill/)"
        elif self.destination == OPENCODE_SKILLS_DIR:
            return "📦 Skills Installer - OpenCode (.opencode/skill/)"
        elif self.destination == CLAUDE_SKILLS_DIR:
            return "📦 Skills Installer - Claude (.claude/skills/)"
        else:
            return f"📦 Skills Installer - {self.destination}"

    def _get_info_text(self) -> str:
        """Get info text"""
        installed_count = len(self.installed)
        return f"Available: {len(self.available_skills)} | Installed: {installed_count} | Space: select | ↑↓: navigate"

    def _format_skill_label(self, skill: SkillInfo) -> str:
        """Format skill label with status indicator"""
        is_installed = skill.dir_name in self.installed
        status = "✓" if is_installed else " "
        desc = skill.description[:50] if skill.description else "No description"
        return f"[{status}] {skill.name:35} {desc}"

    def _get_status_text(self) -> str:
        """Get status text"""
        install_count = len([s for s in self.selected if s not in self.installed])
        remove_count = len([s for s in self.selected if s in self.installed])
        total = len(self.selected)
        
        if total == 0:
            return "No selections"
        else:
            return f"Selected: {total} (Install: {install_count}, Remove: {remove_count})"

    @on(SelectionList.SelectedChanged)
    def on_selection_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Handle selection changes"""
        selection_list = self.query_one("#selection-list", SelectionList)
        self.selected = set(selection_list.selected)
        
        status_widget = self.query_one("#status", Static)
        status_widget.update(self._get_status_text())

    def action_clear_selections(self) -> None:
        """Clear all selections"""
        selection_list = self.query_one("#selection-list", SelectionList)
        for item in list(selection_list.selected):
            selection_list.toggle(item)
        
        self.selected.clear()
        status_widget = self.query_one("#status", Static)
        status_widget.update(self._get_status_text())

    def action_execute_install(self) -> None:
        """Execute installation/removal"""
        if not self.selected:
            return

        for skill_name in sorted(self.selected):
            is_installed = skill_name in self.installed
            dest_path = self.destination / skill_name

            try:
                if is_installed:
                    shutil.rmtree(dest_path)
                else:
                    source_dir = None
                    for skill in self.available_skills:
                        if skill.dir_name == skill_name:
                            source_dir = skill.path
                            break

                    if not source_dir:
                        continue

                    if dest_path.exists():
                        shutil.rmtree(dest_path)

                    shutil.copytree(source_dir, dest_path)

            except Exception as e:
                status_widget = self.query_one("#status", Static)
                status_widget.update(f"❌ Error: {e}")
                return

        self.installed = get_installed_skills(self.destination)
        self.selected.clear()

        selection_list = self.query_one("#selection-list", SelectionList)
        selection_list.clear()
        
        items = []
        for skill in self.available_skills:
            label = self._format_skill_label(skill)
            items.append((label, skill.dir_name))
        
        for label, skill_id in items:
            selection_list.add_option((label, skill_id))

        status_widget = self.query_one("#status", Static)
        status_widget.update("✓ Installation complete")

    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()


class DestinationScreen(Screen):
    """Screen for selecting installation destination"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    DestinationScreen {
        layout: vertical;
        align: center middle;
    }

    #destination-container {
        width: 70;
        height: auto;
        border: solid $primary;
        background: $boost;
        padding: 2;
    }

    #title {
        height: 1;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #info {
        height: auto;
        margin-bottom: 2;
    }

    #buttons {
        height: auto;
        layout: vertical;
    }

    Button {
        margin: 0 0 1 0;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the screen"""
        with Container(id="destination-container"):
            yield Static("📦 Select Installation Destination", id="title")
            yield Static("Choose where to install skills (↑↓ navigate, Enter select):", id="info")
            
            with Vertical(id="buttons"):
                yield Button("Global (~/.config/opencode/skill/)", id="btn-global", variant="primary")
                yield Button("OpenCode (.opencode/skill/)", id="btn-opencode", variant="primary")
                yield Button("Claude (.claude/skills/)", id="btn-claude", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        button_id = event.button.id
        
        destinations = {
            "btn-global": GLOBAL_SKILLS_DIR,
            "btn-opencode": OPENCODE_SKILLS_DIR,
            "btn-claude": CLAUDE_SKILLS_DIR,
        }

        if button_id in destinations:
            destination = destinations[button_id]
            skills = list_skills()
            
            if not skills:
                self.app.exit("No skills found in repository")
                return
            
            self.app.push_screen(SkillListScreen(destination, skills))

    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()


if __name__ == "__main__":
    from textual.app import App

    class InstallerApp(App):
        """Textual installer app"""
        BINDINGS = [
            Binding("ctrl+c", "quit", "Quit"),
        ]

        CSS = """
        Screen {
            background: $surface;
            color: $text;
        }
        """

        def on_mount(self) -> None:
            self.push_screen(DestinationScreen())

    app = InstallerApp()
