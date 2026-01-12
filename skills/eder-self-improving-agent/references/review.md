# Periodic Review Guide

Commands and workflow for reviewing accumulated learnings.

## When to Review

Review `.learnings/` at natural breakpoints:

- Before starting a new major task
- After completing a feature
- When working in an area with past learnings
- Weekly during active development

## Quick Status Commands

### Count pending items

```bash
grep -h "Status\*\*: pending" .learnings/*.md | wc -l
```text

### List all pending high-priority items

```bash
grep -B5 "Priority\*\*: high" .learnings/*.md | grep "^## \["
```

### Find learnings for a specific area

```bash
# Backend learnings
grep -l "Area\*\*: backend" .learnings/*.md

# Frontend learnings
grep -l "Area\*\*: frontend" .learnings/*.md
```text

### Find entries by status

```bash
# Pending entries
grep "Status\*\*: pending" .learnings/*.md

# Resolved entries
grep "Status\*\*: resolved" .learnings/*.md

# In-progress entries
grep "Status\*\*: in_progress" .learnings/*.md
```

### Search for related entries

```bash
# Search by keyword
grep -r "authentication" .learnings/

# Find similar errors
grep -A10 "ERR-" .learnings/ERRORS.md | grep "Summary"
```text

## Review Workflow

### 1. Generate Status Report

```bash
echo "=== Learnings Status ==="
echo "Pending: $(grep -h 'Status\*\*: pending' .learnings/*.md | wc -l)"
echo "In Progress: $(grep -h 'Status\*\*: in_progress' .learnings/*.md | wc -l)"
echo "High Priority: $(grep -h 'Priority\*\*: high' .learnings/*.md | wc -l)"
echo "Critical: $(grep -h 'Priority\*\*: critical' .learnings/*.md | wc -l)"
```

### 2. Identify Patterns

Look for:

- **Recurring errors**: Multiple entries with `See Also` links
- **Similar areas**: Clusters of entries in same area
- **Old pending items**: Entries from weeks ago still pending

### 3. Review Actions

For each entry:

- [ ] **Resolve** if already fixed
- [ ] **Promote** if broadly applicable
- [ ] **Link** related entries with `See Also`
- [ ] **Escalate** recurring issues (bump priority, create tech debt ticket)
- [ ] **Archive** if no longer relevant

### 4. Update Status

Mark resolved items:

```markdown
**Status**: resolved

### Resolution
- **Resolved**: 2025-01-16T09:00:00Z
- **Commit/PR**: #123
- **Notes**: Fixed by implementing XYZ
```text

## Recurring Pattern Detection

If multiple entries reference the same issue:

1. **Search first**: `grep -r "keyword" .learnings/`
2. **Link entries**: Add `**See Also**: ERR-20250110-001` in Metadata
3. **Bump priority** if issue keeps recurring (medium → high)
4. **Consider systemic fix**:
   - Missing documentation → promote to CLAUDE.md
   - Missing automation → add to AGENTS.md
   - Architectural problem → create tech debt ticket

## Example Review Session

```bash
# Check status
grep "Status\*\*: pending" .learnings/*.md | wc -l
# Output: 12 pending items

# List high-priority items
grep -B5 "Priority\*\*: high" .learnings/*.md | grep "^## \["
# Output:
# ## [ERR-20250115-001] docker_build
# ## [LRN-20250116-003] best_practice

# Search for recurring docker issues
grep -r "docker" .learnings/
# Output: 3 different docker errors

# Decision: Promote docker setup to CLAUDE.md
```

## Advanced Queries

### Find entries by date range

```bash
# January 2025 entries
grep "^\[LRN\|ERR\|FEAT\]-202501" .learnings/*.md
```text

### Find unlinked related entries

```bash
# Entries without See Also links that might be related
grep -L "See Also" .learnings/*.md | xargs grep "authentication"
```

### Export summary

```bash
# Create summary report
{
  echo "# Learnings Summary"
  echo
  echo "## High Priority Pending"
  grep -B10 "Priority\*\*: high" .learnings/*.md | grep -E "^## \[|^### Summary"
  echo
  echo "## Recent Errors"
  grep -B10 "ERR-202501" .learnings/ERRORS.md | grep -E "^## \[|^### Summary"
} > learnings_summary.md
```

## Review Checklist

Use this checklist during periodic review:

- [ ] All resolved items marked with Resolution block
- [ ] High-value learnings promoted to CLAUDE.md or AGENTS.md
- [ ] Related entries linked with See Also
- [ ] Recurring issues escalated (priority bump or tech debt)
- [ ] Old entries archived or marked wont_fix if irrelevant
- [ ] New patterns documented
- [ ] Summary report generated for team

## Maintenance Tips

1. **Review little and often**: 5 minutes weekly better than 1 hour monthly
2. **Act on critical immediately**: Don't wait for scheduled review
3. **Promote aggressively**: When in doubt, promote to CLAUDE.md
4. **Archive old resolved**: Move to `.learnings/archive/` after 3 months
5. **Link proactively**: Add See Also while issues are fresh

---

## See Also

- [references/promotion.md](promotion.md) - Guidelines for promoting entries
- [references/formats.md](formats.md) - Entry format specifications
