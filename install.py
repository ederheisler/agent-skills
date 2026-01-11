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

from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.binding import Binding
from textual.widget import Widget
from textual.events import Key

SKILLS_DIR = Path("skills")
DEFAULT_BASE_DIR = Path.home() / "Code"
if not DEFAULT_BASE_DIR.exists():
    DEFAULT_BASE_DIR = Path.home()

GLOBAL_SKILLS_DIR = DEFAULT_BASE_DIR / ".config" / "opencode" / "skill"
OPENCODE_SKILLS_DIR = Path.cwd() / ".opencode" / "skill"
CLAUDE_SKILLS_DIR = Path.cwd() / ".claude" / "skills"


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


class SkillSelector(Static):
    """Custom skill list selector"""

    DEFAULT_CSS = """
    SkillSelector {
        background: $panel;
        height: 1fr;
        overflow: auto;
    }
    """

    def __init__(self, skills: List[SkillInfo], installed: Set[str]):
        super().__init__()
        self.skills = skills
        self.installed = installed
        self.selected: Set[str] = set()
        self.cursor = 0
        self.render_content()

    def render_content(self) -> None:
        """Render the skill list"""
        lines = []
        for idx, skill in enumerate(self.skills):
            is_selected = skill.dir_name in self.selected
            is_installed = skill.dir_name in self.installed
            
            # Build the line
            cursor = "▶ " if idx == self.cursor else "  "
            checkbox = "[✓]" if is_selected else "[ ]"
            status = "•" if is_installed else " "
            
            line = f"{cursor}{checkbox} {status} {skill.name}"
            
            # Highlight current row
            if idx == self.cursor:
                lines.append(f"[reverse]{line}[/reverse]")
            else:
                lines.append(line)
        
        self.update("\n".join(lines))

    def on_key(self, event: Key) -> None:
        """Handle keyboard input"""
        if event.key == "up":
            self.cursor = max(0, self.cursor - 1)
            self.render_content()
            event.prevent_default()
        elif event.key == "down":
            self.cursor = min(len(self.skills) - 1, self.cursor + 1)
            self.render_content()
            event.prevent_default()
        elif event.key == "space":
            skill_name = self.skills[self.cursor].dir_name
            if skill_name in self.selected:
                self.selected.remove(skill_name)
            else:
                self.selected.add(skill_name)
            self.render_content()
            event.prevent_default()

    def get_selected(self) -> Set[str]:
        return self.selected

    def clear_selection(self) -> None:
        self.selected.clear()
        self.render_content()


class SkillListScreen(Screen):
    """Screen for selecting and installing skills"""

    BINDINGS = [
        Binding("escape", "clear_selections", "Clear All"),
        Binding("enter", "execute_install", "Apply"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    SkillListScreen {
        layout: vertical;
    }

    #title {
        height: 1;
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
    }

    #info {
        height: 1;
        background: $boost;
        color: $text;
        padding: 0 1;
    }

    SkillSelector {
        border: solid $accent;
        margin: 1;
    }

    #status {
        height: 1;
        background: $secondary;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self, destination: Path, available_skills: List[SkillInfo]):
        super().__init__()
        self.destination = destination
        self.available_skills = available_skills
        self.installed = get_installed_skills(destination)
        self.skill_selector: SkillSelector | None = None

    def compose(self) -> ComposeResult:
        yield Static(self._get_title(), id="title")
        yield Static(self._get_info(), id="info")
        
        skill_selector = SkillSelector(self.available_skills, self.installed)
        self.skill_selector = skill_selector
        yield skill_selector
        
        yield Static(self._get_status(), id="status")

    def _get_title(self) -> str:
        if self.destination == GLOBAL_SKILLS_DIR:
            return "📦 Global (~/.config/opencode/skill/)"
        elif self.destination == OPENCODE_SKILLS_DIR:
            return "📦 OpenCode (.opencode/skill/)"
        elif self.destination == CLAUDE_SKILLS_DIR:
            return "📦 Claude (.claude/skills/)"
        return f"📦 {self.destination}"

    def _get_info(self) -> str:
        return f"Available: {len(self.available_skills)} | Installed: {len(self.installed)}"

    def _get_status(self) -> str:
        if not self.skill_selector:
            return "Ready"
        selected = self.skill_selector.get_selected()
        if not selected:
            return "Space: select | Enter: apply | ESC: clear | Q: quit"
        
        install = len([s for s in selected if s not in self.installed])
        remove = len([s for s in selected if s in self.installed])
        return f"Selected: {len(selected)} (install: {install}, remove: {remove}) | Enter: apply"

    def on_key(self, event: Key) -> None:
        """Update status on any key"""
        status = self.query_one("#status", Static)
        status.update(self._get_status())

    def action_clear_selections(self) -> None:
        if self.skill_selector:
            self.skill_selector.clear_selection()
            self.query_one("#status", Static).update(self._get_status())

    def action_execute_install(self) -> None:
        if not self.skill_selector:
            return
        
        selected = self.skill_selector.get_selected()
        if not selected:
            return

        status_widget = self.query_one("#status", Static)

        for skill_name in sorted(selected):
            is_installed = skill_name in self.installed
            dest_path = self.destination / skill_name

            try:
                if is_installed:
                    shutil.rmtree(dest_path)
                else:
                    source_dir = next(
                        (s.path for s in self.available_skills if s.dir_name == skill_name),
                        None
                    )
                    if not source_dir:
                        continue
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_dir, dest_path)
            except Exception as e:
                status_widget.update(f"Error: {e}")
                return

        self.installed = get_installed_skills(self.destination)
        self.skill_selector.installed = self.installed
        self.skill_selector.selected.clear()
        self.skill_selector.render_content()
        status_widget.update("✓ Done")

    def action_quit(self) -> None:
        self.app.exit()


class DestinationScreen(Screen):
    """Screen for selecting destination"""

    BINDINGS = [Binding("q", "quit", "Quit")]

    CSS = """
    DestinationScreen {
        layout: vertical;
        align: center middle;
    }

    #container {
        width: 60;
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

    Button {
        margin: 0 0 1 0;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="container"):
            yield Static("📦 Select Installation Destination", id="title")
            
            with Vertical():
                yield Button("Global (~/.config/opencode/skill/)", id="btn-global", variant="primary")
                yield Button("OpenCode (.opencode/skill/)", id="btn-opencode", variant="primary")
                yield Button("Claude (.claude/skills/)", id="btn-claude", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        destinations = {
            "btn-global": GLOBAL_SKILLS_DIR,
            "btn-opencode": OPENCODE_SKILLS_DIR,
            "btn-claude": CLAUDE_SKILLS_DIR,
        }

        if event.button.id in destinations:
            destination = destinations[event.button.id]
            skills = list_skills()
            
            if not skills:
                self.app.exit("No skills found")
                return
            
            self.app.push_screen(SkillListScreen(destination, skills))

    def action_quit(self) -> None:
        self.app.exit()


if __name__ == "__main__":
    from textual.app import App

    class InstallerApp(App):
        BINDINGS = [Binding("ctrl+c", "quit")]

        CSS = """
        Screen {
            background: $surface;
        }
        """

        def on_mount(self) -> None:
            self.push_screen(DestinationScreen())

    InstallerApp().run()
