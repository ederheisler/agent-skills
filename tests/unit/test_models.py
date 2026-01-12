"""Tests for data models"""

import pytest
from pathlib import Path

from src.models import SkillInfo


# --- Tests for SkillInfo properties ---


def test_skill_info_is_script_returns_true_for_script_type():
    """Test is_script property returns True when type is 'script'"""
    # Arrange
    skill = SkillInfo(
        name="Test Skill",
        description="A test skill",
        path=Path("/test"),
        dir_name="test-skill",
        type="script",
    )

    # Act & Assert
    assert skill.is_script is True


def test_skill_info_is_script_returns_false_for_plugin_type():
    """Test is_script property returns False when type is 'plugin'"""
    # Arrange
    skill = SkillInfo(
        name="Test Plugin",
        description="A test plugin",
        path=Path("/test"),
        dir_name="test-plugin",
        type="plugin",
    )

    # Act & Assert
    assert skill.is_script is False


def test_skill_info_is_plugin_returns_true_for_plugin_type():
    """Test is_plugin property returns True when type is 'plugin'"""
    # Arrange
    skill = SkillInfo(
        name="Test Plugin",
        description="A test plugin",
        path=Path("/test"),
        dir_name="test-plugin",
        type="plugin",
    )

    # Act & Assert
    assert skill.is_plugin is True


def test_skill_info_is_plugin_returns_false_for_script_type():
    """Test is_plugin property returns False when type is 'script'"""
    # Arrange
    skill = SkillInfo(
        name="Test Skill",
        description="A test skill",
        path=Path("/test"),
        dir_name="test-skill",
        type="script",
    )

    # Act & Assert
    assert skill.is_plugin is False


def test_skill_info_default_type_is_script():
    """Test SkillInfo defaults to 'script' type when not specified"""
    # Arrange & Act
    skill = SkillInfo(
        name="Default Skill",
        description="A skill with default type",
        path=Path("/test"),
        dir_name="default-skill",
    )

    # Assert
    assert skill.type == "script"
    assert skill.is_script is True
    assert skill.is_plugin is False


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
        type="plugin",
    )

    # Assert
    assert skill.name == "My Skill"
    assert skill.description == "A comprehensive test skill"
    assert skill.path == test_path
    assert skill.dir_name == "my-skill"
    assert skill.type == "plugin"
