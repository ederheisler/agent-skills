# Agent Skills Collection

A curated collection of AI agent skills with progressive disclosure enhancements and agent-agnostic language.

## Skills Included

### 1. **self-improving-agent**
Captures learnings, errors, and corrections to enable continuous improvement.

**Features:**
- Track learnings, errors, and feature requests
- Promote important learnings to project memory
- Periodic review workflow
- Comprehensive entry format templates

**Structure:**
- `SKILL.md` (179 lines) - Core workflow
- `references/` - Detailed format specifications, promotion guidelines, review commands, examples
- `assets/` - Ready-to-use template files

**Origin:** Original skill created for this collection

---

### 2. **frontend-design**
Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics.

**Features:**
- 11 aesthetic directions with implementation details
- Typography, color, motion, and composition guidelines
- Real-world examples with complete code
- Anti-patterns guide with transformations

**Structure:**
- `SKILL.md` (102 lines) - Core workflow and design thinking
- `references/aesthetics.md` - Comprehensive aesthetic directions
- `references/examples.md` - 7 complete real-world examples
- `references/anti-patterns.md` - What to avoid with fixes

**Origin:** Based on [Anthropic's frontend-design skill](https://github.com/anthropics/skills/tree/main/skills/frontend-design), enhanced with progressive disclosure and extensive reference materials

---

### 3. **skill-creator**
Guide for creating effective skills with specialized knowledge, workflows, and tool integrations.

**Features:**
- 6-step skill creation process
- Progressive disclosure design patterns
- Validation and packaging scripts
- Design pattern references

**Structure:**
- `SKILL.md` - Comprehensive creation guide
- `scripts/` - init_skill.py, package_skill.py, quick_validate.py
- `references/` - Output patterns, workflow patterns

**Origin:** From [Anthropic's skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)

---

### 4. **doc-coauthoring**
Structured workflow for co-authoring documentation with context gathering, refinement, and reader testing.

**Features:**
- 3-stage workflow: Context, Refinement, Testing
- Reader Agent testing for quality assurance
- Integration with document platforms
- Iterative section-by-section building

**Structure:**
- `SKILL.md` - Complete workflow guide

**Origin:** From [Anthropic's doc-coauthoring](https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring)

---

### 5. **mcp-builder**
Guide for creating high-quality MCP (Model Context Protocol) servers for LLM integration.

**Features:**
- Comprehensive MCP development workflow
- TypeScript and Python implementation patterns
- Best practices and tool design
- Evaluation framework

**Structure:**
- `SKILL.md` - 4-phase development process
- `reference/` - Best practices, language guides, evaluation guide
- `scripts/` - Evaluation tools and examples

**Origin:** From [Anthropic's mcp-builder](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)

---

### 6. **pdf**
Comprehensive PDF manipulation toolkit for processing, creating, and analyzing PDFs.

**Features:**
- Text and table extraction
- PDF creation and merging/splitting
- Form filling capabilities
- Command-line and Python libraries

**Structure:**
- `SKILL.md` - Core operations guide
- `forms.md` - Form filling instructions
- `reference.md` - Advanced features
- `scripts/` - PDF manipulation utilities

**Origin:** From [Anthropic's pdf](https://github.com/anthropics/skills/tree/main/skills/pdf)

---

### 7. **theme-factory**
Curated collection of 10 professional themes for styling artifacts with cohesive designs.

**Features:**
- 10 pre-set professional themes
- Custom theme generation
- Color palettes and font pairings
- Visual showcase

**Structure:**
- `SKILL.md` - Theme application guide
- `themes/` - 10 theme specifications
- `theme-showcase.pdf` - Visual preview

**Origin:** From [Anthropic's theme-factory](https://github.com/anthropics/skills/tree/main/skills/theme-factory)

---

### 8. **webapp-testing**
Playwright-based toolkit for testing and interacting with local web applications.

**Features:**
- Browser automation with Playwright
- Server lifecycle management
- DOM inspection and interaction
- Console logging capture

**Structure:**
- `SKILL.md` - Testing workflow
- `scripts/` - Server management utilities
- `examples/` - Common testing patterns

**Origin:** From [Anthropic's webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)

---

### 9. **internal-comms**
Templates and guidelines for writing company internal communications.

**Features:**
- 3P updates (Progress, Plans, Problems)
- Company newsletters
- FAQ responses
- Status reports and project updates

**Structure:**
- `SKILL.md` - Usage guide
- `examples/` - Communication templates and guidelines

**Origin:** From [Anthropic's internal-comms](https://github.com/anthropics/skills/tree/main/skills/internal-comms)

---

### 10. **canvas-design**
Create museum-quality visual art in PNG and PDF using design philosophy principles.

**Features:**
- Design philosophy creation workflow
- Visual expression without text dependency
- 81 professional fonts included
- Multi-page artwork support

**Structure:**
- `SKILL.md` - 2-step creation process
- `canvas-fonts/` - 81 professional fonts

**Origin:** From [Anthropic's canvas-design](https://github.com/anthropics/skills/tree/main/skills/canvas-design)

---

### 11. **quality-gates**
Project-agnostic Python quality gates script for comprehensive code quality assurance.

**Features:**
- Bash script enforcing Python code quality gates
- Supports ruff (linting), pyrefly (type checking), radon (complexity)
- Hypothesis checks, pytest (testing), markdownlint (docs)
- Three modes: unit-tests (fast), all-tests (comprehensive), no-tests (static only)
- Graceful fallbacks when tools are missing
- Excludes common directories (tests, docs, build)

**Structure:**
- `SKILL.md` - Complete usage guide with modes and common pitfalls
- `scripts/quality-gates.sh` - Executable quality gates script

**Origin:** Original skill created for Python code quality assurance

---

## Progressive Disclosure Principle

All skills in this collection follow **progressive disclosure** design:

### Three-Level Loading System

1. **Level 1: Metadata** (~100 words)
   - Name and description
   - Always loaded in context
   - Helps the agent decide when to use the skill

2. **Level 2: Core SKILL.md** (<500 lines)
   - Essential workflow and guidance
   - Loaded when skill triggers
   - Links to detailed references

3. **Level 3: References & Assets** (unlimited)
   - Detailed documentation
   - Code examples
   - Templates and assets
   - Loaded only as needed

### Benefits

- **Token efficient** - Only load what's needed
- **Better organized** - Each file has one purpose
- **Easier to maintain** - Update details without touching workflow
- **More comprehensive** - Can include extensive examples and guides

---

## Skill Metrics

| Skill | SKILL.md Lines | Additional Files | Total Files |
|-------|---------------|------------------|-------------|
| self-improving-agent | 179 | 7 (refs + assets) | 8 |
| frontend-design | 102 | 4 (refs + license) | 5 |
| skill-creator | 338 | 7 (refs + scripts) | 8 |
| doc-coauthoring | ~300 | 1 (license) | 2 |
| mcp-builder | ~200 | 10 (refs + scripts) | 11 |
| pdf | ~250 | 12 (refs + scripts) | 13 |
| theme-factory | ~100 | 13 (themes + assets) | 14 |
| webapp-testing | ~150 | 6 (examples + scripts) | 7 |
| internal-comms | ~30 | 6 (examples) | 7 |
| canvas-design | ~250 | 83 (fonts) | 84 |
| quality-gates | ~60 | 2 (scripts) | 3 |

**Total: 11 skills, 238 files**

---

## Usage

Each skill directory contains:
- `SKILL.md` - Main skill file with YAML frontmatter
- `references/` - Optional detailed documentation (loaded on-demand)
- `assets/` - Optional template files, examples, or resources
- `scripts/` - Optional executable utilities
- `LICENSE.txt` - License information

### Loading a Skill

Skills can be:
1. **Copied** directly into your project's skills directory
2. **Referenced** from this repository
3. **Packaged** using the skill-creator scripts

---

## Credits

- **Anthropic Skills**: Original inspiration from [anthropics/skills](https://github.com/anthropics/skills)
- **Enhanced by**: Progressive disclosure improvements and expanded reference materials

---

## License

Individual skills contain their own LICENSE.txt files. Most are licensed under Apache 2.0 (from Anthropic originals).

---

## Contributing

These skills follow the [skill-creator](skill-creator/SKILL.md) guidelines. To add or improve a skill:

1. Use `skill-creator/scripts/init_skill.py` to create a new skill
2. Follow progressive disclosure principles
3. Validate with `skill-creator/scripts/quick_validate.py`
4. Submit a pull request

---

## Learn More

- [What is Progressive Disclosure?](skill-creator/references/output-patterns.md)
- [Skill Creation Process](skill-creator/SKILL.md)
- [Design Patterns](skill-creator/references/workflows.md)
