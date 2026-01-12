"""Utility functions"""

from pathlib import Path
from typing import Tuple


def _extract_frontmatter_lines(content: str) -> list[str]:
    """Extract lines between --- delimiters"""
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break
            continue
        if in_frontmatter:
            frontmatter_lines.append(line)

    return frontmatter_lines


def _parse_quoted_value(value: str) -> str:
    """Remove surrounding quotes from a string"""
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_frontmatter_field(line: str, field_name: str) -> str | None:
    """Parse a single frontmatter field line, returning None if not found"""
    if not line.startswith(f"{field_name}:"):
        return None

    value = line.split(":", 1)[1]
    return _parse_quoted_value(value)


def load_frontmatter(file_path: Path) -> Tuple[str, str]:
    """Parse name and description from file frontmatter"""
    name = file_path.parent.name
    description = ""

    if not file_path.exists():
        return name, description

    try:
        with open(file_path, "r") as f:
            content = f.read()

        frontmatter_lines = _extract_frontmatter_lines(content)

        for line in frontmatter_lines:
            if parsed_name := _parse_frontmatter_field(line, "name"):
                name = parsed_name or file_path.parent.name
            elif parsed_desc := _parse_frontmatter_field(line, "description"):
                description = parsed_desc

    except Exception:
        pass

    return name, description
