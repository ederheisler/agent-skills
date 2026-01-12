# Installing Superpowers for OpenCode (Local Setup)

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- Node.js installed
- Git installed

## Installation Steps

### Option 1: From Local Folder

If you have the superpowers skills in a local folder (like this repository):

```bash
# 1. Create plugin directory
mkdir -p ~/.config/opencode/plugin

# 2. Create symlink to plugin from local folder
ln -sf /path/to/your/skills/folder/.opencode/plugin/superpowers.js ~/.config/opencode/plugin/superpowers.js

# Replace /path/to/your/skills/folder with the actual path to your skills directory
```

### Option 2: From GitHub Repository

```bash
# 1. Create directories
mkdir -p ~/.config/opencode/superpowers
mkdir -p ~/.config/opencode/plugin

# 2. Clone repository
git clone https://github.com/obra/superpowers.git ~/.config/opencode/superpowers

# 3. Create symlink to plugin
ln -sf ~/.config/opencode/superpowers/.opencode/plugin/superpowers.js ~/.config/opencode/plugin/superpowers.js
```

### 3. Restart OpenCode

Restart OpenCode. The plugin will automatically inject superpowers context via the chat.message hook.

You should see superpowers is active when you ask "do you have superpowers?"

## Usage

### Finding Skills

Use the `find_skills` tool to list all available skills:

```text
use find_skills tool
```

### Loading a Skill

Use the `use_skill` tool to load a specific skill:

```text
use use_skill tool with skill_name: "superpowers:brainstorming"
```

### Personal Skills

Create your own skills in `~/.config/opencode/skills/`:

```bash
mkdir -p ~/.config/opencode/skills/my-skill
```

Create `~/.config/opencode/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Use when [condition] - [what it does]
---

# My Skill

[Your skill content here]
```

Personal skills override superpowers skills with the same name.

### Project Skills

Create project-specific skills in your OpenCode project:

```bash
# In your OpenCode project
mkdir -p .opencode/skill/my-project-skill
```

Create `.opencode/skill/my-project-skill/SKILL.md`:

```markdown
---
name: my-project-skill
description: Use when [condition] - [what it does]
---

# My Project Skill

[Your skill content here]
```

**Skill Priority:** Project skills override personal skills, which override superpowers skills.

**Skill Naming:**

- `project:skill-name` - Force project skill lookup (checks .opencode/skill/ and .claude/skills/)
- `skill-name` - Searches project → personal → superpowers
- `superpowers:skill-name` - Force superpowers skill lookup

## Using This Skills Collection Locally

This repository contains the skills collection. When using this with the local setup:

1. **Current directory skills**: Skills in this directory will be available as `superpowers:skill-name`
2. **Plugin**: The plugin file is at `.opencode/plugin/superpowers.js` and references `../../skills` for the skills directory
3. **Personal skills**: Can be added to `~/.config/opencode/skills/` and will override skills in this directory
4. **Project skills**: Can be added to any project's `.opencode/skill/` or `.claude/skills/` directory

## Updating

### From Local Folder

If you're using a local folder, just update the folder contents (e.g., pull from git).

### From GitHub Repository

```bash
cd ~/.config/opencode/superpowers
git pull
```

## Troubleshooting

### Plugin not loading

1. Check plugin file exists: `ls ~/.config/opencode/plugin/superpowers.js`
2. Check if symlink is broken: `readlink ~/.config/opencode/plugin/superpowers.js`
3. Check OpenCode logs for errors
4. Verify Node.js is installed: `node --version`

### Skills not found

1. Verify skills directory exists relative to plugin: The plugin expects `skills/` directory at `../../skills` from its location
2. Use `find_skills` tool to see what's discovered
3. Check file structure: each skill should have a `SKILL.md` file

### Tool mapping issues

When a skill references a Claude Code tool you don't have:

- `TodoWrite` → use `update_plan`
- `Task` with subagents → use `@mention` syntax to invoke OpenCode subagents
- `Skill` → use `use_skill` tool
- File operations → use your native tools

### Wrong skills path

If the plugin can't find the skills directory:

1. Verify the symlink points to the correct `superpowers.js` file
2. Check that the skills directory is at the correct relative path from the plugin
3. For local setups, ensure your directory structure is:

   ```text
   /path/to/skills/
   ├── .opencode/
   │   └── plugin/
   │       └── superpowers.js
   ├── skills/
   │   ├── brainstorming/
   │   ├── test-driven-development/
   │   └── ...
   └── lib/
       └── skills-core.js
   ```

## Getting Help

- Report issues: <https://github.com/obra/superpowers/issues>
- Documentation: <https://github.com/obra/superpowers>
