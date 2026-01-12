"""Skills listing and management"""

import logging
import shutil
from pathlib import Path
from typing import List, Set

from .models import SkillInfo
from .plugin import get_installed_plugins, load_plugins
from .utils import load_frontmatter

logger = logging.getLogger(__name__)


def get_skill_info(skill_dir: Path) -> SkillInfo:
    """Extract skill name and description from SKILL.md frontmatter"""
    skill_file = skill_dir / "SKILL.md"
    name = skill_dir.name
    description = ""

    if skill_file.exists():
        name_fm, desc_fm = load_frontmatter(skill_file)
        name = name_fm or name
        description = desc_fm

    return SkillInfo(
        name=name,
        description=description,
        path=skill_dir,
        dir_name=skill_dir.name,
    )


def load_skills(skills_dir: Path) -> List[SkillInfo]:
    """List all available skills, sorted by name, with plugins first"""
    skills = []

    # Load plugins dynamically
    plugins = load_plugins()
    skills.extend(plugins)

    # Add separator
    separator_skill = SkillInfo(name="", description="", path=Path(""), dir_name="")
    skills.append(separator_skill)

    # Add regular skills (sorted by name)
    regular_skills = []
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir():
                regular_skills.append(get_skill_info(skill_dir))

    regular_skills.sort(key=lambda s: s.name)
    skills.extend(regular_skills)

    return skills


def get_installed_skills(destination: Path) -> Set[str]:
    """Get installed skill names"""
    installed = set()
    if destination.exists():
        installed.update({d.name for d in destination.iterdir() if d.is_dir()})

    # Add installed plugins
    installed.update(get_installed_plugins())

    return installed


def install_skill(skill: SkillInfo, destination: Path) -> bool:
    """Install a regular skill"""
    try:
        dest_path = destination / skill.dir_name
        if dest_path.exists():
            shutil.rmtree(dest_path)
        shutil.copytree(skill.path, dest_path)
        logger.info(f"✓ Installed {skill.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to install {skill.name}: {e}")
        return False


def remove_skill(skill: SkillInfo, destination: Path) -> bool:
    """Remove a regular skill"""
    try:
        dest_path = destination / skill.dir_name
        if dest_path.exists():
            shutil.rmtree(dest_path)
            logger.info(f"✓ Removed {skill.name}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to remove {skill.name}: {e}")
        return False
