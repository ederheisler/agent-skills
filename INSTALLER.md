# Skills Installer

An interactive TUI installer for managing OpenCode skills using [Textual](https://textual.textualize.io/).

## Features

- **Responsive keyboard navigation** - Arrow keys, Space, Enter
- **Multiple destinations** - Global, OpenCode, or Claude installations
- **Live status** - See which skills are installed
- **Batch operations** - Select multiple skills to install/remove at once
- **Keyboard-only** - No mouse required (can use mouse with Textual but not needed)

## Installation

The installer requires `textual`:

```bash
# Using uv (recommended)
uv pip install textual

# Or using pip in a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install textual
```

## Usage

### Quick Start

```bash
# Method 1: Direct Python (if textual is installed)
python3 install.py

# Method 2: Using uv run (recommended, installs dependencies automatically)
uv run --with textual python3 install.py

# Method 3: Using Textual CLI
textual run install.py:app
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate up/down |
| `Space` | Toggle selection |
| `Enter` | Apply selections (install/remove) |
| `Esc` | Clear all selections |
| `Q` | Quit |
| `Ctrl+C` | Emergency quit |

### Workflow

1. **Select Destination** - Choose where to install skills:
   - Global: `~/.config/opencode/skill/`
   - OpenCode: `./.opencode/skill/`
   - Claude: `./.claude/skills/`

2. **Select Skills** - Use `↑`/`↓` and `Space` to select skills
   - `[✓]` = Already installed
   - `[ ]` = Not installed
   - Selected skills will be highlighted

3. **Apply** - Press `Enter` to install/remove selected skills

4. **Review** - Status bar shows counts and completion

## Skill Metadata

Each skill should have a `SKILL.md` file with frontmatter:

```yaml
---
name: My Skill
description: A brief description
---

# Skill content...
```

The installer extracts `name` and `description` from the frontmatter to display in the TUI.

## Destination Paths

### Global Skills (~/.config/opencode/skill/)

Installed globally for all OpenCode projects. Requires creating the directory structure.

### OpenCode Skills (.opencode/skill/)

Project-specific skills for OpenCode installations.

### Claude Skills (.claude/skills/)

Project-specific skills for Claude Code installations.

## Troubleshooting

### "No skills found in repository"

Make sure you're running the installer from the repository root with a `skills/` directory containing skill folders.

### Textual not found

Install textual:

```bash
uv pip install textual
# OR
python3 -m pip install textual
```

### Terminal display issues

Ensure your terminal supports 256 colors:

```bash
echo $TERM  # Should output something like xterm-256color or similar
```

### Slow keyboard response

This is normal in some terminal emulators. Try a different terminal or SSH client if available.

## Implementation Details

The installer is built with:

- **Textual Framework** - Modern TUI framework for Python
- **SelectionList** - For keyboard-navigable skill selection
- **Screen system** - Separate destination and skill selection screens
- **Keyboard-only design** - No mouse input required

See the source code (`install.py`) for implementation details and to customize behavior.
