# Quick Setup for OpenCode

## One-line installation

Replace `/path/to/your/skills/folder` with the actual path to this repository:

```bash
mkdir -p ~/.config/opencode/plugin && ln -sf /path/to/your/skills/folder/.opencode/plugin/superpowers.js ~/.config/opencode/plugin/superpowers.js
```

## Example (if this repo is at `/Users/eder/Code/skills`)

```bash
mkdir -p ~/.config/opencode/plugin && ln -sf /Users/eder/Code/skills/.opencode/plugin/superpowers.js ~/.config/opencode/plugin/superpowers.js
```

## Verify installation

```bash
readlink ~/.config/opencode/plugin/superpowers.js
```

Should point to the `superpowers.js` file in this repository.

## Restart OpenCode

After creating the symlink, restart OpenCode for the plugin to load.

## Check it works

In a new OpenCode session, ask: "do you have superpowers?"

## More details

See [INSTALL.md](INSTALL.md) for full documentation and troubleshooting.
