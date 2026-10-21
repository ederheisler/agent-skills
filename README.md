# agent-skills

Agent skills published by Eder Heisler. Install with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```sh
npx skills add ederheisler/agent-skills --list
npx skills add ederheisler/agent-skills --skill graphify-setup -g
npx skills update
```

## Skills

| Skill | Purpose |
|---|---|
| `graphify-setup` | Set up, migrate, and merge-manage Graphify in a repository. |
| `wtf` | Explains the agent's last response when you invoke `/wtf`: missing rationale, context, terms, and corrections. |

## Releases

The repository version is in [`VERSION`](VERSION). Release notes are in [`CHANGELOG.md`](CHANGELOG.md) and on [GitHub Releases](https://github.com/ederheisler/agent-skills/releases).

Pushes to `main` release automatically, except changes limited to `VERSION` and `CHANGELOG.md`. The first release is `1.2.0`. Later releases increment the patch number. Queued pushes can share a release. No manual release step or npm publication is needed.

Each skill keeps its own version in its own metadata. These versions do not depend on the repository version.

The `skills` CLI decides updates from the content of each installed skill, not from `VERSION`, a skill version, a tag, or a GitHub Release. A normal install follows the source branch. An install pinned to a ref stays on that ref. Tags and releases are for tracking and pinning. `skills update` does not need them. See [`update.ts`](https://github.com/vercel-labs/skills/blob/main/src/update.ts) and the [upstream documentation](https://github.com/vercel-labs/skills#readme).

## License

MIT, see [LICENSE](LICENSE).
