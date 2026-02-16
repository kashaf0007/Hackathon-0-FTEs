"""Skill Definition model for Bronze Tier Constitutional FTE."""

from pydantic import BaseModel, Field
from typing import Literal, List


class SkillDefinition(BaseModel):
    """Skill definition metadata.

    Defines a capability of the FTE with metadata and execution logic.
    All skills must have a SKILL.md file following this schema.
    """

    name: str = Field(..., description="Skill name (matches directory name)")
    purpose: str = Field(..., description="What this skill does")
    constitutional_alignment: List[str] = Field(
        ...,
        description="Which principles this enforces (e.g., ['Local-First', 'HITL Safety'])"
    )
    inputs: List[str] = Field(..., description="What triggers this skill")
    outputs: List[str] = Field(..., description="Files created/modified")
    risk_classification: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        ...,
        description="Risk level of this skill's operations"
    )
    execution_logic: str = Field(..., description="Step-by-step execution flow")
    hitl_checkpoint: str = Field(..., description="When approval is required")
    logging_requirements: str = Field(..., description="What must be logged")
    failure_handling: str = Field(..., description="What happens on error")
    completion_condition: str = Field(..., description="When task is complete")

    class Config:
        validate_assignment = True

    def validate_required_sections(self) -> bool:
        """Validate that all required sections are non-empty."""
        required_fields = [
            self.name,
            self.purpose,
            self.execution_logic,
            self.hitl_checkpoint,
            self.logging_requirements,
            self.failure_handling,
            self.completion_condition
        ]
        return all(field and field.strip() for field in required_fields)

    def is_high_risk(self) -> bool:
        """Check if skill is classified as high risk."""
        return self.risk_classification == "HIGH"
