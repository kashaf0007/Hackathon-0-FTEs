"""Task model for Bronze Tier Constitutional FTE."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, Dict, Any


class Task(BaseModel):
    """Task entity for work items.

    Represents a unit of work to be executed by the orchestrator.
    Tasks flow through states: PENDING → IN_PROGRESS → COMPLETED/FAILED
    High-risk tasks may enter AWAITING_APPROVAL state.
    """

    task_id: str = Field(..., description="Unique task identifier (e.g., task-001)")
    title: str = Field(..., description="Human-readable task title")
    type: str = Field(..., description="Task type (e.g., draft_email, organize_files)")
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(default="MEDIUM", description="Task priority level")
    status: Literal["PENDING", "IN_PROGRESS", "AWAITING_APPROVAL", "APPROVED", "COMPLETED", "FAILED"] = Field(
        default="PENDING",
        description="Current task status"
    )
    created: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    started: Optional[datetime] = Field(None, description="Task start timestamp")
    completed: Optional[datetime] = Field(None, description="Completion timestamp")
    timeout_seconds: int = Field(default=300, description="Task timeout in seconds (default 5 minutes)")
    assigned_skill: Optional[str] = Field(None, description="Skill handling this task")
    retry_count: int = Field(default=0, ge=0, le=3, description="Number of retry attempts (max 3)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task-specific context data")
    expected_output: Optional[str] = Field(None, description="Description of expected result")
    actual_output: Optional[str] = Field(None, description="Actual result after execution")
    error_message: Optional[str] = Field(None, description="Error details if failed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < 3 and self.status == "FAILED"

    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = "IN_PROGRESS"
        self.updated = datetime.now()
        if not self.started:
            self.started = datetime.now()

    def mark_completed(self, output: str) -> None:
        """Mark task as completed with output."""
        self.status = "COMPLETED"
        self.completed = datetime.now()
        self.updated = datetime.now()
        self.actual_output = output

    def mark_failed(self, error: str) -> None:
        """Mark task as failed with error message."""
        self.status = "FAILED"
        self.updated = datetime.now()
        self.error_message = error
        self.retry_count += 1

    def is_timed_out(self) -> bool:
        """Check if task has exceeded timeout."""
        if not self.started or self.status not in ["IN_PROGRESS"]:
            return False

        elapsed = (datetime.now() - self.started).total_seconds()
        return elapsed > self.timeout_seconds

    def is_incomplete(self) -> bool:
        """Check if task is in incomplete state (started but not finished)."""
        return self.status == "IN_PROGRESS"
