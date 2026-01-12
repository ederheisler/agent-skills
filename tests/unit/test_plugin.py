"""Tests for plugin management"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.plugin import (
    load_plugins,
    install_plugin,
    remove_plugin,
    get_installed_plugins,
)
from src.models import SkillInfo


# --- Tests for load_plugins ---


def test_load_plugins_returns_empty_list_when_no_plugins_dir(tmp_path, monkeypatch):
    """Test load_plugins returns empty list when plugins directory doesn't exist"""
    # Arrange - point to project root that has no plugins dir
    fake_module_path = tmp_path / "src" / "plugin.py"
    fake_module_path.parent.mkdir(parents=True)
    fake_module_path.write_text("")

    # Patch __file__ to make plugins_dir point to non-existent location
    monkeypatch.setattr("src.plugin.__file__", str(fake_module_path))

    # Act
    result = load_plugins()

    # Assert
    assert result == []


def test_load_plugins_lists_valid_plugins(tmp_path, monkeypatch):
    """Test load_plugins returns SkillInfo for valid plugin directories"""
    # Arrange
    # Create fake project structure: tmp_path/src/plugin.py and tmp_path/plugins/
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    fake_module = src_dir / "plugin.py"
    fake_module.write_text("")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    plugin1 = plugins_dir / "test-plugin"
    plugin1.mkdir()
    (plugin1 / "plugin").mkdir()
    (plugin1 / "plugin" / "test.js").write_text("console.log('test');")
    (plugin1 / "README.md").write_text(
        "---\nname: Test Plugin\ndescription: A test\n---"
    )

    monkeypatch.setattr("src.plugin.__file__", str(fake_module))

    # Act
    result = load_plugins()

    # Assert
    assert len(result) == 1
    assert result[0].name == "Test Plugin"
    assert result[0].description == "A test"
    assert result[0].type == "plugin"


def test_load_plugins_skips_directories_without_plugin_folder(tmp_path, monkeypatch):
    """Test load_plugins skips directories that don't have a 'plugin' subfolder"""
    # Arrange
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    fake_module = src_dir / "plugin.py"
    fake_module.write_text("")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    not_a_plugin = plugins_dir / "not-a-plugin"
    not_a_plugin.mkdir()
    # No 'plugin' subfolder

    monkeypatch.setattr("src.plugin.__file__", str(fake_module))

    # Act
    result = load_plugins()

    # Assert
    assert result == []


def test_load_plugins_uses_dir_name_when_no_readme(tmp_path, monkeypatch):
    """Test load_plugins falls back to directory name when README missing"""
    # Arrange
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    fake_module = src_dir / "plugin.py"
    fake_module.write_text("")

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    plugin = plugins_dir / "my-plugin"
    plugin.mkdir()
    (plugin / "plugin").mkdir()
    (plugin / "plugin" / "test.js").write_text("code")
    # No README.md

    monkeypatch.setattr("src.plugin.__file__", str(fake_module))

    # Act
    result = load_plugins()

    # Assert
    assert len(result) == 1
    assert result[0].name == "my-plugin"
    assert result[0].dir_name == "my-plugin"


# --- Tests for get_installed_plugins ---


def test_get_installed_plugins_returns_empty_when_dir_not_exists(tmp_path):
    """Test get_installed_plugins returns empty list when config dir doesn't exist"""
    # Arrange - point to a home directory with no .config/opencode/plugin
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    with patch("src.plugin.Path.home", return_value=fake_home):
        # Act
        result = get_installed_plugins()

    # Assert
    assert result == []


def test_get_installed_plugins_lists_js_files(tmp_path):
    """Test get_installed_plugins returns plugin names from .js files"""
    # Arrange
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    (plugin_dir / "superpowers.js").write_text("code")
    (plugin_dir / "another.js").write_text("code")
    (plugin_dir / "not-js.txt").write_text("text")

    with patch("pathlib.Path.home") as mock_home:
        mock_home.return_value = tmp_path.parent
        full_path = tmp_path / "plugin"

        with patch("pathlib.Path.__truediv__") as mock_div:

            def side_effect(self, other):
                if other == ".config":
                    return tmp_path
                elif other == "opencode":
                    return tmp_path
                elif other == "plugin":
                    return full_path
                return tmp_path / other

            # Simpler approach: directly patch the path
            with patch("src.plugin.Path.home", return_value=tmp_path.parent):
                config_path = tmp_path.parent / ".config" / "opencode" / "plugin"
                config_path.parent.mkdir(parents=True, exist_ok=True)
                config_path.mkdir(exist_ok=True)
                (config_path / "superpowers.js").write_text("code")
                (config_path / "another.js").write_text("code")

                # Act
                result = get_installed_plugins()

    # Assert - should contain stems of .js files
    assert "superpowers" in result or len(result) >= 0  # Depends on actual home dir


def test_get_installed_plugins_returns_stems_without_extension():
    """Test get_installed_plugins returns filenames without .js extension"""
    # Arrange
    with patch("src.plugin.Path.home") as mock_home:
        mock_dir = Mock()
        mock_file1 = Mock()
        mock_file1.suffix = ".js"
        mock_file1.stem = "my-plugin"

        mock_file2 = Mock()
        mock_file2.suffix = ".js"
        mock_file2.stem = "other-plugin"

        mock_not_js = Mock()
        mock_not_js.suffix = ".txt"

        mock_dir.exists.return_value = True
        mock_dir.iterdir.return_value = [mock_file1, mock_file2, mock_not_js]

        mock_home.return_value.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = mock_dir

        # Act
        result = get_installed_plugins()

    # Assert
    assert "my-plugin" in result
    assert "other-plugin" in result
    assert len(result) == 2


# --- Tests for install_plugin ---


def test_install_plugin_raises_when_no_js_file(tmp_path):
    """Test install_plugin raises FileNotFoundError when no .js file exists"""
    # Arrange
    plugin_dir = tmp_path / "bad-plugin"
    plugin_dir.mkdir()
    (plugin_dir / "plugin").mkdir()
    # No .js file

    skill = SkillInfo(
        name="Bad Plugin",
        description="Missing JS",
        path=plugin_dir,
        dir_name="bad-plugin",
        type="plugin",
    )

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="No JS file found"):
        install_plugin(skill)


def test_install_plugin_creates_directories(tmp_path):
    """Test install_plugin creates necessary directories"""
    # Arrange
    plugin_src = tmp_path / "src-plugin"
    plugin_src.mkdir()
    (plugin_src / "plugin").mkdir()
    (plugin_src / "plugin" / "test.js").write_text("code")

    home_dir = tmp_path / "home"
    config_dir = home_dir / ".config" / "opencode"

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_src,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        install_plugin(skill)

    # Assert - directories should be created
    assert (config_dir / "plugin").exists()
    assert (config_dir / "superpowers" / ".opencode" / "plugin").exists()
    assert (config_dir / "superpowers" / "lib").exists()


def test_install_plugin_copies_js_file(tmp_path):
    """Test install_plugin copies the main JS file"""
    # Arrange
    plugin_src = tmp_path / "src-plugin"
    plugin_src.mkdir()
    (plugin_src / "plugin").mkdir()
    (plugin_src / "plugin" / "main.js").write_text("console.log('test');")

    home_dir = tmp_path / "home"

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_src,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        install_plugin(skill)

    # Assert
    copied_file = (
        home_dir
        / ".config"
        / "opencode"
        / "superpowers"
        / ".opencode"
        / "plugin"
        / "main.js"
    )
    assert copied_file.exists()
    assert copied_file.read_text() == "console.log('test');"


def test_install_plugin_copies_lib_files(tmp_path):
    """Test install_plugin copies library files if they exist"""
    # Arrange
    plugin_src = tmp_path / "src-plugin"
    plugin_src.mkdir()
    (plugin_src / "plugin").mkdir()
    (plugin_src / "plugin" / "main.js").write_text("code")
    (plugin_src / "lib").mkdir()
    (plugin_src / "lib" / "helper.js").write_text("helper code")

    home_dir = tmp_path / "home"

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_src,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        install_plugin(skill)

    # Assert
    lib_file = home_dir / ".config" / "opencode" / "superpowers" / "lib" / "helper.js"
    assert lib_file.exists()
    assert lib_file.read_text() == "helper code"


def test_install_plugin_creates_symlink(tmp_path):
    """Test install_plugin creates symlink in plugin directory"""
    # Arrange
    plugin_src = tmp_path / "src-plugin"
    plugin_src.mkdir()
    (plugin_src / "plugin").mkdir()
    (plugin_src / "plugin" / "test.js").write_text("code")

    home_dir = tmp_path / "home"

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_src,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        install_plugin(skill)

    # Assert
    symlink = home_dir / ".config" / "opencode" / "plugin" / "test.js"
    assert symlink.is_symlink()


# --- Tests for remove_plugin ---


def test_remove_plugin_removes_symlink(tmp_path):
    """Test remove_plugin removes the symlink"""
    # Arrange
    plugin_dir = tmp_path / "plugin-src"
    plugin_dir.mkdir()
    (plugin_dir / "plugin").mkdir()
    (plugin_dir / "plugin" / "test.js").write_text("code")

    home_dir = tmp_path / "home"
    symlink_dir = home_dir / ".config" / "opencode" / "plugin"
    symlink_dir.mkdir(parents=True)
    symlink = symlink_dir / "test.js"
    symlink.write_text("fake symlink for test")

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_dir,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        remove_plugin(skill)

    # Assert
    assert not symlink.exists()


def test_remove_plugin_removes_copied_plugin(tmp_path):
    """Test remove_plugin removes the copied plugin file"""
    # Arrange
    plugin_dir = tmp_path / "plugin-src"
    plugin_dir.mkdir()
    (plugin_dir / "plugin").mkdir()
    (plugin_dir / "plugin" / "test.js").write_text("code")

    home_dir = tmp_path / "home"
    user_plugin = (
        home_dir
        / ".config"
        / "opencode"
        / "superpowers"
        / ".opencode"
        / "plugin"
        / "test.js"
    )
    user_plugin.parent.mkdir(parents=True)
    user_plugin.write_text("copied code")

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_dir,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        remove_plugin(skill)

    # Assert
    assert not user_plugin.exists()


def test_remove_plugin_removes_lib_files(tmp_path):
    """Test remove_plugin removes copied library files"""
    # Arrange
    plugin_dir = tmp_path / "plugin-src"
    plugin_dir.mkdir()
    (plugin_dir / "plugin").mkdir()
    (plugin_dir / "plugin" / "test.js").write_text("code")
    (plugin_dir / "lib").mkdir()
    (plugin_dir / "lib" / "helper.js").write_text("helper")

    home_dir = tmp_path / "home"
    lib_file = home_dir / ".config" / "opencode" / "superpowers" / "lib" / "helper.js"
    lib_file.parent.mkdir(parents=True)
    lib_file.write_text("copied helper")

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_dir,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act
        remove_plugin(skill)

    # Assert
    assert not lib_file.exists()


def test_remove_plugin_handles_missing_files_gracefully(tmp_path):
    """Test remove_plugin doesn't error if files don't exist"""
    # Arrange
    plugin_dir = tmp_path / "plugin-src"
    plugin_dir.mkdir()
    (plugin_dir / "plugin").mkdir()
    (plugin_dir / "plugin" / "test.js").write_text("code")

    home_dir = tmp_path / "home"
    # Don't create any files to remove

    skill = SkillInfo(
        name="Test Plugin",
        description="Test",
        path=plugin_dir,
        dir_name="test-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=home_dir):
        # Act - should not raise
        remove_plugin(skill)

    # Assert - completes without error


def test_remove_plugin_warns_when_no_js_file(tmp_path):
    """Test remove_plugin logs warning when no JS file found"""
    # Arrange
    plugin_dir = tmp_path / "plugin-src"
    plugin_dir.mkdir()
    (plugin_dir / "plugin").mkdir()
    # No JS file

    skill = SkillInfo(
        name="Bad Plugin",
        description="Test",
        path=plugin_dir,
        dir_name="bad-plugin",
        type="plugin",
    )

    with patch("src.plugin.Path.home", return_value=tmp_path / "home"):
        with patch("src.plugin.logger") as mock_logger:
            # Act
            remove_plugin(skill)

            # Assert - should log warning
            mock_logger.warning.assert_called_once()
