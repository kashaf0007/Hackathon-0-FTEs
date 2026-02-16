"""Base Skill interface for Bronze Tier Constitutional FTE.

All skills must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pathlib import Path

from src.models import Task, LogEntry


class BaseSkill(ABC):
    """Base class for all skills.

    Skills are capabilities of the FTE that can execute tasks.
    Each skill must have a SKILL.md file defining its metadata.
    """

    def __init__(self, skill_path: Path):
        """Initialize skill.

        Args:
            skill_path: Path to skill directory (contains SKILL.md)
        """
        self.skill_path = skill_path
        self.name = skill_path.name
        self.skill_md_path = skill_path / "SKILL.md"

        if not self.skill_md_path.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    @abstractmethod
    def execute(self, task: Task, dry_run: bool = False) -> Dict[str, Any]:
        """Execute the skill for a given task.

        Args:
            task: Task to execute
            dry_run: If True, simulate execution without making changes

        Returns:
            Dictionary with execution results:
            - success: bool
            - output: str (result description)
            - error: Optional[str] (error message if failed)

        Raises:
            Exception: If execution fails critically
        """
        pass

    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """Check if this skill can handle the given task.

        Args:
            task: Task to check

        Returns:
            True if skill can handle this task type
        """
        pass

    def get_risk_level(self, task: Task) -> str:
        """Get risk level for this task.

        Default implementation returns LOW.
        Override in subclasses for different risk levels.

        Args:
            task: Task to evaluate

        Returns:
            Risk level: LOW, MEDIUM, or HIGH
        """
        return "LOW"

    def __repr__(self) -> str:
        """String representation of skill."""
        return f"{self.__class__.__name__}(name={self.name})"
