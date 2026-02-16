"""Watcher Configuration model for Bronze Tier Constitutional FTE."""

from pydantic import BaseModel, Field
from typing import Literal, Dict, Any


class WatcherConfig(BaseModel):
    """Watcher configuration.

    Defines a proactive monitoring system that creates tasks.
    Watchers detect events and automatically queue work.
    """

    name: str = Field(..., description="Watcher name (unique identifier)")
    type: Literal["file", "email", "schedule"] = Field(..., description="Watcher type")
    enabled: bool = Field(default=True, description="Whether watcher is active")
    trigger_conditions: Dict[str, Any] = Field(
        ...,
        description="When to trigger (path, pattern, event type, etc.)"
    )
    polling_interval: int = Field(
        default=60,
        ge=1,
        description="Seconds between checks (minimum 1)"
    )
    task_template: Dict[str, Any] = Field(
        ...,
        description="Template for created tasks (type, priority, context structure)"
    )

    class Config:
        validate_assignment = True

    def should_poll(self, seconds_since_last: int) -> bool:
        """Check if enough time has passed to poll again."""
        return seconds_since_last >= self.polling_interval
