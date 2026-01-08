# Entry Format Templates

Detailed format specifications for all entry types. Use these templates when creating new entries.

## Table of Contents

- [Learning Entry Format](#learning-entry-format)
- [Error Entry Format](#error-entry-format)
- [Feature Request Format](#feature-request-format)
- [ID Generation](#id-generation)
- [Field Specifications](#field-specifications)

---

## Learning Entry Format

Append to `.learnings/LEARNINGS.md`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001 (if related to existing entry)

---
```

### Learning Categories

- `correction` - User corrected your understanding
- `insight` - New understanding from observation
- `knowledge_gap` - Discovered missing knowledge
- `best_practice` - Better approach found

---

## Error Entry Format

Append to `.learnings/ERRORS.md`:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
```text
Actual error message or output
```

### Context

- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix

If identifiable, what might resolve this

### Metadata

- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (if recurring)

---
```

---

## Feature Request Format

Append to `.learnings/FEATURE_REQUESTS.md`:

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
What the user wanted to do

### User Context
Why they needed it, what problem they're solving

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
How this could be built, what it might extend

### Metadata
- Frequency: first_time | recurring
- Related Features: existing_feature_name

---
```

---

## ID Generation

Format: `TYPE-YYYYMMDD-XXX`

- **TYPE**: `LRN` (learning), `ERR` (error), `FEAT` (feature)
- **YYYYMMDD**: Current date
- **XXX**: Sequential number or random 3 chars (e.g., `001`, `A7B`)

Examples: `LRN-20250115-001`, `ERR-20250115-A3F`, `FEAT-20250115-002`

---

## Field Specifications

### Priority Levels

| Priority | When to Use |
|----------|-------------|
| `critical` | Blocks core functionality, data loss risk, security issue |
| `high` | Significant impact, affects common workflows, recurring issue |
| `medium` | Moderate impact, workaround exists |
| `low` | Minor inconvenience, edge case, nice-to-have |

### Area Tags

| Area | Scope |
|------|-------|
| `frontend` | UI, components, client-side code |
| `backend` | API, services, server-side code |
| `infra` | CI/CD, deployment, Docker, cloud |
| `tests` | Test files, testing utilities, coverage |
| `docs` | Documentation, comments, READMEs |
| `config` | Configuration files, environment, settings |

### Status Values

- `pending` - Not yet addressed
- `in_progress` - Actively being worked on
- `resolved` - Fixed or completed
- `wont_fix` - Decided not to address
- `promoted` - Elevated to AGENTS.md or CLAUDE.md

### Source Values

- `conversation` - Learned during normal conversation
- `error` - Discovered from failure/error
- `user_feedback` - User explicitly corrected or taught

---

## Resolution Block

When an entry is resolved, add this section after Metadata:

```markdown
### Resolution
- **Resolved**: 2025-01-16T09:00:00Z
- **Commit/PR**: abc123 or #42
- **Notes**: Brief description of what was done
```

Then update the Status field to `resolved`.

---

## See Also

- [references/examples.md](examples.md) - Complete examples of well-formatted entries
- [references/promotion.md](promotion.md) - Guidelines for promoting entries to project memory
