"""Data models for skills manager"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class SkillInfo:
    name: str
    description: str
    path: Path
    dir_name: str
    type: Literal["script", "plugin"] = "script"

    @property
    def is_script(self) -> bool:
        return self.type == "script"

    @property
    def is_plugin(self) -> bool:
        return self.type == "plugin"