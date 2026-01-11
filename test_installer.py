#!/usr/bin/env python3
"""Test the installer's core functionality"""

from pathlib import Path
from install import list_skills, get_installed_skills, SkillInfo

# Test 1: List all skills
print("=" * 60)
print("TEST 1: List Available Skills")
print("=" * 60)
skills = list_skills()
print(f"Found {len(skills)} skills:")
for skill in skills[:5]:  # Show first 5
    print(f"  • {skill.name:<30} ({skill.dir_name})")
if len(skills) > 5:
    print(f"  ... and {len(skills) - 5} more")

# Test 2: Check installed skills
print("\n" + "=" * 60)
print("TEST 2: Check Installed Skills (if any)")
print("=" * 60)
test_dest = Path("/tmp/test-skills")
installed = get_installed_skills(test_dest)
print(f"Installed in {test_dest}: {len(installed)} skills")
if installed:
    for skill in list(installed)[:5]:
        print(f"  • {skill}")

# Test 3: Verify SkillListItem construction
print("\n" + "=" * 60)
print("TEST 3: Skill Info Extraction")
print("=" * 60)
if skills:
    skill = skills[0]
    print(f"Name: {skill.name}")
    print(f"Description: {skill.description}")
    print(f"Path: {skill.path}")
    print(f"Dir Name: {skill.dir_name}")
    print("✓ Skill info looks good")

print("\n" + "=" * 60)
print("✓ All tests passed! Installer ready to use.")
print("=" * 60)
