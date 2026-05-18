"""Tests for data models"""

from pathlib import Path

from src.models import SkillInfo


def test_skill_info_stores_all_fields():
    """Test SkillInfo correctly stores all provided fields"""
    # Arrange
    test_path = Path("/home/user/skills/my-skill")

    # Act
    skill = SkillInfo(
        name="My Skill",
        description="A comprehensive test skill",
        path=test_path,
        dir_name="my-skill",
    )

    # Assert
    assert skill.name == "My Skill"
    assert skill.description == "A comprehensive test skill"
    assert skill.path == test_path
    assert skill.dir_name == "my-skill"
