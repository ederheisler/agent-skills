name: python-quality-gates
description: Use when needing project-agnostic Python quality gates script for linting, type checking, complexity analysis, hypothesis checks, testing, and docs linting before commits.

# Python Quality Gates

## Overview
Project-agnostic bash script enforcing Python code quality gates using ruff, pyrefly, radon, hypothesis checks, pytest, markdownlint. Modes allow fast runs (unit-tests for quick feedback, all-tests for comprehensive validation, no-tests for static only) to avoid context pollution between tasks.

## When to Use
Before committing Python code to ensure consistent quality checks, catch issues early, enforce standards across projects without assumptions about directory structure.

## Core Pattern
Run the script with a mode: `./quality-gates.sh unit-tests` for fast static + unit tests, `all-tests` for full validation, `no-tests` for lint/type/complexity only.

## Quick Reference
| Mode | Gates Run | Use Case |
|------|-----------|----------|
| unit-tests | ruff, pyrefly, radon, hypothesis, pytest unit/, markdownlint | Fast feedback between tasks |
| all-tests | ruff, pyrefly, radon, hypothesis, pytest all, markdownlint | Pre-merge/deploy comprehensive check |
| no-tests | ruff, pyrefly, radon, hypothesis, markdownlint | Static analysis only when time critical |

## Implementation
See quality-gates.sh for the script. Uses uv/uvx for tools, excludes common dirs like tests, docs, build. Graceful fallbacks if tools missing.

**For AI agents:** Check AGENTS.md for project-specific instructions. Load available superpowers skills and MCP tools (e.g., serena) before running gates.

## Common Mistakes
- Running full all-tests too often slows down iteration.
- Skipping modes under pressure; use no-tests for urgent static checks.
- Not excluding non-code dirs leads to false positives.

## Common Rationalizations
| Excuse | Reality |
|--------|---------|
| "Time-critical, skip checks" | Use no-tests mode for fast static validation. |
| "Already tested manually" | Automation ensures consistency; manual misses edge cases. |
| "Partial checks good enough" | Modes provide full coverage options; skipping hypothesis misses bugs. |
| "Static sufficient, skip tests" | Use no-tests mode explicitly; tests catch logic errors. |
| "Too slow, skip radon/type" | Tools are fast; skipping misses complexity/type issues. |
| "Script not in project" | Download/copy to project; run locally. |
| "Tools not installed" | Graceful fallbacks skip missing tools; install uv for full coverage. |
| "Modes confusing" | unit-tests fast, all-tests comprehensive, no-tests static only. |
| "Project doesn't need this" | All Python projects benefit from quality gates. |

## Red Flags - STOP and Start Over
- Skipping all checks
- Running partial without mode
- "Already did it manually"
- "Good enough for now"
- "Static checks sufficient"
- "Tests take too long"
- "Script not available"
- "Tools missing anyway"
- "Modes too confusing"
- Rationalizing under pressure

All mean run the script with appropriate mode.