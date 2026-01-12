# Promoting Entries to Project Memory

Guidelines for elevating learnings from `.learnings/` to permanent project documentation.

## When to Promote

Promote a learning when it's broadly applicable:

- **Applies across multiple files/features** - Not a one-off fix
- **Knowledge any contributor should know** - Human or AI
- **Prevents recurring mistakes** - Seen the issue multiple times
- **Documents project-specific conventions** - Not general knowledge

## Promotion Targets

| Target | What Belongs There |
|--------|--------------------|
| `AGENTS.md` | Agent-specific workflows, tool usage patterns, automation rules |
| `CLAUDE.md` | Project conventions, architecture decisions, context for humans & AI |

Choose based on audience:

- **AGENTS.md**: Instructions for AI agents performing automated tasks
- **CLAUDE.md**: Context for any contributor (human or AI) working on the project

## How to Promote

### Step 1: Distill the Learning

Transform the verbose learning into a concise, actionable rule.

**Before (in LEARNINGS.md)**:

```markdown
## [LRN-20250115-002] knowledge_gap

### Details
Attempted to run `npm install` but project uses pnpm workspaces.
Lock file is `pnpm-lock.yaml`, not `package-lock.json`.
User had to correct me.

### Suggested Action
Check for `pnpm-lock.yaml` or `pnpm-workspace.yaml` before assuming npm.
Use `pnpm install` for this project.
```text

**After (in CLAUDE.md)** - concise:

```markdown
## Build & Dependencies
- Package manager: pnpm (not npm) - use `pnpm install`
```

### Step 2: Add to Target File

Insert into the appropriate section, or create a new section if needed.

**For AGENTS.md** - focus on workflow:

```markdown
## After API Changes
1. Regenerate client: `pnpm run generate:api`
2. Check for type errors: `pnpm tsc --noEmit`
```text

**For CLAUDE.md** - focus on context:

```markdown
## API Architecture
- Uses OpenAPI spec in `openapi.yaml`
- TypeScript client is auto-generated (don't edit `src/client/api.ts` manually)
- Regenerate after spec changes: `pnpm run generate:api`
```

### Step 3: Update Original Entry

Mark the learning as promoted:

1. Change `**Status**: pending` → `**Status**: promoted`
2. Add promotion reference:

   ```markdown
   **Promoted**: CLAUDE.md
   ```

Example:

```markdown
## [LRN-20250115-002] knowledge_gap

**Logged**: 2025-01-15T14:22:00Z
**Priority**: medium
**Status**: promoted
**Promoted**: CLAUDE.md
**Area**: config

[... rest of entry ...]
```text

## Promotion Examples

### Example 1: Build Tooling

**Original Learning**:
> Project uses pnpm workspaces. Attempted `npm install` but failed.
> Lock file is `pnpm-lock.yaml`. Must use `pnpm install`.

**Promoted to CLAUDE.md**:

```markdown
## Build & Dependencies
- Package manager: pnpm (not npm) - use `pnpm install`
```

**Why promoted**: Any contributor needs this immediately; prevents recurring confusion.

---

### Example 2: API Workflow

**Original Learning**:
> When modifying API endpoints, must regenerate TypeScript client.
> Forgetting this causes type mismatches at runtime.

**Promoted to AGENTS.md**:

```markdown
## After API Changes
1. Regenerate client: `pnpm run generate:api`
2. Check for type errors: `pnpm tsc --noEmit`
```text

**Why promoted**: Recurring workflow that agents should follow automatically.

---

### Example 3: Architecture Context

**Original Learning**:
> All API responses must include correlation ID from request headers
> for distributed tracing. Responses without this break observability.

**Promoted to CLAUDE.md**:

```markdown
## API Conventions
- All responses must echo `X-Correlation-ID` from request headers
- Required for distributed tracing (breaks observability pipeline if missing)
```

**Why promoted**: Architectural constraint that affects all API development.

---

## What NOT to Promote

Don't promote if:

- **One-off fix**: Specific to a single file/function
- **Already documented**: Information exists in official docs
- **Too specific**: Only relevant to one edge case
- **Temporary**: Workaround that will be removed

Instead:

- Keep in `.learnings/` as historical reference
- Mark as `resolved` when fixed
- Add `wont_fix` if not worth promoting

## Maintenance

### Periodic Cleanup

When reviewing `.learnings/`:

- Promote high-value entries that have aged well
- Archive old resolved entries
- Update promoted entries if project changes

### Avoid Duplication

Before promoting:

1. Search target file for similar content
2. Update existing section instead of adding redundant entry
3. Link related promoted entries with cross-references

---

## See Also

- [references/formats.md](formats.md) - Entry format specifications
- [references/examples.md](examples.md) - Example entries with promotion notes
