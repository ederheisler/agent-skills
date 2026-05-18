#!/usr/bin/env python3
"""
Interactive TUI installer for OpenCode skills using Textual.

Run with: uv run --with textual python3 skills_manager.py

Keyboard controls:
- ↑/↓: Navigate
- Space: Toggle selection
- U: Update all installed
- Enter: Apply selections
- Esc: Clear selections
- Q: Quit
"""

from src.app import InstallerApp

if __name__ == "__main__":
    app = InstallerApp()
    app.run()
