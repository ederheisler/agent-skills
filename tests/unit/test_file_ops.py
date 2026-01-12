from pathlib import Path
from unittest.mock import patch, Mock
import shutil

import pytest

from src import models, skills

# --- Fixtures ---


@pytest.fixture
def mock_skills_dir(tmp_path):
    """Create a temporary structure for skills"""
    skills_root = tmp_path / "skills"
    skills_root.mkdir()

    # Skill 1: Valid with Metadata
    s1 = skills_root / "skill-one"
    s1.mkdir()
    (s1 / "SKILL.md").write_text(
        "---\nname: One\ndescription: The first skill\n---\n# Content"
    )

    # Skill 2: No Metadata (defaults to dir name)
    s2 = skills_root / "skill-two"
    s2.mkdir()
    (s2 / "SKILL.md").write_text("# Just Content")

    return skills_root


@pytest.fixture
def mock_dest_dir(tmp_path):
    """Create a temporary destination directory"""
    dest = tmp_path / "dest"
    dest.mkdir()
    return dest


# --- Tests ---


def test_install_skill_copies_files(tmp_path, mock_dest_dir):
    """Test that install_skill correctly copies the skill directory"""
    # Arrange
    source = tmp_path / "source_skill"
    source.mkdir()
    (source / "script.py").write_text("print('hello')")
    (source / "subdir").mkdir()
    (source / "subdir" / "data.txt").write_text("data")

    skill = models.SkillInfo(
        name="Source Skill",
        description="A test skill",
        path=source,
        dir_name="source_skill",
    )

    # Act
    result = skills.install_skill(skill, mock_dest_dir)

    # Assert
    assert result is True
    installed_path = mock_dest_dir / "source_skill"
    assert installed_path.exists()
    assert (installed_path / "script.py").read_text() == "print('hello')"
    assert (installed_path / "subdir" / "data.txt").read_text() == "data"


def test_install_skill_overwrites_existing(tmp_path, mock_dest_dir):
    """Test that install_skill overwrites an existing installation"""
    # Arrange
    source = tmp_path / "source_skill_v2"
    source.mkdir()
    (source / "version.txt").write_text("v2")

    dest_skill = mock_dest_dir / "my_skill"
    dest_skill.mkdir()
    (dest_skill / "version.txt").write_text("v1")
    (dest_skill / "old_file.txt").write_text("keep?")

    skill = models.SkillInfo(
        name="My Skill", description="A test skill", path=source, dir_name="my_skill"
    )

    # Act
    result = skills.install_skill(skill, mock_dest_dir)

    # Assert
    assert result is True
    assert (dest_skill / "version.txt").read_text() == "v2"
    assert not (
        dest_skill / "old_file.txt"
    ).exists()  # install_skill calls rmtree first


def test_remove_skill_deletes_directory(mock_dest_dir):
    """Test that remove_skill deletes the installed directory"""
    # Arrange
    target = mock_dest_dir / "to_remove"
    target.mkdir()
    (target / "file").touch()

    skill = models.SkillInfo(
        name="Removable",
        description="desc",
        path=Path("irrelevant"),
        dir_name="to_remove",
    )

    # Act
    result = skills.remove_skill(skill, mock_dest_dir)

    # Assert
    assert result is True
    assert not target.exists()


def test_remove_skill_returns_false_if_not_exists(mock_dest_dir):
    """Test that remove_skill returns False if directory doesn't exist"""
    skill = models.SkillInfo(
        name="Ghost",
        description="desc",
        path=Path("irrelevant"),
        dir_name="ghost_skill",
    )

    # Act
    result = skills.remove_skill(skill, mock_dest_dir)

    # Assert
    assert result is False


@patch("src.skills.load_plugins")
def test_load_skills_lists_available_skills(mock_load_plugins, mock_skills_dir):
    """Test loading skills from the configured directory"""
    # Arrange
    mock_load_plugins.return_value = []

    # Act
    result = skills.load_skills(mock_skills_dir)

    # Assert
    # Expect: Separator (1) + 2 regular skills = 3 items total
    # Wait, implementation adds separator explicitly.
    # skills = [] + load_plugins + [separator] + regular_skills

    assert len(result) == 3

    # Filter out separator
    real_skills = [s for s in result if s.name != ""]
    assert len(real_skills) == 2

    names = {s.name for s in real_skills}
    # "One" comes from frontmatter, "skill-two" comes from dir name default
    assert "One" in names
    assert "skill-two" in names

    # Check description
    skill_one = next(s for s in real_skills if s.name == "One")
    assert skill_one.description == "The first skill"


def test_get_installed_skills_lists_directories(mock_dest_dir):
    """Test listing installed skills"""
    # Arrange
    (mock_dest_dir / "skill1").mkdir()
    (mock_dest_dir / "skill2").mkdir()
    (mock_dest_dir / "file_not_dir").touch()

    with patch("src.skills.get_installed_plugins", return_value=[]):
        # Act
        result = skills.get_installed_skills(mock_dest_dir)

    # Assert
    assert "skill1" in result
    assert "skill2" in result
    assert "file_not_dir" not in result


def test_get_installed_skills_includes_plugins(mock_dest_dir):
    """Test that installed plugins are included in the set"""
    with patch("src.skills.get_installed_plugins", return_value=["my-plugin"]):
        result = skills.get_installed_skills(mock_dest_dir)

    assert "my-plugin" in result


# --- Error handling tests ---


def test_install_skill_returns_false_on_permission_error(tmp_path, mock_dest_dir):
    """Test install_skill returns False when permission denied"""
    # Arrange
    source = tmp_path / "source_skill"
    source.mkdir()
    (source / "file.txt").write_text("content")

    skill = models.SkillInfo(
        name="Test Skill",
        description="Test",
        path=source,
        dir_name="test_skill",
    )

    # Act - Mock copytree to raise PermissionError
    with patch("shutil.copytree", side_effect=PermissionError("Access denied")):
        result = skills.install_skill(skill, mock_dest_dir)

    # Assert
    assert result is False


def test_install_skill_returns_false_on_io_error(tmp_path, mock_dest_dir):
    """Test install_skill returns False on I/O errors"""
    # Arrange
    source = tmp_path / "source_skill"
    source.mkdir()
    (source / "file.txt").write_text("content")

    skill = models.SkillInfo(
        name="Test Skill",
        description="Test",
        path=source,
        dir_name="test_skill",
    )

    # Act - Mock copytree to raise OSError (disk full, etc.)
    with patch("shutil.copytree", side_effect=OSError("Disk full")):
        result = skills.install_skill(skill, mock_dest_dir)

    # Assert
    assert result is False


def test_remove_skill_returns_false_on_permission_error(mock_dest_dir):
    """Test remove_skill returns False when permission denied"""
    # Arrange
    target = mock_dest_dir / "to_remove"
    target.mkdir()

    skill = models.SkillInfo(
        name="Test Skill",
        description="Test",
        path=Path("irrelevant"),
        dir_name="to_remove",
    )

    # Act - Mock rmtree to raise PermissionError
    with patch("shutil.rmtree", side_effect=PermissionError("Access denied")):
        result = skills.remove_skill(skill, mock_dest_dir)

    # Assert
    assert result is False


def test_remove_skill_returns_false_on_io_error(mock_dest_dir):
    """Test remove_skill returns False on I/O errors"""
    # Arrange
    target = mock_dest_dir / "to_remove"
    target.mkdir()

    skill = models.SkillInfo(
        name="Test Skill",
        description="Test",
        path=Path("irrelevant"),
        dir_name="to_remove",
    )

    # Act - Mock rmtree to raise OSError
    with patch("shutil.rmtree", side_effect=OSError("I/O error")):
        result = skills.remove_skill(skill, mock_dest_dir)

    # Assert
    assert result is False


def test_install_skill_does_not_catch_keyboard_interrupt(tmp_path, mock_dest_dir):
    """Test install_skill allows KeyboardInterrupt to propagate"""
    # Arrange
    source = tmp_path / "source_skill"
    source.mkdir()

    skill = models.SkillInfo(
        name="Test Skill",
        description="Test",
        path=source,
        dir_name="test_skill",
    )

    # Act & Assert - KeyboardInterrupt should propagate
    with patch("shutil.copytree", side_effect=KeyboardInterrupt()):
        with pytest.raises(KeyboardInterrupt):
            skills.install_skill(skill, mock_dest_dir)


def test_remove_skill_does_not_catch_keyboard_interrupt(mock_dest_dir):
    """Test remove_skill allows KeyboardInterrupt to propagate"""
    # Arrange
    target = mock_dest_dir / "to_remove"
    target.mkdir()

    skill = models.SkillInfo(
        name="Test Skill",
        description="Test",
        path=Path("irrelevant"),
        dir_name="to_remove",
    )

    # Act & Assert - KeyboardInterrupt should propagate
    with patch("shutil.rmtree", side_effect=KeyboardInterrupt()):
        with pytest.raises(KeyboardInterrupt):
            skills.remove_skill(skill, mock_dest_dir)
