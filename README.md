# Agent Skills Collection

A curated collection of AI agent skills with progressive disclosure enhancements.

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

| Skill | SKILL.md Lines | Reference Files | Total Content |
|-------|---------------|-----------------|---------------|
| self-improving-agent | 179 | 4 files | 2,483+ lines |
| frontend-design | 102 | 3 files | 1,506+ lines |
| skill-creator | 338 | 2 files | 1,156+ lines |

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
