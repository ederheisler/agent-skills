"""Tests for persistence layer"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.persistence import (
    load_state,
    save_state,
    get_last_destination,
    set_last_destination,
    DB_FILE,
)


# --- Tests for load_state ---


def test_load_state_returns_empty_dict_when_file_not_exists(tmp_path):
    """Test load_state returns empty dict when db.json doesn't exist"""
    # Arrange - change working directory
    with patch.object(Path, "exists", return_value=False):
        # Act
        result = load_state()

    # Assert
    assert result == {}


def test_load_state_reads_valid_json(tmp_path):
    """Test load_state successfully reads valid JSON data"""
    # Arrange
    test_data = {"last_destination": "/some/path", "other_key": "value"}

    with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = load_state()

    # Assert
    assert result == test_data


def test_load_state_handles_empty_file(tmp_path):
    """Test load_state handles empty JSON file"""
    # Arrange - empty file should parse as error and return {}
    with patch("builtins.open", mock_open(read_data="")):
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = load_state()

    # Assert - should return empty dict on parse error
    assert result == {}


def test_load_state_handles_invalid_json(tmp_path):
    """Test load_state handles malformed JSON gracefully"""
    # Arrange
    with patch("builtins.open", mock_open(read_data="not valid json {")):
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = load_state()

    # Assert - should return empty dict on parse error
    assert result == {}


def test_load_state_handles_read_permission_error():
    """Test load_state handles file read permission errors"""
    # Arrange
    with patch.object(Path, "exists", return_value=True):
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            # Act
            result = load_state()

    # Assert - should return empty dict on error
    assert result == {}


# --- Tests for save_state ---


def test_save_state_writes_json_to_file(tmp_path):
    """Test save_state writes state dictionary to db.json"""
    # Arrange
    test_state = {"last_destination": "/test/path", "count": 42}
    mock_file = mock_open()

    with patch("builtins.open", mock_file):
        # Act
        save_state(test_state)

    # Assert - verify file was opened for writing
    mock_file.assert_called_once_with(DB_FILE, "w")

    # Verify JSON was written
    handle = mock_file()
    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    parsed = json.loads(written_content)
    assert parsed == test_state


def test_save_state_formats_json_with_indent(tmp_path):
    """Test save_state formats JSON with proper indentation"""
    # Arrange
    test_state = {"key": "value"}
    mock_file = mock_open()

    with patch("builtins.open", mock_file):
        # Act
        save_state(test_state)

    # Assert - verify indented JSON
    handle = mock_file()
    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    assert "\n" in written_content  # Should have newlines from indent


def test_save_state_handles_write_error():
    """Test save_state handles write errors gracefully"""
    # Arrange
    test_state = {"data": "value"}

    with patch("builtins.open", side_effect=IOError("Disk full")):
        # Act - should not raise exception
        save_state(test_state)

    # Assert - function completes without raising


def test_save_state_handles_permission_error():
    """Test save_state handles permission errors"""
    # Arrange
    test_state = {"data": "value"}

    with patch("builtins.open", side_effect=PermissionError("Access denied")):
        # Act - should not raise exception
        save_state(test_state)

    # Assert - function completes without raising


def test_save_state_with_empty_dict():
    """Test save_state can save empty dictionary"""
    # Arrange
    mock_file = mock_open()

    with patch("builtins.open", mock_file):
        # Act
        save_state({})

    # Assert - verify empty dict was written
    handle = mock_file()
    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    parsed = json.loads(written_content)
    assert parsed == {}


# --- Tests for get_last_destination ---


def test_get_last_destination_returns_path_when_exists():
    """Test get_last_destination returns Path when last_destination exists in state"""
    # Arrange
    test_path = "/home/user/skills"
    mock_state = {"last_destination": test_path}

    with patch("src.persistence.load_state", return_value=mock_state):
        # Act
        result = get_last_destination()

    # Assert
    assert result == Path(test_path)


def test_get_last_destination_returns_none_when_not_in_state():
    """Test get_last_destination returns None when key not in state"""
    # Arrange
    with patch("src.persistence.load_state", return_value={}):
        # Act
        result = get_last_destination()

    # Assert
    assert result is None


def test_get_last_destination_returns_none_when_value_is_none():
    """Test get_last_destination returns None when value is None"""
    # Arrange
    with patch("src.persistence.load_state", return_value={"last_destination": None}):
        # Act
        result = get_last_destination()

    # Assert
    assert result is None


def test_get_last_destination_returns_none_when_value_is_empty_string():
    """Test get_last_destination returns None for empty string"""
    # Arrange
    with patch("src.persistence.load_state", return_value={"last_destination": ""}):
        # Act
        result = get_last_destination()

    # Assert
    assert result is None


def test_get_last_destination_handles_relative_path():
    """Test get_last_destination converts relative path to Path object"""
    # Arrange
    with patch(
        "src.persistence.load_state", return_value={"last_destination": "./skills"}
    ):
        # Act
        result = get_last_destination()

    # Assert
    assert result == Path("./skills")
    assert isinstance(result, Path)


# --- Tests for set_last_destination ---


def test_set_last_destination_saves_path_as_string():
    """Test set_last_destination converts Path to string and saves"""
    # Arrange
    test_path = Path("/home/user/skills")
    mock_state = {}

    with patch("src.persistence.load_state", return_value=mock_state.copy()):
        with patch("src.persistence.save_state") as mock_save:
            # Act
            set_last_destination(test_path)

    # Assert
    mock_save.assert_called_once()
    saved_state = mock_save.call_args[0][0]
    assert saved_state["last_destination"] == str(test_path)


def test_set_last_destination_preserves_existing_state():
    """Test set_last_destination preserves other keys in state"""
    # Arrange
    test_path = Path("/new/path")
    existing_state = {"other_key": "other_value", "count": 42}

    with patch("src.persistence.load_state", return_value=existing_state.copy()):
        with patch("src.persistence.save_state") as mock_save:
            # Act
            set_last_destination(test_path)

    # Assert
    saved_state = mock_save.call_args[0][0]
    assert saved_state["other_key"] == "other_value"
    assert saved_state["count"] == 42
    assert saved_state["last_destination"] == str(test_path)


def test_set_last_destination_overwrites_previous_destination():
    """Test set_last_destination overwrites existing last_destination"""
    # Arrange
    old_path = "/old/path"
    new_path = Path("/new/path")
    existing_state = {"last_destination": old_path}

    with patch("src.persistence.load_state", return_value=existing_state.copy()):
        with patch("src.persistence.save_state") as mock_save:
            # Act
            set_last_destination(new_path)

    # Assert
    saved_state = mock_save.call_args[0][0]
    assert saved_state["last_destination"] == str(new_path)


def test_set_last_destination_with_relative_path():
    """Test set_last_destination handles relative paths"""
    # Arrange
    test_path = Path("./relative/path")

    with patch("src.persistence.load_state", return_value={}):
        with patch("src.persistence.save_state") as mock_save:
            # Act
            set_last_destination(test_path)

    # Assert - Path normalizes ./relative/path to relative/path
    saved_state = mock_save.call_args[0][0]
    assert saved_state["last_destination"] == "relative/path"


# --- Integration tests ---


def test_round_trip_save_and_load(tmp_path):
    """Test saving and loading state works end-to-end"""
    # Arrange
    test_db = tmp_path / "test_db.json"
    test_path = Path("/test/destination")

    with patch("src.persistence.DB_FILE", test_db):
        # Act - save state
        with patch("src.persistence.load_state", return_value={}):
            with patch("src.persistence.save_state") as mock_save:
                set_last_destination(test_path)

        # Verify the saved state structure
        saved_state = mock_save.call_args[0][0]
        assert "last_destination" in saved_state

        # Simulate loading it back
        with patch("src.persistence.load_state", return_value=saved_state):
            result = get_last_destination()

    # Assert
    assert result == test_path
