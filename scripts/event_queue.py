"""
EventQueue class for managing event files with atomic operations.
Handles event creation, retrieval, and lifecycle management.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from scripts.file_utils import atomic_write_json, FileLock


class EventQueue:
    """
    File-based event queue for AI Employee system.
    Events are stored as JSON files in AI_Employee_Vault/Needs_Action/
    """

    def __init__(self, queue_dir: str = "AI_Employee_Vault/Needs_Action"):
        """
        Initialize event queue.

        Args:
            queue_dir: Directory to store event files
        """
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def push(self, event: Dict[str, Any]) -> str:
        """
        Add event to queue with atomic write.

        Args:
            event: Event dictionary (must contain 'source' field)

        Returns:
            Event ID (filename without extension)

        Raises:
            ValueError: If event is missing required fields
        """
        # Validate required fields
        if 'source' not in event:
            raise ValueError("Event must contain 'source' field")

        # Generate event ID if not present
        if 'event_id' not in event:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            source = event['source']
            unique_id = uuid.uuid4().hex[:6]
            event['event_id'] = f"{timestamp}_{source}_{unique_id}"

        # Ensure created_at timestamp
        if 'created_at' not in event:
            event['created_at'] = datetime.now().isoformat() + 'Z'

        # Ensure processed flag
        if 'processed' not in event:
            event['processed'] = False

        # Write event file atomically
        event_file = self.queue_dir / f"{event['event_id']}.json"
        atomic_write_json(str(event_file), event)

        return event['event_id']

    def pop(self) -> Optional[tuple[Dict[str, Any], Path]]:
        """
        Get next event from queue (FIFO order).

        Returns:
            Tuple of (event_dict, event_file_path) or None if queue is empty
        """
        # Get all event files sorted by name (timestamp-based)
        event_files = sorted(self.queue_dir.glob('*.json'))

        if not event_files:
            return None

        # Get first event file
        event_file = event_files[0]

        try:
            # Read with lock to prevent concurrent access
            with FileLock(str(event_file), mode='r') as f:
                event = json.load(f)
            return event, event_file
        except Exception:
            # If file is corrupted or locked, skip it
            return None

    def peek(self) -> Optional[Dict[str, Any]]:
        """
        View next event without removing it from queue.

        Returns:
            Event dictionary or None if queue is empty
        """
        result = self.pop()
        if result:
            return result[0]
        return None

    def move_to_done(self, event_file: Path) -> None:
        """
        Move processed event to Done/ directory.

        Args:
            event_file: Path to event file
        """
        done_dir = Path('AI_Employee_Vault/Done')
        done_dir.mkdir(parents=True, exist_ok=True)

        # Move file to Done/
        target = done_dir / event_file.name
        event_file.rename(target)

    def move_to_pending_approval(self, event_file: Path) -> None:
        """
        Move event requiring approval to Pending_Approval/ directory.

        Args:
            event_file: Path to event file
        """
        pending_dir = Path('AI_Employee_Vault/Pending_Approval')
        pending_dir.mkdir(parents=True, exist_ok=True)

        # Move file to Pending_Approval/
        target = pending_dir / event_file.name
        event_file.rename(target)

    def get_queue_size(self) -> int:
        """
        Get number of events in queue.

        Returns:
            Number of event files
        """
        return len(list(self.queue_dir.glob('*.json')))

    def list_events(self) -> List[str]:
        """
        List all event IDs in queue.

        Returns:
            List of event IDs (filenames without extension)
        """
        return [f.stem for f in sorted(self.queue_dir.glob('*.json'))]

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event dictionary or None if not found
        """
        event_file = self.queue_dir / f"{event_id}.json"
        if not event_file.exists():
            return None

        try:
            with open(event_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def delete_event(self, event_id: str) -> bool:
        """
        Delete event from queue.

        Args:
            event_id: Event ID

        Returns:
            True if deleted, False if not found
        """
        event_file = self.queue_dir / f"{event_id}.json"
        if event_file.exists():
            event_file.unlink()
            return True
        return False


# Global queue instance
_queue = None


def get_queue() -> EventQueue:
    """Get or create the global event queue instance."""
    global _queue
    if _queue is None:
        _queue = EventQueue()
    return _queue


# Alias for compatibility
def get_event_queue() -> EventQueue:
    """Get or create the global event queue instance (alias)."""
    return get_queue()
