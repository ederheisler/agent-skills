"""
Interactive TUI screens for skills manager.
"""

from pathlib import Path
from typing import Set

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from .. import plugin
from ..config import LOG_FILE, logger
from ..models import SkillInfo
from ..persistence import get_last_destination, set_last_destination
from ..skills import get_installed_skills, install_skill, load_skills, remove_skill
from .widgets import DescriptionModal, LogModal, SkillItem


class DirListItem(ListItem):
    """ListItem with directory name stored"""

    def __init__(self, label: Label, dir_name: str):
        super().__init__(label)
        self.dir_name = dir_name
        logger.info(f"DirListItem created: dir_name={dir_name}")


class DirectoryBrowserScreen(Screen):
    """Screen for browsing directories to select skills source"""

    BINDINGS = [
        Binding("enter", "select_directory", "Enter Dir", show=True),
        Binding("b", "select_current", "Select Current", show=True),
        Binding("h", "toggle_hidden", "Toggle Hidden", show=True),
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    CSS = """
    DirectoryBrowserScreen {
        layout: vertical;
        background: $surface;
    }

    #browser-header {
        height: 3;
        background: $primary;
        color: $text;
        border-bottom: heavy $accent;
        padding: 1;
    }

    #browser-title {
        width: 1fr;
        text-style: bold;
        color: $text;
    }

    #current-path {
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

    #browser-footer {
        height: 2;
        background: $secondary;
        color: $text;
        border-top: heavy $accent;
        padding: 0 1;
    }
    """

    def __init__(self, current_dir: Path):
        super().__init__()
        self.current_dir = current_dir
        self.selected_path = None
        self.show_hidden = False
        logger.info(f"DirectoryBrowserScreen initialized with: {current_dir}")

    def on_mount(self) -> None:
        logger.info(f"DirectoryBrowserScreen mounted, current_dir={self.current_dir}")

    def on_key(self, event) -> None:
        """Handle Enter manually since ListView consumes it"""
        logger.info(f"DirectoryBrowserScreen key pressed: {event.key}")

        # Handle Enter key manually since ListView consumes it
        if event.key == "enter":
            self.action_select_directory()
            event.prevent_default()
            return

        # Log current focus for debugging
        list_view = self.query_one("#dir-list", ListView)
        if list_view.index is not None:
            logger.info(
                f"Current focus index: {list_view.index}, total items: {len(list_view.children)}"
            )
            if list_view.index < len(list_view.children):
                item = list_view.children[list_view.index]
                if isinstance(item, DirListItem):
                    logger.info(f"Focused item: {item.dir_name}")
                else:
                    logger.info(f"Focused item type: {type(item)}")

    def compose(self) -> ComposeResult:
        with Container(id="browser-header"):
            yield Label("Browse Destination Directory", id="browser-title")
            yield Label(f"Current: {self.current_dir}", id="current-path")

        with ListView(id="dir-list"):
            # Add parent directory if not root
            if self.current_dir != self.current_dir.parent:
                yield DirListItem(Label(".. (Parent Directory)"), "..")

            # List subdirectories
            if self.current_dir.exists():
                for item in sorted(self.current_dir.iterdir()):
                    if item.is_dir() and (
                        self.show_hidden or not item.name.startswith(".")
                    ):
                        yield DirListItem(Label(item.name), item.name)

        with Container(id="browser-footer"):
            yield Static(
                "Enter: Enter Dir  H: Toggle Hidden  B: Select Current  Esc: Cancel",
                id="footer",
            )

    def _populate_list(self) -> None:
        """Populate the directory list"""
        logger.info(
            f"_populate_list called for: {self.current_dir}, show_hidden={self.show_hidden}"
        )
        list_view = self.query_one("#dir-list", ListView)
        list_view.clear()

        # Add parent directory if not root
        if self.current_dir != self.current_dir.parent:
            list_view.append(DirListItem(Label(".. (Parent Directory)"), ".."))
            logger.info("Added parent directory item")

        # List subdirectories
        if self.current_dir.exists():
            dirs = sorted(
                [
                    item
                    for item in self.current_dir.iterdir()
                    if item.is_dir()
                    and (self.show_hidden or not item.name.startswith("."))
                ]
            )
            logger.info(
                f"Found {len(dirs)} subdirectories (show_hidden={self.show_hidden})"
            )
            for item in dirs:
                list_view.append(DirListItem(Label(item.name), item.name))
                logger.info(f"Added directory: {item.name}")
        else:
            logger.warning(f"Directory does not exist: {self.current_dir}")

    def _update_header(self) -> None:
        """Update the current path display"""
        self.query_one("#current-path", Label).update(f"Current: {self.current_dir}")

    def action_select_directory(self) -> None:
        """Enter the current highlighted directory"""
        list_view = self.query_one("#dir-list", ListView)
        logger.info(
            f"action_select_directory: index={list_view.index}, children={len(list_view.children)}"
        )
        if list_view.index is not None and list_view.index < len(list_view.children):
            item = list_view.children[list_view.index]
            logger.info(
                f"Selected item type: {type(item)}, is DirListItem: {isinstance(item, DirListItem)}"
            )
            if isinstance(item, DirListItem):
                name = item.dir_name
                logger.info(f"Navigating to: {name}")

                if name == "..":
                    # Navigate to parent
                    self.current_dir = self.current_dir.parent
                else:
                    # Navigate into subdirectory
                    self.current_dir = self.current_dir / name

                logger.info(f"New current_dir: {self.current_dir}")
                # Refresh the list and header
                self._populate_list()
                self._update_header()

    def action_select_current(self) -> None:
        """Select the current directory as destination"""
        logger.info(f"action_select_current called, selecting: {self.current_dir}")
        self.selected_path = self.current_dir
        logger.info(f"Dismissing screen with selected_path: {self.selected_path}")
        self.dismiss(self)

    def action_toggle_hidden(self) -> None:
        """Toggle visibility of hidden files"""
        self.show_hidden = not self.show_hidden
        logger.info(f"Toggled show_hidden to: {self.show_hidden}")
        self._populate_list()

    def action_cancel(self) -> None:
        """Cancel browsing"""
        logger.info("action_cancel called")
        self.selected_path = None
        logger.info("Dismissing screen with selected_path: None")
        self.dismiss(None)


class SkillListScreen(Screen):
    """Main screen for selecting and installing skills"""

    BINDINGS = [
        Binding("space", "toggle_skill", "Toggle", show=True),
        Binding("enter", "execute_install", "Apply", show=True),
        Binding("e", "show_description", "Description", show=True),
        Binding("l", "show_logs", "Show Logs", show=True),
        Binding("u", "reinstall_all", "Update All", show=True),
        Binding("b", "browse_source", "Browse Destination", show=True),
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
        self.skills_dir = Path("skills")

        # Load last destination from persistence, or use default
        last_dest = get_last_destination()
        if last_dest and last_dest.exists():
            self.destination = last_dest
            logger.info(f"Loaded last destination: {self.destination}")
        else:
            self.destination = Path.home() / ".claude" / "skills"  # default
            logger.info(f"Using default destination: {self.destination}")

        self.available_skills = load_skills(self.skills_dir)
        self.installed = get_installed_skills(self.destination)
        self.selected_skills: Set[str] = set()
        self.reinstall_mode: Set[str] = set()  # Track skills marked for reinstall
        logger.info(f"Available skills: {len(self.available_skills)}")
        logger.info(f"Installed skills: {self.installed}")
        logger.info(f"Destination: {self.destination}")

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
        with Container(id="footer"):
            with Horizontal():
                yield Static(self._get_footer_left(), id="footer-left")
                yield Static(self._get_footer_right(), id="footer-right")

    def _get_title(self) -> str:
        if self.selected_skills:
            install = len([s for s in self.selected_skills if s not in self.installed])
            remove = len([s for s in self.selected_skills if s in self.installed])
            return f"📦 Selected: {len(self.selected_skills)} (install: {install}, remove: {remove})"
        return "📦 Skills Manager"

    def _get_header_info(self) -> str:
        return f"Available: {len(self.available_skills)} | Installed: {len(self.installed)}"

    def _get_footer_left(self) -> str:
        return "Space: Toggle  U: Update All Installed  B: Browse Destination  Enter: Apply  E: Description  L: Logs  Q: Quit"

    def _get_footer_right(self) -> str:
        return str(self.destination)

    def _get_footer(self) -> str:
        if not self.selected_skills:
            return f"Destination: {self.destination}\nSpace: Toggle  Enter: Apply  Esc: Clear  Q: Quit"

        install = len([s for s in self.selected_skills if s not in self.installed])
        remove = len([s for s in self.selected_skills if s in self.installed])
        return f"Selected: {len(self.selected_skills)} (install: {install}, remove: {remove})  |  Enter: Apply  Esc: Clear  Q: Quit"

    def _find_skill(self, dir_name: str) -> SkillInfo | None:
        """Find a skill by directory name"""
        return next(
            (s for s in self.available_skills if s.dir_name == dir_name),
            None,
        )

    def action_reinstall_all(self) -> None:
        """Reinstall all installed skills immediately"""
        logger.info("Action: reinstall_all - reinstalling all installed skills")

        # Refresh installed list first
        self.installed = get_installed_skills(self.destination)

        installed_names = self.installed
        if not installed_names:
            self.notify("No installed skills to update", severity="warning")
            return

        self.notify(
            "Updating...",
            title="Update Started",
            severity="information",
        )

        errors = []
        skill_success_count = 0
        plugin_success_count = 0

        # Iterate over all available skills to find the ones that are installed
        for skill in self.available_skills:
            if skill.dir_name in installed_names:
                try:
                    if skill.is_plugin:
                        logger.info(f"Reinstalling plugin {skill.name}")
                        plugin.remove_plugin(skill)  # type: ignore[arg-type]
                        plugin.install_plugin(skill)  # type: ignore[arg-type]
                        plugin_success_count += 1
                    else:
                        logger.info(f"Reinstalling skill {skill.name}")
                        if install_skill(skill, self.destination):
                            skill_success_count += 1
                        else:
                            errors.append(f"{skill.name}: installation failed")
                except Exception as e:
                    logger.error(f"Failed to update {skill.name}: {e}")
                    errors.append(f"{skill.name}: {e}")

        # Refresh state
        self.refresh_installed_status()

        # Show results
        if errors:
            error_details = "\n".join(errors)
            logger.error(f"Update failed for {len(errors)} items:\n{error_details}")
            total_success = skill_success_count + plugin_success_count
            self.notify(
                f"Updated {total_success} items.\n\nFailed:\n{error_details}",
                title="Update Complete with Errors",
                severity="error",
                timeout=10.0,
            )
        else:
            parts = []
            if skill_success_count > 0:
                parts.append(
                    f"{skill_success_count} skill{'s' if skill_success_count != 1 else ''}"
                )
            if plugin_success_count > 0:
                parts.append(
                    f"{plugin_success_count} plugin{'s' if plugin_success_count != 1 else ''}"
                )
            msg = (
                f"Successfully updated {' + '.join(parts)}"
                if parts
                else "No updates needed (or installed items not found in source)"
            )
            self.notify(
                msg,
                title="Update Complete",
                severity="information",
                timeout=3.0,
            )

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

    def refresh_installed_status(self):
        """Update the installed status of all items"""
        self.installed = get_installed_skills(self.destination)
        try:
            list_view = self.query_one(ListView)
            for item in list_view.children:
                if isinstance(item, SkillItem):
                    item.is_installed = item.skill.dir_name in self.installed
                    self._update_item_display(item)
        except Exception as e:
            logger.error(f"Error updating UI: {e}", exc_info=True)

    def action_execute_install(self) -> None:
        """Execute the installation/removal of selected skills"""
        logger.info(f"Action: execute_install, selected={self.selected_skills}")

        if not self.selected_skills:
            return

        try:
            self.query_one(ListView)
        except Exception as e:
            logger.error(f"Exception getting widgets: {e}", exc_info=True)
            return

        # Prepare lists
        to_process = sorted(self.selected_skills)
        errors = []
        success_count = 0

        for skill_dir_name in to_process:
            skill = self._find_skill(skill_dir_name)
            if not skill:
                logger.warning(f"Skill not found: {skill_dir_name}")
                continue

            is_installed = skill_dir_name in self.installed
            is_reinstall = skill_dir_name in self.reinstall_mode

            should_remove = is_installed and not is_reinstall

            try:
                if skill.is_plugin:
                    if should_remove:
                        logger.info(f"Removing plugin {skill.name}")
                        plugin.remove_plugin(skill)  # type: ignore[arg-type]
                        success_count += 1
                    else:
                        logger.info(f"Installing plugin {skill.name}")
                        plugin.install_plugin(skill)  # type: ignore[arg-type]
                        success_count += 1
                else:
                    if should_remove:
                        logger.info(f"Removing skill {skill.name}")
                        if remove_skill(skill, self.destination):
                            success_count += 1
                        else:
                            errors.append(f"{skill.name}: delete failed")
                    else:
                        logger.info(f"Installing skill {skill.name}")
                        if install_skill(skill, self.destination):
                            success_count += 1
                        else:
                            errors.append(f"{skill.name}: install failed")

            except Exception as e:
                logger.error(f"Error processing {skill.name}: {e}")
                errors.append(f"{skill.name}: {e}")

        # Update UI
        self.refresh_installed_status()
        self.selected_skills.clear()
        self.reinstall_mode.clear()
        self._update_header()

        if errors:
            self.notify("Errors:\n" + "\n".join(errors), severity="error")
        else:
            self.notify(
                f"Success! Processed {success_count} items.", severity="information"
            )

    def _update_item_display(self, item: SkillItem) -> None:
        """Update the display of a single item"""
        item.refresh_display()

    def _update_header(self) -> None:
        self.query_one("#header-title", Label).update(self._get_title())
        self.query_one("#header-info", Label).update(self._get_header_info())

    def _update_footer(self) -> None:
        self.query_one("#footer-left", Static).update(self._get_footer_left())
        self.query_one("#footer-right", Static).update(self._get_footer_right())

    def action_show_description(self) -> None:
        """Show the description of the selected skill"""
        list_view = self.query_one(ListView)
        if list_view.index is not None and list_view.index < len(list_view.children):
            item = list_view.children[list_view.index]
            if isinstance(item, SkillItem):
                self.app.push_screen(DescriptionModal(item.skill))

    def action_show_logs(self) -> None:
        """Show the logs"""
        log_content = ""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, "r") as f:
                    log_content = f.read()
            else:
                log_content = "Log file not found."
        except Exception as e:
            log_content = f"Error reading logs: {e}"

        self.app.push_screen(LogModal(log_content))

    def action_browse_source(self) -> None:
        """Browse for a destination directory"""
        logger.info("action_browse_source called")

        # Start from the parent of the current destination if it exists
        # Otherwise fall back to ~/Code or ~
        if self.destination.exists():
            # Go up from ~/.claude/skills to the project root
            start_dir = self.destination.parent.parent
            logger.info(
                f"Starting from current destination's project root: {start_dir}"
            )
        else:
            start_dir = Path.home() / "Code"
            if not start_dir.exists():
                start_dir = Path.home()
            logger.info(f"Starting from default: {start_dir}")

        logger.info(f"Opening DirectoryBrowserScreen with start_dir: {start_dir}")
        browser = DirectoryBrowserScreen(start_dir)

        def check_selection(result: DirectoryBrowserScreen | None) -> None:
            logger.info(f"check_selection callback: result={result}")
            if result and result.selected_path:
                logger.info(f"Selected path: {result.selected_path}")
                self.destination = result.selected_path / ".claude" / "skills"
                logger.info(f"New destination: {self.destination}")

                # Save the destination to persistence
                set_last_destination(self.destination)

                self.installed = get_installed_skills(self.destination)
                self.selected_skills.clear()
                self.reinstall_mode.clear()
                self.refresh_installed_status()
                self._update_header()
                self._update_footer()
            else:
                logger.info("No path selected or result is None")

        self.app.push_screen(browser, check_selection)

    def action_quit(self) -> None:
        logger.info("Action: quit")
        self.app.exit()

    def on_key(self, event) -> None:
        """Handle Enter manually"""
        # Handle Enter key manually since ListView consumes it
        if event.key == "enter":
            self.action_execute_install()
            event.prevent_default()
