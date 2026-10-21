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

The latest `vX.Y.Z` tag is the source of truth. [`VERSION`](VERSION) is updated from it automatically. `1.2.0` is the published baseline. Release notes are in [`CHANGELOG.md`](CHANGELOG.md) and on [GitHub Releases](https://github.com/ederheisler/agent-skills/releases).

Only changes under `skills/**` release, including prose edits. Breaking changes (`type!:` or a `BREAKING CHANGE:` trailer) bump major, `feat:` bumps minor, and everything else bumps patch. The highest bump wins. For example, `1.2.0` becomes `2.0.0`, `1.3.0`, or `1.2.1`. Root docs, CI, `VERSION`, and metadata commits do not release or tag. Changes that are made and then reverted do not release. The workflow can run on every push to `main`, but it does nothing without a net skill change. Queued pushes share one release. No manual release step or npm publication is needed. The full schema is in [`RELEASES.md`](RELEASES.md).

Each skill keeps its own version in its own metadata. These versions do not depend on the repository version.

The `skills` CLI decides updates from the content of each installed skill, not from `VERSION`, a skill version, a tag, or a GitHub Release. A normal install follows the source branch. An install pinned to a ref stays on that ref. Tags and releases are for tracking and pinning. `skills update` does not need them. See [`update.ts`](https://github.com/vercel-labs/skills/blob/main/src/update.ts) and the [upstream documentation](https://github.com/vercel-labs/skills#readme).

## License

MIT, see [LICENSE](LICENSE).
