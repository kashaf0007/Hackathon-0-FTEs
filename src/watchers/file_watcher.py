"""File Watcher for Bronze Tier Constitutional FTE.

Proactively monitors for file events and creates tasks automatically.
"""

import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from src.watchers.base import BaseWatcher
from src.models import Task
from src.utils import format_markdown_task, atomic_write


class FileWatcherHandler(FileSystemEventHandler):
    """Handler for file system events.

    Processes file creation events and creates tasks.
    """

    def __init__(self, watcher: 'FileWatcher'):
        """Initialize handler.

        Args:
            watcher: Parent FileWatcher instance
        """
        self.watcher = watcher
        self.last_event_time = {}

    def on_created(self, event):
        """Handle file creation event.

        Args:
            event: File system event
        """
        if event.is_directory:
            print(f"[FileWatcher] Ignoring directory creation: {event.src_path}")
            return

        # Debounce: ignore events within 1 second of last event for same file
        file_path = event.src_path
        current_time = time.time()

        if file_path in self.last_event_time:
            if current_time - self.last_event_time[file_path] < 1.0:
                print(f"[FileWatcher] Debouncing duplicate event for: {file_path}")
                return  # Ignore duplicate event

        self.last_event_time[file_path] = current_time

        # Filter by pattern if specified
        if self.watcher.file_pattern:
            if not Path(file_path).match(self.watcher.file_pattern):
                print(f"[FileWatcher] File does not match pattern '{self.watcher.file_pattern}': {file_path}")
                return
            else:
                print(f"[FileWatcher] File matches pattern '{self.watcher.file_pattern}': {file_path}")

        # Create task for this event
        print(f"[FileWatcher] Processing file creation event: {file_path}")
        self.watcher.create_task_for_file(Path(file_path))


class FileWatcher(BaseWatcher):
    """File watcher implementation.

    Monitors a directory for file creation events and automatically
    creates tasks in Needs_Action/.
    """

    def __init__(
        self,
        name: str,
        monitored_path: Path,
        needs_action_path: Path,
        file_pattern: Optional[str] = None,
        task_type: str = "draft_email",
        enabled: bool = True
    ):
        """Initialize file watcher.

        Args:
            name: Watcher name
            monitored_path: Directory to monitor
            needs_action_path: Where to create task files
            file_pattern: File pattern to match (e.g., "*.txt")
            task_type: Type of task to create
            enabled: Whether watcher is active
        """
        super().__init__(name, enabled)
        self.monitored_path = Path(monitored_path)
        self.needs_action_path = Path(needs_action_path)
        self.file_pattern = file_pattern
        self.task_type = task_type
        self.observer: Optional[Observer] = None
        self.handler: Optional[FileWatcherHandler] = None
        self.task_counter = 0

        # Ensure directories exist
        self.monitored_path.mkdir(parents=True, exist_ok=True)
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        """Start the file watcher.

        Begins monitoring the directory for file creation events.
        """
        if not self.enabled:
            print(f"[FileWatcher] Watcher '{self.name}' is disabled")
            return

        if self.observer is not None:
            print(f"[FileWatcher] Watcher '{self.name}' is already running")
            return  # Already running

        try:
            # Validate monitored path exists and is accessible
            if not self.monitored_path.exists():
                print(f"[FileWatcher] Error: Monitored path does not exist: {self.monitored_path}")
                print(f"[FileWatcher] Creating directory: {self.monitored_path}")
                self.monitored_path.mkdir(parents=True, exist_ok=True)

            if not self.monitored_path.is_dir():
                print(f"[FileWatcher] Error: Monitored path is not a directory: {self.monitored_path}")
                return

            # Check read permissions
            import os
            if not os.access(self.monitored_path, os.R_OK):
                print(f"[FileWatcher] Error: No read permission for {self.monitored_path}")
                return

            # Create observer and handler
            self.observer = Observer()
            self.handler = FileWatcherHandler(self)

            # Schedule monitoring
            self.observer.schedule(
                self.handler,
                str(self.monitored_path),
                recursive=False
            )

            # Start observer thread
            self.observer.start()
            print(f"[FileWatcher] Started monitoring: {self.monitored_path}")

        except Exception as e:
            print(f"[FileWatcher] Error starting watcher: {str(e)}")
            import traceback
            traceback.print_exc()
            self.observer = None
            self.handler = None

    def stop(self) -> None:
        """Stop the file watcher.

        Stops monitoring and cleans up resources.
        """
        if self.observer is not None:
            try:
                print(f"[FileWatcher] Stopping watcher '{self.name}'...")
                self.observer.stop()
                self.observer.join(timeout=5)

                # Check if observer thread is still alive
                if self.observer.is_alive():
                    print(f"[FileWatcher] Warning: Observer thread did not stop within timeout")
                else:
                    print(f"[FileWatcher] Watcher '{self.name}' stopped successfully")

            except Exception as e:
                print(f"[FileWatcher] Error stopping watcher: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                self.observer = None
                self.handler = None

    def check(self) -> List[Task]:
        """Check for new events (not used with watchdog).

        Watchdog uses event-driven approach, so this returns empty list.

        Returns:
            Empty list (events handled by callbacks)
        """
        return []

    def create_task_for_file(self, file_path: Path) -> None:
        """Create task for detected file.

        Args:
            file_path: Path to detected file
        """
        try:
            # Validate file exists and is readable
            if not file_path.exists():
                print(f"[FileWatcher] Error: File does not exist: {file_path}")
                return

            if not file_path.is_file():
                print(f"[FileWatcher] Error: Path is not a file: {file_path}")
                return

            # Generate task ID
            self.task_counter += 1
            task_id = f"task-{self.task_counter:03d}"

            # Read file content with error handling
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    content = file_path.read_text(encoding='latin-1')
                except Exception as e:
                    content = f"[Could not read file content: {str(e)}]"
            except PermissionError:
                content = "[Permission denied reading file]"
            except Exception as e:
                content = f"[Error reading file: {str(e)}]"

            # Create task
            task_title = f"Draft Reply to {file_path.name}"
            task_content = format_markdown_task(
                title=task_title,
                task_type=self.task_type,
                priority="MEDIUM",
                created=datetime.now().isoformat(),
                status="PENDING",
                context=f"File detected: {file_path}\n\nContent:\n{content[:500]}...",
                expected_output="Draft reply saved to this file"
            )

            # Ensure needs_action_path exists and is writable
            import os
            self.needs_action_path.mkdir(parents=True, exist_ok=True)

            if not os.access(self.needs_action_path, os.W_OK):
                print(f"[FileWatcher] Error: No write permission for {self.needs_action_path}")
                return

            # Write task file
            task_file = self.needs_action_path / f"{task_id}.md"
            atomic_write(task_file, task_content)
            print(f"[FileWatcher] Created task: {task_file}")

        except Exception as e:
            print(f"[FileWatcher] Error creating task for {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()

    def is_running(self) -> bool:
        """Check if watcher is running.

        Returns:
            True if observer is active
        """
        return self.enabled and self.observer is not None and self.observer.is_alive()
