"""Data models for skills manager"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillInfo:
    name: str
    description: str
    path: Path
    dir_name: str
