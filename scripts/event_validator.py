"""
Event schema validator using jsonschema.
Validates event files against the standard event schema.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator


# Standard event schema based on contracts/event-schema.json
EVENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["event_id", "source", "type", "timestamp", "priority", "content", "created_at"],
    "properties": {
        "event_id": {
            "type": "string",
            "pattern": "^[0-9]{8}_[0-9]{6}_[a-z]+_[a-zA-Z0-9]+$"
        },
        "source": {
            "type": "string",
            "enum": ["gmail", "whatsapp", "linkedin", "filesystem", "calendar", "slack"]
        },
        "type": {
            "type": "string"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"]
        },
        "content": {
            "type": "object",
            "required": ["body"],
            "properties": {
                "subject": {"type": "string"},
                "body": {"type": "string", "minLength": 1},
                "from": {"type": "string"},
                "to": {"type": "string"},
                "attachments": {"type": "array"}
            }
        },
        "metadata": {
            "type": "object"
        },
        "created_at": {
            "type": "string",
            "format": "date-time"
        },
        "processed": {
            "type": "boolean"
        }
    }
}


class EventValidator:
    """Validates events against the standard schema."""

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize validator with schema.

        Args:
            schema: JSON schema dict (uses default if not provided)
        """
        self.schema = schema or EVENT_SCHEMA
        self.validator = Draft7Validator(self.schema)

    def validate_event(self, event: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate an event dictionary against the schema.

        Args:
            event: Event dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validate(instance=event, schema=self.schema)
            return True, None
        except ValidationError as e:
            return False, str(e.message)

    def validate_event_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate an event file against the schema.

        Args:
            file_path: Path to event JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                event = json.load(f)
            return self.validate_event(event)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except IOError as e:
            return False, f"File error: {str(e)}"

    def get_validation_errors(self, event: Dict[str, Any]) -> list[str]:
        """
        Get all validation errors for an event.

        Args:
            event: Event dictionary to validate

        Returns:
            List of error messages
        """
        errors = []
        for error in self.validator.iter_errors(event):
            errors.append(f"{'.'.join(str(p) for p in error.path)}: {error.message}")
        return errors


# Global validator instance
_validator = None


def get_validator() -> EventValidator:
    """Get or create the global validator instance."""
    global _validator
    if _validator is None:
        _validator = EventValidator()
    return _validator


def validate_event(event: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Convenience function to validate an event.

    Args:
        event: Event dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    return get_validator().validate_event(event)
