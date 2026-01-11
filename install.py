#!/usr/bin/env python3
"""
Interactive TUI installer for OpenCode skills using Textual.

Run with: uv run --with textual python3 install.py

Keyboard controls:
- ↑/↓: Navigate
- Space: Toggle selection
- Enter: Apply selections
- Esc: Clear selections
- Q: Quit
"""

import shutil
from pathlib import Path
from typing import Set, List
from dataclasses import dataclass

from textual.app import ComposeResult, App
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, Label
from textual.binding import Binding

SKILLS_DIR = Path("skills")
DEFAULT_BASE_DIR = Path.home() / "Code"
if not DEFAULT_BASE_DIR.exists():
    DEFAULT_BASE_DIR = Path.home()
DESTINATION = DEFAULT_BASE_DIR / ".config" / "opencode" / "skill"


@dataclass
class SkillInfo:
    name: str
    description: str
    path: Path
    dir_name: str


def get_skill_info(skill_dir: Path) -> SkillInfo:
    """Extract skill name and description from SKILL.md frontmatter"""
    skill_file = skill_dir / "SKILL.md"
    name = skill_dir.name
    description = ""

    if skill_file.exists():
        try:
            with open(skill_file, "r") as f:
                content = f.read()

            # Parse YAML frontmatter
            lines = content.split("\n")
            frontmatter_lines = []
            in_frontmatter = False

            for line in lines:
                if line.strip() == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                    continue
                if in_frontmatter:
                    frontmatter_lines.append(line)

            # Parse frontmatter as YAML
            for line in frontmatter_lines:
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip("\"'")
                elif line.startswith("description:"):
                    # Handle quoted descriptions with special characters
                    desc = line.split(":", 1)[1].strip()
                    # Remove surrounding quotes if present
                    if (desc.startswith('"') and desc.endswith('"')) or (
                        desc.startswith("'") and desc.endswith("'")
                    ):
                        desc = desc[1:-1]
                    description = desc
        except Exception:
            pass

    return SkillInfo(
        name=name,
        description=description,
        path=skill_dir,
        dir_name=skill_dir.name,
    )


def list_skills() -> List[SkillInfo]:
    """List all available skills, sorted by name"""
    if not SKILLS_DIR.exists():
        return []

    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            skills.append(get_skill_info(skill_dir))

    return sorted(skills, key=lambda s: s.name)


def get_installed_skills(destination: Path) -> Set[str]:
    """Get installed skill names"""
    if not destination.exists():
        return set()
    return {d.name for d in destination.iterdir() if d.is_dir()}


class SkillItem(ListItem):
    """A skill in the list with selection state"""

    def __init__(self, skill: SkillInfo, is_installed: bool):
        self.skill = skill
        self.is_installed = is_installed
        self.selected = False

        # Create label text with full description
        if is_installed:
            label_text = "[yellow]✓[/yellow]"
        else:
            label_text = " "

        label_text += f" {skill.name}"
        if skill.description:
            # Truncate description to fit reasonably in terminal
            desc = skill.description[:60]
            if len(skill.description) > 60:
                desc += "…"
            label_text += f" — {desc}"

        super().__init__(Label(label_text))


class SkillListScreen(Screen):
    """Main screen for selecting and installing skills"""

    BINDINGS = [
        Binding("space", "toggle_skill", "Toggle", show=True),
        Binding("escape", "clear_selections", "Clear All", show=True),
        Binding("enter", "execute_install", "Apply", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    SkillListScreen {
        layout: vertical;
        background: $surface;
    }

    #header {
        height: 3;
        background: $primary;
        color: $text;
        border-bottom: heavy $accent;
        padding: 1;
    }

    #header-title {
        width: 1fr;
        text-style: bold;
        color: $text;
    }

    #header-info {
        width: 1fr;
        color: $text;
        opacity: 0.8;
    }

    ListView {
        border: solid $accent;
        margin: 1;
        background: $boost;
        height: 1fr;
    }

    ListItem {
        padding: 0 1;
        height: auto;
    }

    ListItem:hover {
        background: $primary 20%;
    }

    ListItem:focus {
        background: $primary;
        text-style: bold;
    }

    #footer {
        height: 2;
        background: $secondary;
        color: $text;
        border-top: heavy $accent;
        padding: 0 1;
        content-align: left middle;
    }
    """

    def __init__(self):
        super().__init__()
        self.available_skills = list_skills()
        self.installed = get_installed_skills(DESTINATION)
        self.selected_skills: Set[str] = set()

    def compose(self) -> ComposeResult:
        # Header
        with Container(id="header"):
            yield Label(self._get_title(), id="header-title")
            yield Label(self._get_header_info(), id="header-info")

        # Skill list - yield items directly
        with ListView():
            for skill in self.available_skills:
                is_installed = skill.dir_name in self.installed
                yield SkillItem(skill, is_installed)

        # Footer
        yield Static(self._get_footer(), id="footer")

    def _get_title(self) -> str:
        return f"📦 Skills Manager"

    def _get_header_info(self) -> str:
        return f"Available: {len(self.available_skills)} | Installed: {len(self.installed)}"

    def _get_footer(self) -> str:
        if not self.selected_skills:
            return f"Destination: {DESTINATION}\nSpace: Toggle  Enter: Apply  Esc: Clear  Q: Quit"

        install = len([s for s in self.selected_skills if s not in self.installed])
        remove = len([s for s in self.selected_skills if s in self.installed])
        return f"Selected: {len(self.selected_skills)} (install: {install}, remove: {remove})  |  Enter: Apply  Esc: Clear  Q: Quit"

    def action_toggle_skill(self) -> None:
        """Toggle the selected skill"""
        try:
            list_view = self.query_one(ListView)
            if list_view.index is not None and list_view.index < len(
                list_view.children
            ):
                item = list_view.children[list_view.index]
                if isinstance(item, SkillItem):
                    item.selected = not item.selected
                    skill_name = item.skill.dir_name

                    # Update selection set
                    if item.selected:
                        self.selected_skills.add(skill_name)
                    else:
                        self.selected_skills.discard(skill_name)

                    # Update item display
                    self._update_item_display(item)
                    self._update_footer()
        except Exception:
            pass

    def action_clear_selections(self) -> None:
        """Clear all selections"""
        try:
            list_view = self.query_one(ListView)
            for item in list_view.children:
                if isinstance(item, SkillItem):
                    item.selected = False
                    self._update_item_display(item)

            self.selected_skills.clear()
            self._update_footer()
        except Exception:
            pass

    def action_execute_install(self) -> None:
        """Execute the installation/removal of selected skills"""
        if not self.selected_skills:
            return

        try:
            footer = self.query_one("#footer", Static)
            list_view = self.query_one(ListView)
        except Exception:
            return

        for skill_name in sorted(self.selected_skills):
            is_installed = skill_name in self.installed
            dest_path = DESTINATION / skill_name

            try:
                if is_installed:
                    shutil.rmtree(dest_path)
                else:
                    source_dir = next(
                        (
                            s.path
                            for s in self.available_skills
                            if s.dir_name == skill_name
                        ),
                        None,
                    )
                    if not source_dir:
                        continue
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_dir, dest_path)
            except Exception as e:
                footer.update(f"❌ Error: {e}")
                return

        # Update state
        self.installed = get_installed_skills(DESTINATION)

        # Clear selections and refresh display
        for item in list_view.children:
            if isinstance(item, SkillItem):
                item.selected = False
                item.is_installed = item.skill.dir_name in self.installed
                self._update_item_display(item)

        self.selected_skills.clear()
        footer.update("✓ Done!")

    def _update_item_display(self, item: SkillItem) -> None:
        """Update the display of a skill item"""
        # Build the marker with colors
        if item.selected:
            if item.is_installed:
                # Yellow checkmark + Red ✕ to show it will be removed
                marker = "[yellow]✓[/yellow][red]✕[/red]"
            else:
                # Red ✕ to show it will be installed
                marker = "[red]✕[/red]"
        else:
            if item.is_installed:
                # Yellow checkmark for installed
                marker = "[yellow]✓[/yellow]"
            else:
                # Space for not installed
                marker = " "

        text = f"{marker} {item.skill.name}"
        if item.skill.description:
            desc = item.skill.description[:60]
            if len(item.skill.description) > 60:
                desc += "…"
            text += f" — {desc}"

        # Update the label
        label = item.children[0]
        if isinstance(label, Label):
            label.update(text)

    def _update_footer(self) -> None:
        """Update the footer message"""
        try:
            footer = self.query_one("#footer", Static)
            footer.update(self._get_footer())
        except Exception:
            pass

    def action_quit(self) -> None:
        self.app.exit()


class InstallerApp(App):
    """Main installer application"""

    BINDINGS = [Binding("ctrl+c", "quit")]

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(SkillListScreen())


if __name__ == "__main__":
    app = InstallerApp()
    app.run()
