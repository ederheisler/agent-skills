"""Tests for utility functions"""

import pytest
from pathlib import Path

from src.utils import load_frontmatter


# --- Tests for load_frontmatter ---


def test_load_frontmatter_with_valid_metadata(tmp_path):
    """Test parsing frontmatter with name and description"""
    # Arrange
    file = tmp_path / "skill-dir" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        "---\nname: My Skill\ndescription: A test skill\n---\n# Content here"
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "My Skill"
    assert description == "A test skill"


def test_load_frontmatter_with_quoted_values(tmp_path):
    """Test parsing frontmatter with quoted strings"""
    # Arrange
    file = tmp_path / "skill-dir" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        '---\nname: "Quoted Name"\ndescription: "Quoted description"\n---\n# Content'
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "Quoted Name"
    assert description == "Quoted description"


def test_load_frontmatter_with_single_quotes(tmp_path):
    """Test parsing frontmatter with single-quoted strings"""
    # Arrange
    file = tmp_path / "skill-dir" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        "---\nname: 'Single Quoted'\ndescription: 'Single quoted desc'\n---\n# Content"
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "Single Quoted"
    assert description == "Single quoted desc"


def test_load_frontmatter_missing_name_uses_directory(tmp_path):
    """Test that missing name defaults to parent directory name"""
    # Arrange
    file = tmp_path / "fallback-skill" / "SKILL.md"
    file.parent.mkdir()
    file.write_text("---\ndescription: Only description provided\n---\n# Content")

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "fallback-skill"
    assert description == "Only description provided"


def test_load_frontmatter_missing_description(tmp_path):
    """Test that missing description returns empty string"""
    # Arrange
    file = tmp_path / "skill-dir" / "SKILL.md"
    file.parent.mkdir()
    file.write_text("---\nname: Name Only\n---\n# Content")

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "Name Only"
    assert description == ""


def test_load_frontmatter_no_frontmatter(tmp_path):
    """Test file without frontmatter uses directory name"""
    # Arrange
    file = tmp_path / "no-frontmatter" / "SKILL.md"
    file.parent.mkdir()
    file.write_text("# Just content, no metadata")

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "no-frontmatter"
    assert description == ""


def test_load_frontmatter_empty_file(tmp_path):
    """Test empty file returns directory name and empty description"""
    # Arrange
    file = tmp_path / "empty-skill" / "SKILL.md"
    file.parent.mkdir()
    file.write_text("")

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "empty-skill"
    assert description == ""


def test_load_frontmatter_file_not_exists(tmp_path):
    """Test non-existent file returns directory name"""
    # Arrange
    file = tmp_path / "missing-skill" / "SKILL.md"
    file.parent.mkdir()
    # Don't create the file

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "missing-skill"
    assert description == ""


def test_load_frontmatter_malformed_frontmatter(tmp_path):
    """Test malformed frontmatter falls back to directory name for empty name field"""
    # Arrange
    file = tmp_path / "malformed" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        "---\n"
        "name:\n"  # Empty value - should fallback to directory name
        "description\n"  # Missing colon
        "---\n"
        "# Content"
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert - should fallback to directory name when name is empty
    assert name == "malformed"
    assert description == ""


def test_load_frontmatter_incomplete_frontmatter_delimiter(tmp_path):
    """Test file with only opening delimiter"""
    # Arrange
    file = tmp_path / "incomplete" / "SKILL.md"
    file.parent.mkdir()
    file.write_text("---\nname: Incomplete\n# Content without closing delimiter")

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "Incomplete"
    assert description == ""


def test_load_frontmatter_with_colons_in_values(tmp_path):
    """Test frontmatter values containing colons"""
    # Arrange
    file = tmp_path / "colons" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        "---\n"
        "name: My Skill: Advanced\n"
        "description: Description: with colons\n"
        "---\n"
        "# Content"
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "My Skill: Advanced"
    assert description == "Description: with colons"


def test_load_frontmatter_with_whitespace(tmp_path):
    """Test frontmatter with extra whitespace"""
    # Arrange
    file = tmp_path / "spaces" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        "---\n"
        "name:    Lots Of Spaces   \n"
        "description:   Spaced description   \n"
        "---\n"
        "# Content"
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert
    assert name == "Lots Of Spaces"
    assert description == "Spaced description"


def test_load_frontmatter_with_multiline_content(tmp_path):
    """Test frontmatter stops at first closing delimiter"""
    # Arrange
    file = tmp_path / "multiline" / "SKILL.md"
    file.parent.mkdir()
    file.write_text(
        "---\n"
        "name: First Name\n"
        "description: First description\n"
        "---\n"
        "# Content\n"
        "---\n"
        "name: Second Name\n"
        "---\n"
    )

    # Act
    name, description = load_frontmatter(file)

    # Assert - should only parse first frontmatter block
    assert name == "First Name"
    assert description == "First description"


def test_load_frontmatter_read_error_returns_defaults(tmp_path):
    """Test that file read errors return directory name and empty description"""
    # Arrange - create a directory instead of a file to trigger read error
    fake_file = tmp_path / "error-skill" / "SKILL.md"
    fake_file.parent.mkdir()
    fake_file.mkdir()  # Make it a directory, not a file

    # Act
    name, description = load_frontmatter(fake_file)

    # Assert - should return defaults without raising exception
    assert name == "error-skill"
    assert description == ""
