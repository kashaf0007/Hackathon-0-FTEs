"""Watchers package for Bronze Tier Constitutional FTE.

Contains watcher implementations for proactive monitoring.
"""

from .file_watcher import FileWatcher

__all__ = [
    "FileWatcher",
]
