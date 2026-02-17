"""
WatcherBase class - Base class for all watcher implementations.
Provides common polling logic, event normalization, and duplicate detection.
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from scripts.logger import get_logger
from scripts.event_queue import get_queue
from scripts.event_validator import get_validator


class WatcherBase(ABC):
    """
    Base class for all watchers (Gmail, WhatsApp, LinkedIn, etc.).

    Watchers are responsible for:
    1. Polling external sources for new events
    2. Detecting new events (with duplicate prevention)
    3. Normalizing events to standard format
    4. Creating event files in Needs_Action/
    5. Logging all detections

    Watchers must NOT execute actions - only detect and create task files.
    """

    def __init__(self, source: str, poll_interval: int = 600):
        """
        Initialize watcher.

        Args:
            source: Source identifier (gmail, whatsapp, linkedin, etc.)
            poll_interval: Polling interval in seconds (default: 600 = 10 minutes)
        """
        self.source = source
        self.poll_interval = poll_interval
        self.logger = get_logger()
        self.queue = get_queue()
        self.validator = get_validator()

        # Track seen event hashes to prevent duplicates
        self.seen_hashes: Set[str] = set()
        self.seen_hashes_file = Path(f"AI_Employee_Vault/Watchers/.{source}_seen.json")
        self._load_seen_hashes()

    def _load_seen_hashes(self) -> None:
        """Load previously seen event hashes from disk."""
        if self.seen_hashes_file.exists():
            try:
                with open(self.seen_hashes_file, 'r') as f:
                    data = json.load(f)
                    self.seen_hashes = set(data.get('hashes', []))
            except Exception:
                self.seen_hashes = set()

    def _save_seen_hashes(self) -> None:
        """Save seen event hashes to disk."""
        self.seen_hashes_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.seen_hashes_file, 'w') as f:
                json.dump({'hashes': list(self.seen_hashes)}, f)
        except Exception:
            pass

    def _compute_event_hash(self, event_data: Dict[str, Any]) -> str:
        """
        Compute hash of event for duplicate detection.

        Args:
            event_data: Raw event data from source

        Returns:
            SHA256 hash of event
        """
        # Create stable string representation
        stable_str = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(stable_str.encode()).hexdigest()

    def _is_duplicate(self, event_hash: str) -> bool:
        """
        Check if event has been seen before.

        Args:
            event_hash: Event hash

        Returns:
            True if duplicate, False if new
        """
        return event_hash in self.seen_hashes

    def _mark_as_seen(self, event_hash: str) -> None:
        """
        Mark event as seen.

        Args:
            event_hash: Event hash
        """
        self.seen_hashes.add(event_hash)

        # Limit size of seen hashes (keep last 1000)
        if len(self.seen_hashes) > 1000:
            # Remove oldest 100 hashes
            hashes_list = list(self.seen_hashes)
            self.seen_hashes = set(hashes_list[-900:])

        self._save_seen_hashes()

    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw event to standard format.

        Args:
            raw_event: Raw event data from source

        Returns:
            Normalized event dictionary
        """
        # Generate event ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import uuid
        unique_id = uuid.uuid4().hex[:6]
        event_id = f"{timestamp}_{self.source}_{unique_id}"

        # Build normalized event
        normalized = {
            "event_id": event_id,
            "source": self.source,
            "type": raw_event.get('type', 'unknown'),
            "timestamp": raw_event.get('timestamp', datetime.now().isoformat() + 'Z'),
            "priority": raw_event.get('priority', 'medium'),
            "content": {
                "subject": raw_event.get('subject', ''),
                "body": raw_event.get('body', ''),
                "from": raw_event.get('from', ''),
                "to": raw_event.get('to', ''),
                "attachments": raw_event.get('attachments', [])
            },
            "metadata": raw_event.get('metadata', {}),
            "created_at": datetime.now().isoformat() + 'Z',
            "processed": False
        }

        return normalized

    def create_event_file(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Create event file in Needs_Action/ directory.

        Args:
            event: Normalized event dictionary

        Returns:
            Event ID if created, None if validation failed
        """
        # Validate event
        is_valid, error = self.validator.validate_event(event)
        if not is_valid:
            self.logger.error(
                component="watcher",
                action="validation_failed",
                actor=self.source,
                target=event.get('event_id', 'unknown'),
                details={"error": error}
            )
            return None

        # Create event file via queue
        try:
            event_id = self.queue.push(event)

            # Log successful detection
            self.logger.info(
                component="watcher",
                action="event_detected",
                actor=self.source,
                target=event_id,
                details={
                    "event_type": event.get('type'),
                    "priority": event.get('priority'),
                    "from": event.get('content', {}).get('from')
                }
            )

            return event_id
        except Exception as e:
            self.logger.error(
                component="watcher",
                action="event_creation_failed",
                actor=self.source,
                target="queue",
                details={"error": str(e)}
            )
            return None

    @abstractmethod
    def fetch_new_events(self) -> List[Dict[str, Any]]:
        """
        Fetch new events from source (must be implemented by subclasses).

        Returns:
            List of raw event dictionaries

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement fetch_new_events()")

    def poll_once(self) -> int:
        """
        Poll source once for new events.

        Returns:
            Number of new events detected
        """
        start_time = time.time()

        try:
            # Fetch new events from source
            raw_events = self.fetch_new_events()

            new_events_count = 0

            for raw_event in raw_events:
                # Compute event hash for duplicate detection
                event_hash = self._compute_event_hash(raw_event)

                # Skip if duplicate
                if self._is_duplicate(event_hash):
                    continue

                # Normalize event
                normalized_event = self.normalize_event(raw_event)

                # Create event file
                event_id = self.create_event_file(normalized_event)

                if event_id:
                    # Mark as seen
                    self._mark_as_seen(event_hash)
                    new_events_count += 1

            duration_ms = int((time.time() - start_time) * 1000)

            # Log poll completion
            self.logger.info(
                component="watcher",
                action="poll_complete",
                actor=self.source,
                target="source",
                details={
                    "events_found": len(raw_events),
                    "new_events": new_events_count,
                    "duplicates_skipped": len(raw_events) - new_events_count
                },
                duration_ms=duration_ms
            )

            return new_events_count

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="poll_failed",
                actor=self.source,
                target="source",
                details={"error": str(e)}
            )
            return 0

    def run(self, max_iterations: Optional[int] = None) -> None:
        """
        Run watcher in continuous polling mode.

        Args:
            max_iterations: Maximum number of poll iterations (None = infinite)
        """
        iteration = 0

        self.logger.info(
            component="watcher",
            action="watcher_started",
            actor=self.source,
            target="source",
            details={"poll_interval": self.poll_interval}
        )

        try:
            while max_iterations is None or iteration < max_iterations:
                self.poll_once()
                iteration += 1

                if max_iterations is None or iteration < max_iterations:
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self.logger.info(
                component="watcher",
                action="watcher_stopped",
                actor=self.source,
                target="source",
                details={"iterations": iteration}
            )
