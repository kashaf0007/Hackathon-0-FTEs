"""
File locking utilities for cross-platform file operations.
Supports both Unix (fcntl) and Windows (msvcrt) file locking.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

# Import platform-specific locking modules
if sys.platform == 'win32':
    import msvcrt
else:
    import fcntl


class FileLock:
    """
    Cross-platform file locking context manager.

    Usage:
        with FileLock('/path/to/file.txt') as f:
            # File is locked, perform operations
            content = f.read()
    """

    def __init__(self, file_path: str, mode: str = 'r', timeout: float = 30.0):
        """
        Initialize file lock.

        Args:
            file_path: Path to file to lock
            mode: File open mode ('r', 'w', 'a', etc.)
            timeout: Maximum time to wait for lock (seconds)
        """
        self.file_path = Path(file_path)
        self.mode = mode
        self.timeout = timeout
        self.file_handle: Optional[object] = None

    def __enter__(self):
        """Acquire lock and open file."""
        start_time = time.time()

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Open file
        self.file_handle = open(self.file_path, self.mode, encoding='utf-8')

        # Try to acquire lock with timeout
        while True:
            try:
                if sys.platform == 'win32':
                    # Windows: lock entire file
                    msvcrt.locking(self.file_handle.fileno(), msvcrt.LK_NBLCK, os.path.getsize(self.file_path.as_posix()) or 1)
                else:
                    # Unix: use fcntl
                    fcntl.flock(self.file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (IOError, OSError):
                # Lock not available
                if time.time() - start_time > self.timeout:
                    self.file_handle.close()
                    raise TimeoutError(f"Could not acquire lock on {self.file_path} within {self.timeout} seconds")
                time.sleep(0.1)

        return self.file_handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock and close file."""
        if self.file_handle:
            try:
                if sys.platform == 'win32':
                    # Windows: unlock file
                    msvcrt.locking(self.file_handle.fileno(), msvcrt.LK_UNLCK, os.path.getsize(self.file_path.as_posix()) or 1)
                else:
                    # Unix: release lock
                    fcntl.flock(self.file_handle.fileno(), fcntl.LOCK_UN)
            except (IOError, OSError):
                pass  # Lock may already be released
            finally:
                self.file_handle.close()


def atomic_write(file_path: str, content: str) -> None:
    """
    Write content to file atomically using temp file + rename.

    Args:
        file_path: Path to target file
        content: Content to write
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file
    temp_path = path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Atomic rename
    temp_path.replace(path)


def atomic_write_json(file_path: str, data: dict) -> None:
    """
    Write JSON data to file atomically.

    Args:
        file_path: Path to target file
        data: Dictionary to write as JSON
    """
    import json
    content = json.dumps(data, indent=2, ensure_ascii=False)
    atomic_write(file_path, content)


def safe_read(file_path: str, default: str = "") -> str:
    """
    Safely read file with lock, return default if file doesn't exist.

    Args:
        file_path: Path to file
        default: Default value if file doesn't exist

    Returns:
        File content or default
    """
    path = Path(file_path)
    if not path.exists():
        return default

    try:
        with FileLock(file_path, mode='r') as f:
            return f.read()
    except Exception:
        return default


def safe_read_json(file_path: str, default: dict = None) -> dict:
    """
    Safely read JSON file with lock, return default if file doesn't exist.

    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist

    Returns:
        Parsed JSON or default
    """
    import json
    if default is None:
        default = {}

    content = safe_read(file_path, "")
    if not content:
        return default

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return default
