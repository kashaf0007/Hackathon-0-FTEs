"""Base Watcher interface for Bronze Tier Constitutional FTE.

All watchers must implement this interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.models import Task


class BaseWatcher(ABC):
    """Base class for all watchers.

    Watchers proactively monitor for events and create tasks.
    They enable autonomous operation without manual intervention.
    """

    def __init__(self, name: str, enabled: bool = True):
        """Initialize watcher.

        Args:
            name: Watcher name (unique identifier)
            enabled: Whether watcher is active
        """
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def start(self) -> None:
        """Start the watcher.

        Begin monitoring for events.
        Should be non-blocking (use threads if needed).
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the watcher.

        Stop monitoring and clean up resources.
        Should gracefully shut down any threads.
        """
        pass

    @abstractmethod
    def check(self) -> List[Task]:
        """Check for new events and create tasks.

        This method is called periodically by the orchestrator.

        Returns:
            List of tasks created from detected events
        """
        pass

    def is_running(self) -> bool:
        """Check if watcher is currently running.

        Returns:
            True if watcher is active and monitoring
        """
        return self.enabled

    def __repr__(self) -> str:
        """String representation of watcher."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.__class__.__name__}(name={self.name}, {status})"
