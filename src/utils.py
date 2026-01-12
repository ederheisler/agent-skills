"""Utility functions"""
from pathlib import Path
from typing import Tuple


def load_frontmatter(file_path: Path) -> Tuple[str, str]:
    """Parse name and description from file frontmatter"""
    name = file_path.parent.name
    description = ""
    
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                content = f.read()

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

            for line in frontmatter_lines:
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip("\"'")
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    if (desc.startswith('"') and desc.endswith('"')) or (
                        desc.startswith("'") and desc.endswith("'")
                    ):
                        desc = desc[1:-1]
                    description = desc
        except Exception:
            pass
            
    return name, description
