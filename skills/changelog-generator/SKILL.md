---
name: changelog-generator
description: Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes. Turns hours of manual changelog writing into minutes of automated generation.
---

# Changelog Generator

This skill transforms technical git commits into polished, user-friendly changelogs that your customers and users will actually understand and appreciate. It encodes the frameworks for writing release notes that different audiences actually read.

## When to Use This Skill

- Preparing release notes for a new version
- Creating weekly or monthly product update summaries
- Documenting changes for customers
- Writing changelog entries for app store submissions
- Generating update notifications
- Creating internal release documentation or detailed technical logs
- Maintaining a public changelog/product updates page

## What This Skill Does

1. **Scans Git History**: Analyzes commits from a specific time period or between versions
2. **Categorizes Changes**: Groups commits into logical categories (features, improvements, bug fixes, breaking changes, security)
3. **Translates Technical → User-Friendly**: Converts developer commits into customer language
4. **Formats Professionally**: Creates clean, structured changelog entries tailored to specific audiences
5. **Filters Noise**: Excludes internal commits (refactoring, tests, etc.)
6. **Follows Best Practices**: Applies changelog guidelines and your brand voice

## How to Use

### Basic Usage

From your project repository:

```
Create a changelog from commits since last release
```

```
Generate changelog for all commits from the past week
```

```
Create release notes for version 2.5.0 tailored for end users
```

### With Specific Date Range

```
Create a changelog for all commits between March 1 and March 15
```

### With Custom Guidelines

```
Create a changelog for commits since v2.4.0, using my changelog 
guidelines from CHANGELOG_STYLE.md
```

## Execution Instructions

Follow these steps to generate the changelog:

### 1. Fetch Commit History

Choose the appropriate command based on the user's request:

**By Time Period:**
```bash
# Get commits from the last X days/weeks
git log --since="7 days ago" --oneline --no-merges

# Get commits between two dates
git log --since="2024-03-01" --until="2024-03-15" --oneline --no-merges
```

**By Version Tag:**
```bash
# Get commits between the last tag and HEAD
git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-merges

# Get commits between two specific tags
git log v1.0.0..v1.1.0 --oneline --no-merges
```

### 2. Categorize Commits

Map commit contents to categories using these regex patterns (case-insensitive):

| Prefix/Pattern | Category | Emoji |
|----------------|----------|-------|
| `^feat:` or `feature:` | **New** | 🚀 |
| `^fix:` or `bug:` | **Fixed** | 🐛 |
| `^perf:` or `performance:` | **Improved** | ⚡ |
| `^docs:` | **Documentation** | 📚 |
| `^style:` or `ui:` | **Improved** | ✨ |
| `^refactor:` | **Internal** (Exclude unless major) | 🛠️ |
| `^test:` | **Internal** (Exclude) | 🧪 |
| `^chore:` | **Internal** (Exclude) | 🧹 |
| `BREAKING CHANGE:` | **Changed** | ⚠️ |

**Heuristics for Uncategorized Commits:**
- If message starts with "Add", "Create", "New" → **New**
- If message starts with "Update", "Improve", "Better" → **Improved**
- If message starts with "Fix", "Resolve", "Correct" → **Fixed**
- If message starts with "Remove", "Delete", "Deprecate" → **Changed**

### 3. Filter Noise

**Exclude commits that match:**
- `Merge branch...`
- `Bump version...`
- `Update dependencies...` (unless security related)
- `Lint code...`
- `Update README...` (unless meaningful doc change)

### 4. Group & Summarize

1. **Group** related commits (e.g., 5 commits about "Dark Mode" should become 1 bullet point).
2. **Summarize** technical details into user benefits.
   - *Input*: `feat: add redis caching layer to user endpoints`
   - *Output*: `Improved`: **User Dashboards**: Profiles now load instantly.

## Release Note Structure

### Standard Format

```markdown
## [VERSION] - [DATE]

### 🚀 NEW
- **[Feature]**: [User benefit] [Link to docs]

### ✨ IMPROVED  
- **[Enhancement]**: [What's better]

### 🐛 FIXED
- **[Bug]**: [What was wrong, now resolved]

### ⚠️ CHANGED
- **[Breaking change]**: [What to do]

### 📚 DOCUMENTATION
- **[Doc update]**: [What's new]
```

## Audience-Specific Versions

When asking for a changelog, specify your audience to get the right tone and detail level.

### End User (Customer-Facing)

**Tone:** Benefit-focused, simple language
**Length:** 3-5 bullets per category

**Example:**
> **New: Export to Excel**
> You can now export any report to Excel with one click. Find the export button in the top right of any report view.

### Technical (Developer-Facing)

**Tone:** Precise, technical detail
**Include:** API changes, breaking changes, migration steps

**Example:**
> **API: New pagination parameters**
> Added `cursor` and `limit` parameters to `/api/v2/users`. The `offset` parameter is deprecated and will be removed in v3.0. See [migration guide].

### Internal (Sales/CS)

**Tone:** Enablement-focused
**Include:** Talking points, competitive implications

**Example:**
> **New: Export to Excel**
> - Talking point: "You can now export any report to Excel instantly"
> - Customer ask this solves: Export functionality (requested by 47 customers)
> - Competitive note: Competitor X charges extra for this

## Categorization Framework

| Category | Icon | Include When |
|----------|------|--------------|
| New | 🚀 | New features or capabilities |
| Improved | ✨ | Enhancements to existing features |
| Fixed | 🐛 | Bug fixes |
| Changed | ⚠️ | Breaking changes, deprecations |
| Security | 🔒 | Security updates |
| Performance | ⚡ | Speed/efficiency improvements |

## Writing Guidelines

### Transform Technical to User

| Technical | User-Friendly |
|-----------|---------------|
| "Implemented caching layer" | "Reports now load 3x faster" |
| "Fixed null pointer exception" | "Resolved issue causing occasional crashes" |
| "Added OAuth2 support" | "You can now sign in with Google" |
| "Refactored data model" | [Don't include - no user impact] |

### What to Include/Exclude

**Include:**
- User-facing changes
- Performance improvements users will notice
- Bug fixes users reported
- Security updates

**Exclude:**
- Internal refactoring
- Test improvements
- Dependency updates (unless security)
- Changes with no user impact

## Tips

- Run from your git repository root
- Specify date ranges for focused changelogs
- Use your CHANGELOG_STYLE.md for consistent formatting
- Review and adjust the generated changelog before publishing
- Save output directly to CHANGELOG.md

## Related Use Cases

- Creating GitHub release notes
- Writing app store update descriptions
- Generating email updates for users
- Creating social media announcement posts
