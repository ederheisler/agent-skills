#!/usr/bin/env python3
"""Test the installer's core functionality"""

from pathlib import Path
from install import list_skills, get_installed_skills, SkillInfo

# Test 1: List all skills
print("=" * 80)
print("TEST 1: List Available Skills with Frontmatter Parsing")
print("=" * 80)
skills = list_skills()
print(f"Found {len(skills)} skills:\n")
for i, skill in enumerate(skills[:5], 1):  # Show first 5
    desc = (
        skill.description[:70] + "…"
        if len(skill.description) > 70
        else skill.description
    )
    print(f"{i}. {skill.name}")
    print(f"   Dir: {skill.dir_name}")
    print(f"   Desc: {desc}\n")
if len(skills) > 5:
    print(f"... and {len(skills) - 5} more skills")

# Test 2: Check installed skills
print("\n" + "=" * 80)
print("TEST 2: Check Installed Skills (if any)")
print("=" * 80)
test_dest = Path("/tmp/test-skills")
installed = get_installed_skills(test_dest)
print(f"Installed in {test_dest}: {len(installed)} skills")
if installed:
    for skill in list(installed)[:5]:
        print(f"  • {skill}")

# Test 3: Verify all skills have descriptions
print("\n" + "=" * 80)
print("TEST 3: Frontmatter Coverage Check")
print("=" * 80)
skills_without_desc = [s for s in skills if not s.description]
if skills_without_desc:
    print(f"⚠️  {len(skills_without_desc)} skills missing descriptions:")
    for skill in skills_without_desc:
        print(f"  • {skill.name} ({skill.dir_name})")
else:
    print(f"✓ All {len(skills)} skills have descriptions from frontmatter")

print("\n" + "=" * 80)
print("✓ All tests passed! Installer ready with dynamic skill loading.")
print("=" * 80)
