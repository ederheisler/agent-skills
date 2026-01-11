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
import logging
from datetime import datetime

from textual.app import ComposeResult, App
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, Label
from textual.binding import Binding

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
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
    """List all available skills, sorted by name, with plugin script first"""
    skills = []

    # Add plugin script first
    plugin_path = (
        Path.home()
        / ".config"
        / "opencode"
        / "superpowers"
        / ".opencode"
        / "plugin"
        / "superpowers.js"
    )
    plugin_skill = SkillInfo(
        name="superpowers.js",
        description="OpenCode plugin for superpowers integration",
        path=plugin_path.parent,
        dir_name="superpowers.js",
    )
    skills.append(plugin_skill)

    # Add separator (empty skill for visual gap)
    separator_skill = SkillInfo(name="", description="", path=Path(""), dir_name="")
    skills.append(separator_skill)

    # Add regular skills
    if SKILLS_DIR.exists():
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if skill_dir.is_dir():
                skills.append(get_skill_info(skill_dir))

    return skills


def get_installed_skills(destination: Path) -> Set[str]:
    """Get installed skill names"""
    installed = set()

    # Check regular skills
    if destination.exists():
        installed.update({d.name for d in destination.iterdir() if d.is_dir()})

    # Check plugin script
    plugin_target = Path.home() / ".config" / "opencode" / "plugin" / "superpowers.js"
    logger.info(
        f"Checking plugin: {plugin_target}, exists={plugin_target.exists()}, is_symlink={plugin_target.is_symlink()}"
    )
    if plugin_target.exists() and plugin_target.is_symlink():
        installed.add("superpowers.js")
        logger.info("Plugin superpowers.js detected as installed")
    else:
        logger.info(
            f"Plugin superpowers.js NOT detected: exists={plugin_target.exists()}, symlink={plugin_target.is_symlink()}"
        )

    return installed


class SkillItem(ListItem):
    """A skill in the list with selection state"""

    def __init__(self, skill: SkillInfo, is_installed: bool):
        self.skill = skill
        self.is_installed = is_installed
        self.selected = False

        # Create formatted text with 3 columns: marker | title | description
        text = self._format_skill_text()
        super().__init__(Label(text))

    def _format_skill_text(self) -> str:
        """Format skill as aligned columns: MARKER | TITLE | DESCRIPTION"""
        # Handle separator (empty skill for visual gap)
        if not self.skill.name:
            return ""

        # Column 1: Marker (3 chars wide)
        if self.selected:
            if self.is_installed:
                marker = "[yellow]o[/yellow][red]✖[/red]"
            else:
                marker = "[white]✓[/white]"
        else:
            if self.is_installed:
                marker = "[yellow]o[/yellow]"
            else:
                marker = " "

        # Ensure marker column is 3 chars (accounting for ANSI codes)
        if self.selected and self.is_installed:
            # o✖ takes 2 visual chars, pad to 3
            marker_col = f"{marker} "
        else:
            # Single chars get 2 spaces
            marker_col = f"{marker}  "

        # Column 2: Title (32 chars wide)
        title_col = f"{self.skill.name:<32}"

        # Column 3: Description (remaining space)
        desc_col = ""
        if self.skill.description:
            desc_col = f"  {self.skill.description}"

        return f"{marker_col}{title_col}{desc_col}"


class DescriptionModal(Screen):
    """Modal overlay to show full skill description"""

    BINDINGS = [
        Binding("e", "close_modal", "Close", show=True),
    ]

    MODAL = True  # Make this a modal screen

    CSS = """
    DescriptionModal {
        align: center middle;
        background: rgba(0,0,0,0.7);  /* Semi-transparent dark background */
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
        from textual.widgets import Static, Button
        from textual.containers import Vertical, Center

        with Center():
            with Vertical(id="modal-container"):
                yield Static(f"[bold]{self.skill.name}[/bold]", id="title")
                yield Static(
                    self.skill.description or "No description available.",
                    id="description",
                )
                with Center():
                    yield Button("Close (E)", id="close_btn")

    def on_button_pressed(self, event):
        """Handle button press"""
        if event.button.id == "close_btn":
            self.app.pop_screen()

    def action_close_modal(self):
        """Close the modal"""
        self.app.pop_screen()


class LogModal(Screen):
    """Modal to show recent log entries"""

    MODAL = True

    BINDINGS = [
        Binding("escape", "close_modal", "Close", show=True),
    ]

    CSS = """
    LogModal {
        align: center middle;
        background: rgba(0,0,0,0.7);
    }

    #modal-container {
        width: 90;
        height: 80;
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

    #log-content {
        width: 100%;
        height: 100%;
        overflow: auto;
    }

    #close_btn {
        margin-top: 2;
        align: center middle;
    }
    """

    def compose(self):
        """Show recent log entries"""
        from textual.widgets import Static, Button
        from textual.containers import Vertical, Center

        # Get recent log content
        log_content = self._get_recent_logs()

        with Vertical(id="modal-container"):
            yield Static("Recent Log Entries", id="title")
            yield Static(log_content, id="log-content")
            with Center():
                yield Button("Close (ESC)", id="close_btn")

    def _get_recent_logs(self) -> str:
        """Get the 20 most recent log lines"""
        try:
            log_files = list(LOG_DIR.glob("installer_*.log"))
            if not log_files:
                return "No log files found."

            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

            # Read the last 20 lines
            with open(latest_log, "r") as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines

            return "".join(recent_lines)
        except Exception as e:
            return f"Error reading logs: {e}"

    def on_button_pressed(self, event):
        """Handle button press"""
        if event.button.id == "close_btn":
            self.app.pop_screen()

    def action_close_modal(self):
        """Close the modal"""
        self.app.pop_screen()


class SkillListScreen(Screen):
    """Main screen for selecting and installing skills"""

    BINDINGS = [
        Binding("space", "toggle_skill", "Toggle", show=True),
        Binding("enter", "execute_install", "Apply", show=True),
        Binding("e", "show_description", "Description", show=True),
        Binding("l", "show_logs", "Show Logs", show=True),
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

    .column-marker {
        width: 4;
        text-align: center;
    }

    .column-title {
        width: 20;
        margin-left: 1;
    }

    .column-description {
        width: 1fr;
        margin-left: 1;
        opacity: 0.8;
    }

    #footer {
        height: 2;
        background: $secondary;
        color: $text;
        border-top: heavy $accent;
        padding: 0 1;
    }

    #footer-left {
        width: 1fr;
        content-align: left middle;
    }

    #footer-right {
        width: auto;
        content-align: right middle;
    }
    """

    def __init__(self):
        super().__init__()
        logger.info("=== SkillListScreen initialized ===")
        self.available_skills = list_skills()
        self.installed = get_installed_skills(DESTINATION)
        self.selected_skills: Set[str] = set()
        logger.info(f"Available skills: {len(self.available_skills)}")
        logger.info(f"Installed skills: {self.installed}")
        logger.info(f"Destination: {DESTINATION}")

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

        # Footer with two columns
        from textual.containers import Horizontal

        with Container(id="footer"):
            with Horizontal():
                yield Static(self._get_footer_left(), id="footer-left")
                yield Static(self._get_footer_right(), id="footer-right")

    def _get_title(self) -> str:
        if self.selected_skills:
            install = len([s for s in self.selected_skills if s not in self.installed])
            remove = len([s for s in self.selected_skills if s in self.installed])
            return f"📦 Selected: {len(self.selected_skills)} (install: {install}, remove: {remove})"
        return f"📦 Skills Manager"

    def _get_header_info(self) -> str:
        return f"Available: {len(self.available_skills)} | Installed: {len(self.installed)}"

    def _get_footer_left(self) -> str:
        return "Space: Toggle  Enter: Apply  E: Description  L: Logs  Q: Quit"

    def _get_footer_right(self) -> str:
        return str(DESTINATION)

    def _get_footer(self) -> str:
        if not self.selected_skills:
            return f"Destination: {DESTINATION}\nSpace: Toggle  Enter: Apply  Esc: Clear  Q: Quit"

        install = len([s for s in self.selected_skills if s not in self.installed])
        remove = len([s for s in self.selected_skills if s in self.installed])
        return f"Selected: {len(self.selected_skills)} (install: {install}, remove: {remove})  |  Enter: Apply  Esc: Clear  Q: Quit"

    def action_toggle_skill(self) -> None:
        """Toggle the selected skill"""
        logger.debug("Action: toggle_skill")
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

                    logger.info(
                        f"Toggled skill: {skill_name}, selected={item.selected}"
                    )
                    # Update item display
                    self._update_item_display(item)
                    self._update_footer()
                    self._update_header()
        except Exception as e:
            logger.error(f"Error in toggle_skill: {e}", exc_info=True)

    def action_execute_install(self) -> None:
        """Execute the installation/removal of selected skills"""
        logger.info(f"Action: execute_install, selected={self.selected_skills}")
        debug_log = []

        if not self.selected_skills:
            logger.debug("No selected skills")
            return

        try:
            footer_left = self.query_one("#footer-left", Static)
            list_view = self.query_one(ListView)
            debug_log.append("Got footer_left and list_view")
            logger.debug("Got footer_left and list_view")
        except Exception as e:
            logger.error(f"Exception getting widgets: {e}", exc_info=True)
            return

        # Count what we're doing
        to_install = [s for s in self.selected_skills if s not in self.installed]
        to_remove = [s for s in self.selected_skills if s in self.installed]
        logger.info(f"to_install={to_install}, to_remove={to_remove}")
        debug_log.append(f"to_install={to_install}, to_remove={to_remove}")

        # Execute operations
        errors = []
        for skill_name in sorted(self.selected_skills):
            is_installed = skill_name in self.installed
            dest_path = DESTINATION / skill_name
            logger.debug(
                f"Processing {skill_name}: is_installed={is_installed}, type={type(skill_name)}"
            )

            try:
                logger.info(
                    f"Skill check: '{skill_name}' == 'superpowers.js'? {skill_name == 'superpowers.js'}"
                )
                if skill_name == "superpowers.js":
                    # Handle plugin script specially
                    if is_installed:
                        # Remove plugin symlink
                        logger.info(f"Removing plugin {skill_name}")
                        plugin_target = (
                            Path.home()
                            / ".config"
                            / "opencode"
                            / "plugin"
                            / "superpowers.js"
                        )
                        if plugin_target.exists():
                            plugin_target.unlink()
                            logger.info(f"✓ Removed plugin symlink: {plugin_target}")
                        else:
                            logger.warning(
                                f"Plugin symlink not found for removal: {plugin_target}"
                            )
                        debug_log.append(f"Removed plugin {skill_name}")
                    else:
                        # Install plugin symlink
                        logger.info(f"Installing plugin {skill_name}")
                        plugin_dir = Path.home() / ".config" / "opencode" / "plugin"
                        plugin_dir.mkdir(parents=True, exist_ok=True)

                        source = (
                            Path(__file__).parent
                            / ".opencode"
                            / "plugin"
                            / "superpowers.js"
                        )
                        target = plugin_dir / "superpowers.js"

                        # Check if source exists
                        if not source.exists():
                            error_msg = f"Source file not found: {source}. Please install superpowers first."
                            logger.error(f"✗ {error_msg}")
                            self.app.notify(
                                error_msg,
                                title="❌ Error",
                                severity="error",
                                timeout=6.0,
                            )
                            return

                        # Remove existing if any
                        if target.exists() or target.is_symlink():
                            target.unlink()

                        # Create symlink
                        target.symlink_to(source)
                        logger.info(
                            f"✓ Installed plugin {skill_name} -> {target} -> {source}"
                        )
                        debug_log.append(f"Installed plugin {skill_name}")

                        # Verify installation
                        if (
                            target.exists()
                            and target.is_symlink()
                            and target.readlink() == source
                        ):
                            logger.info(
                                f"✓ Verification: symlink exists and points to correct target"
                            )
                            success_msg = f"Plugin installed: {target} -> {source}"
                        else:
                            logger.error(
                                f"✗ Verification failed: symlink not created properly"
                            )
                            success_msg = f"Plugin installed but verification failed"

                        # Show success notification
                        self.app.notify(
                            success_msg,
                            title="✅ Success",
                            severity="information",
                            timeout=6.0,
                        )
                        target = plugin_dir / "superpowers.js"

                        # Remove existing if any
                        if target.exists() or target.is_symlink():
                            target.unlink()

                        # Create symlink
                        target.symlink_to(source)
                        logger.info(
                            f"✓ Installed plugin {skill_name} -> {target} -> {source}"
                        )
                        debug_log.append(f"Installed plugin {skill_name}")

                        # Verify installation
                        if target.exists() and target.is_symlink():
                            logger.info(f"✓ Verification: symlink exists and is valid")
                            success_msg = f"Plugin installed: {target} -> {source}"
                        else:
                            logger.error(
                                f"✗ Verification failed: symlink not created properly"
                            )
                            success_msg = f"Plugin installed but verification failed"

                        # Show success notification with details
                        self.app.notify(
                            success_msg,
                            title="✅ Success",
                            severity="information",
                            timeout=6.0,
                        )
                else:
                    # Handle regular skills
                    if is_installed:
                        # Remove
                        logger.info(f"Removing {skill_name}")
                        shutil.rmtree(dest_path)
                        debug_log.append(f"Removed {skill_name}")
                    else:
                        # Install
                        logger.info(f"Installing {skill_name}")
                        source_dir = next(
                            (
                                s.path
                                for s in self.available_skills
                                if s.dir_name == skill_name
                            ),
                            None,
                        )
                        if not source_dir:
                            logger.warning(f"Source not found for {skill_name}")
                            debug_log.append(f"Source not found for {skill_name}")
                            continue
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        # Ensure destination directory exists
                        DESTINATION.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(source_dir, dest_path)
                        logger.info(f"✓ Installed {skill_name}")
                        debug_log.append(f"Installed {skill_name}")
            except Exception as e:
                logger.error(f"Error with {skill_name}: {e}", exc_info=True)
                debug_log.append(f"Error with {skill_name}: {e}")
                errors.append(f"{skill_name}: {str(e)}")

        if errors:
            msg = f"Error: {errors[0][:40]}"
            logger.error(f"Installation failed: {errors}")
            self.notify(msg, title="❌ Failed", severity="error", timeout=4.0)
            return

        # Update state
        self.installed = get_installed_skills(DESTINATION)
        logger.info(f"Updated installed: {self.installed}")

        # Clear selections and refresh display
        try:
            list_view = self.query_one(ListView)
            for i, item in enumerate(list_view.children):
                if isinstance(item, SkillItem):
                    item.selected = False
                    item.is_installed = item.skill.dir_name in self.installed
                    self._update_item_display(item)
                    logger.debug(f"Updated item {i}: {item.skill.dir_name}")
        except Exception as e:
            logger.error(f"Exception updating items: {e}", exc_info=True)

        self.selected_skills.clear()
        self._update_header()

        # Show success notification
        if to_install and to_remove:
            msg = f"Installed {len(to_install)}, Removed {len(to_remove)}"
        elif to_install:
            msg = (
                f"Installed {len(to_install)} skill{'s' if len(to_install) > 1 else ''}"
            )
        else:
            msg = f"Removed {len(to_remove)} skill{'s' if len(to_remove) > 1 else ''}"

        logger.info(f"Success: {msg}")
        self.notify(msg, title="✅ Success", severity="information", timeout=6.0)

        # Also update header to show new count
        try:
            header_info = self.query_one("#header-info", Label)
            header_info.update(self._get_header_info())
            debug_log.append("Header updated")
        except Exception as e:
            debug_log.append(f"Exception updating header: {e}")

        # Write final debug log
        with open("/tmp/skills_install.log", "w") as f:
            f.write("\n".join(debug_log))

    def _update_item_display(self, item: SkillItem) -> None:
        """Update the display of a skill item"""
        # Rebuild the formatted text
        text = item._format_skill_text()

        # Update the label
        label = item.children[0]
        if isinstance(label, Label):
            label.update(text)

    def _update_footer(self) -> None:
        """Update the footer messages"""
        try:
            footer_left = self.query_one("#footer-left", Static)
            footer_left.update(self._get_footer_left())
        except Exception:
            pass

    def _update_header(self) -> None:
        """Update the header messages"""
        try:
            header_title = self.query_one("#header-title", Label)
            header_title.update(self._get_title())
        except Exception:
            pass

    def action_show_description(self) -> None:
        """Show description of currently selected skill in a modal overlay"""
        try:
            list_view = self.query_one(ListView)
            if list_view.index is not None:
                item = list_view.children[list_view.index]
                if isinstance(item, SkillItem):
                    # Create and show modal overlay
                    modal = DescriptionModal(item.skill)
                    self.app.push_screen(modal)
        except Exception as e:
            logger.error(f"Error showing description: {e}")

    def action_show_logs(self) -> None:
        """Show recent log entries in a modal"""
        try:
            modal = LogModal()
            self.app.push_screen(modal)
        except Exception as e:
            logger.error(f"Error showing logs: {e}")

    def action_quit(self) -> None:
        logger.info("Action: quit")
        self.app.exit()

    def on_key(self, event) -> None:
        """Log all key presses and handle Enter manually"""
        logger.debug(f"Key pressed: {event.key}")

        # Handle Enter key manually since ListView consumes it
        if event.key == "enter":
            logger.debug("Enter key detected, calling action_execute_install")
            self.action_execute_install()
            event.prevent_default()


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


if __name__ == "__main__":
    app = InstallerApp()
    app.run()
