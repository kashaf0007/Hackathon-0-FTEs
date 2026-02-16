"""Schema validation utilities for Bronze Tier Constitutional FTE.

Provides validation helpers for Pydantic models and JSON schemas.
"""

from typing import Type, Any, Dict, List
from pydantic import BaseModel, ValidationError


def validate_model(model_class: Type[BaseModel], data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate data against Pydantic model.

    Args:
        model_class: Pydantic model class
        data: Data to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> from src.models import Task
        >>> data = {"task_id": "task-001", "title": "Test", "type": "test"}
        >>> is_valid, errors = validate_model(Task, data)
        >>> is_valid
        True
    """
    try:
        model_class(**data)
        return True, []
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return False, errors


def validate_skill_sections(sections: Dict[str, str]) -> tuple[bool, List[str]]:
    """Validate SKILL.md has all required sections.

    Args:
        sections: Dictionary of section names to content

    Returns:
        Tuple of (is_valid, missing_sections)
    """
    required_sections = [
        "Purpose",
        "Constitutional Alignment",
        "Inputs",
        "Outputs",
        "Risk Classification",
        "Execution Logic",
        "HITL Checkpoint",
        "Logging Requirements",
        "Failure Handling",
        "Completion Condition"
    ]

    missing = []
    for section in required_sections:
        if section not in sections or not sections[section].strip():
            missing.append(section)

    return len(missing) == 0, missing


def validate_risk_level(risk_level: str) -> bool:
    """Validate risk level is one of allowed values.

    Args:
        risk_level: Risk level string

    Returns:
        True if valid, False otherwise
    """
    return risk_level in ["LOW", "MEDIUM", "HIGH"]


def validate_task_status(status: str) -> bool:
    """Validate task status is one of allowed values.

    Args:
        status: Status string

    Returns:
        True if valid, False otherwise
    """
    return status in ["PENDING", "IN_PROGRESS", "AWAITING_APPROVAL", "APPROVED", "COMPLETED", "FAILED"]


def validate_approval_status(status: str) -> bool:
    """Validate approval status is one of allowed values.

    Args:
        status: Status string

    Returns:
        True if valid, False otherwise
    """
    return status in ["PENDING", "APPROVED", "REJECTED"]
