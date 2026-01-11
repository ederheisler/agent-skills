#!/usr/bin/env python3
"""
Tests for the skills installer - runs without pytest.
"""

import shutil
import tempfile
from pathlib import Path
from typing import List, Tuple

from install import (
    get_skill_info,
    list_skills,
    get_installed_skills,
    SkillInfo,
)

SKILLS_DIR = Path("skills")


class TestRunner:
    """Simple test runner without pytest"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests: List[Tuple[str, bool, str]] = []

    def assert_true(self, condition: bool, message: str) -> None:
        if condition:
            self.passed += 1
            self.tests.append((message, True, ""))
        else:
            self.failed += 1
            self.tests.append((message, False, f"Assertion failed: {message}"))

    def assert_equal(self, actual, expected, message: str) -> None:
        if actual == expected:
            self.passed += 1
            self.tests.append((message, True, ""))
        else:
            self.failed += 1
            self.tests.append((message, False, f"Expected {expected}, got {actual}"))

    def assert_in(self, item, container, message: str) -> None:
        if item in container:
            self.passed += 1
            self.tests.append((message, True, ""))
        else:
            self.failed += 1
            self.tests.append((message, False, f"{item} not in {container}"))

    def report(self) -> None:
        print(f"\n{'=' * 60}")
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print(f"{'=' * 60}\n")

        for test_name, passed, error in self.tests:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {test_name}")
            if error:
                print(f"       {error}")

        print(f"\n{'=' * 60}\n")


# Create test runner
runner = TestRunner()


def test_list_skills():
    """Test skill discovery"""
    skills = list_skills()
    runner.assert_true(isinstance(skills, list), "list_skills returns a list")
    runner.assert_true(len(skills) > 0, "At least one skill found")


def test_skills_sorted():
    """Test skills are sorted by name"""
    skills = list_skills()
    names = [s.name for s in skills]
    runner.assert_equal(names, sorted(names), "Skills sorted by name")


def test_skill_info_fields():
    """Test skill info has required fields"""
    skills = list_skills()
    if skills:
        skill = skills[0]
        runner.assert_true(skill.name, f"Skill has name: {skill.name}")
        runner.assert_true(skill.path, f"Skill has path: {skill.path}")
        runner.assert_true(skill.dir_name, f"Skill has dir_name: {skill.dir_name}")


def test_get_skill_info_parses():
    """Test frontmatter parsing"""
    skill_dir = SKILLS_DIR / "brainstorming"
    if skill_dir.exists():
        skill = get_skill_info(skill_dir)
        runner.assert_true(skill.name, "Skill has name from frontmatter")
        runner.assert_equal(skill.dir_name, "brainstorming", "dir_name matches folder")


def test_installed_skills_empty():
    """Test get_installed_skills on empty directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        installed = get_installed_skills(dest)
        runner.assert_equal(installed, set(), "No skills in empty directory")


def test_installed_skills_detects():
    """Test get_installed_skills detects directories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        (dest / "skill1").mkdir()
        (dest / "skill2").mkdir()
        (dest / "file.txt").touch()

        installed = get_installed_skills(dest)
        runner.assert_in("skill1", installed, "skill1 detected")
        runner.assert_in("skill2", installed, "skill2 detected")
        runner.assert_true("file.txt" not in installed, "Files not included")


def test_skill_copy():
    """Test copying a skill directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "skill"
        source = SKILLS_DIR / "brainstorming"

        if source.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, dest)

            runner.assert_true(dest.exists(), "Destination exists")
            runner.assert_true((dest / "SKILL.md").exists(), "SKILL.md copied")


def test_skill_removal():
    """Test removing a skill directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "test_skill"
        dest.mkdir()
        (dest / "file.txt").touch()

        runner.assert_true(dest.exists(), "Directory created")
        shutil.rmtree(dest)
        runner.assert_true(not dest.exists(), "Directory removed after rmtree")


def test_install_workflow():
    """Test full install workflow"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        source = SKILLS_DIR / "brainstorming"

        if source.exists():
            # Before install
            initial = get_installed_skills(dest)
            runner.assert_true(
                "brainstorming" not in initial, "Not initially installed"
            )

            # Install
            dest.mkdir(parents=True, exist_ok=True)
            skill_dest = dest / "brainstorming"
            shutil.copytree(source, skill_dest)

            # After install
            after = get_installed_skills(dest)
            runner.assert_in("brainstorming", after, "Skill installed")


def test_remove_workflow():
    """Test full remove workflow"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        source = SKILLS_DIR / "brainstorming"

        if source.exists():
            # Install first
            dest.mkdir(parents=True, exist_ok=True)
            skill_dest = dest / "brainstorming"
            shutil.copytree(source, skill_dest)

            before = get_installed_skills(dest)
            runner.assert_in("brainstorming", before, "Initially installed")

            # Remove
            shutil.rmtree(skill_dest)

            # Verify removed
            after = get_installed_skills(dest)
            runner.assert_true("brainstorming" not in after, "Skill removed")


def test_multiple_install():
    """Test installing multiple skills"""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir)
        skills_to_install = ["brainstorming", "canvas-design"]

        dest.mkdir(parents=True, exist_ok=True)

        for skill_name in skills_to_install:
            source = SKILLS_DIR / skill_name
            if source.exists():
                skill_dest = dest / skill_name
                shutil.copytree(source, skill_dest)

        installed = get_installed_skills(dest)
        for skill_name in skills_to_install:
            if (SKILLS_DIR / skill_name).exists():
                runner.assert_in(skill_name, installed, f"{skill_name} installed")


if __name__ == "__main__":
    # Run all tests
    test_list_skills()
    test_skills_sorted()
    test_skill_info_fields()
    test_get_skill_info_parses()
    test_installed_skills_empty()
    test_installed_skills_detects()
    test_skill_copy()
    test_skill_removal()
    test_install_workflow()
    test_remove_workflow()
    test_multiple_install()

    # Report results
    runner.report()
