# Research & Technology Validation

**Feature**: Bronze Tier Constitutional FTE
**Date**: 2026-02-16
**Phase**: 0 (Research)

## Overview

This document captures technology decisions, best practices research, and pattern validation for the Bronze Tier Constitutional FTE implementation. All technical context items from plan.md have been validated and documented here.

## Technology Stack Validation

### Python 3.11+ Selection

**Decision**: Use Python 3.11+ as the implementation language

**Research Findings**:
- Python 3.11+ provides excellent file I/O performance (critical for file-based operations)
- Strong ecosystem for CLI applications and file system monitoring
- Native support for type hints and Pydantic integration
- Cross-platform compatibility (Windows, Linux, macOS)
- Existing project already uses Python (pyproject.toml detected)

**Best Practices**:
- Use pathlib for cross-platform file path handling
- Leverage type hints for better IDE support and validation
- Use context managers for file operations (automatic cleanup)
- Implement proper exception handling for file I/O errors

**Alternatives Considered**:
- Node.js: Rejected (less suitable for file-heavy operations, callback complexity)
- Go: Rejected (overkill for Bronze tier, steeper learning curve)
- Rust: Rejected (too complex for rapid prototyping)

### Dependency Selection

#### 1. python-dotenv (Environment Variables)

**Purpose**: Load environment variables from .env file

**Research Findings**:
- Industry standard for Python environment management
- Simple API: `load_dotenv()` automatically loads .env
- Supports variable expansion and multiline values
- No external dependencies

**Usage Pattern**:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file
dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
```

**Best Practices**:
- Call `load_dotenv()` at application startup
- Provide sensible defaults with `os.getenv(key, default)`
- Never log environment variable values
- Always include .env in .gitignore

#### 2. watchdog (File System Monitoring)

**Purpose**: Monitor file system events for proactive watchers

**Research Findings**:
- Cross-platform file system event monitoring
- Supports recursive directory watching
- Event types: created, modified, deleted, moved
- Efficient (uses OS-native APIs: inotify, FSEvents, ReadDirectoryChangesW)

**Usage Pattern**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TaskWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # Handle new file in monitored directory

observer = Observer()
observer.schedule(TaskWatcher(), path="./monitored", recursive=False)
observer.start()
```

**Best Practices**:
- Use separate thread for observer (non-blocking)
- Filter events by file extension or pattern
- Debounce rapid events (avoid duplicate processing)
- Graceful shutdown with observer.stop() and observer.join()

**Note**: For Bronze tier, watchdog is used only for demo workflow watcher. Main orchestrator uses simple polling for task queue.

#### 3. Pydantic (Data Validation)

**Purpose**: Schema validation for tasks, logs, and approval requests

**Research Findings**:
- Runtime data validation with type hints
- Automatic JSON serialization/deserialization
- Clear validation error messages
- Excellent performance (Rust-based core in v2)

**Usage Pattern**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class Task(BaseModel):
    task_id: str
    type: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    created: datetime
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Best Practices**:
- Use Field() for validation constraints and descriptions
- Leverage Literal types for enums
- Implement custom validators with @validator decorator
- Use model_validate() for parsing untrusted data

#### 4. pytest (Testing Framework)

**Purpose**: Unit and integration testing

**Research Findings**:
- Industry standard Python testing framework
- Rich plugin ecosystem (pytest-cov for coverage)
- Fixture system for test setup/teardown
- Parametrized tests for multiple scenarios

**Usage Pattern**:
```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_vault(tmp_path):
    """Create temporary AI_Employee_Vault structure"""
    vault = tmp_path / "AI_Employee_Vault"
    (vault / "Needs_Action").mkdir(parents=True)
    (vault / "Done").mkdir(parents=True)
    return vault

def test_task_processing(temp_vault):
    # Test with temporary vault
    pass
```

**Best Practices**:
- Use fixtures for common setup (temp directories, mock data)
- Parametrize tests for multiple input scenarios
- Aim for >80% code coverage
- Separate unit tests (fast) from integration tests (slower)

## File System Patterns

### Atomic File Operations

**Challenge**: Prevent partial writes and race conditions

**Solution**: Write to temporary file, then atomic rename

**Implementation**:
```python
from pathlib import Path
import tempfile
import shutil

def atomic_write(path: Path, content: str):
    """Write file atomically to prevent partial reads"""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (same filesystem)
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp"
    )

    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)

        # Atomic rename (POSIX guarantees atomicity)
        shutil.move(temp_path, path)
    except:
        # Clean up temp file on error
        Path(temp_path).unlink(missing_ok=True)
        raise
```

**Best Practices**:
- Always create temp file in same directory (same filesystem)
- Use try/except to clean up temp file on error
- On Windows, may need to remove target first (not atomic)
- For critical operations, consider file locking

### File Locking for Concurrent Access

**Challenge**: Multiple processes/threads accessing same file

**Solution**: Use fcntl (Unix) or msvcrt (Windows) for file locking

**Implementation**:
```python
import fcntl  # Unix
import msvcrt  # Windows
import platform

def lock_file(file_obj):
    """Cross-platform file locking"""
    if platform.system() == "Windows":
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_LOCK, 1)
    else:
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_EX)

def unlock_file(file_obj):
    """Cross-platform file unlocking"""
    if platform.system() == "Windows":
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
```

**Best Practices**:
- Use context managers for automatic unlock
- Set timeout for lock acquisition (avoid deadlock)
- For Bronze tier, simple retry logic sufficient
- Consider advisory locks (cooperative locking)

**Note**: For Bronze tier with single orchestrator process, file locking is optional. Implement if concurrent access becomes an issue.

### JSON Log Rotation

**Challenge**: Prevent unbounded log file growth

**Solution**: Daily log files with automatic rotation

**Implementation**:
```python
from datetime import datetime
from pathlib import Path
import json

class DailyLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, entry: dict):
        """Append entry to today's log file"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{today}.json"

        # Read existing entries
        entries = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                entries = json.load(f)

        # Append new entry
        entries.append(entry)

        # Write atomically
        atomic_write(log_file, json.dumps(entries, indent=2))
```

**Best Practices**:
- Use ISO 8601 date format (YYYY-MM-DD) for filenames
- Store as JSON array for easy parsing
- Consider archiving logs older than 30 days
- Implement log compression for long-term storage

**Optimization**: For high-volume logging, consider append-only format (one JSON object per line) to avoid reading entire file.

### Markdown Parsing and Validation

**Challenge**: Parse task files in markdown format

**Solution**: Use frontmatter + markdown body pattern

**Implementation**:
```python
import re
from typing import Dict, Any

def parse_task_file(content: str) -> Dict[str, Any]:
    """Parse markdown task file with metadata"""
    lines = content.split('\n')

    # Extract title (first # heading)
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Extract metadata (bold key-value pairs)
    metadata = {}
    for line in lines:
        match = re.match(r'\*\*(\w+)\*\*:\s*(.+)', line)
        if match:
            key, value = match.groups()
            metadata[key.lower()] = value.strip()

    # Extract sections (## headings)
    sections = {}
    current_section = None
    section_content = []

    for line in lines:
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(section_content).strip()
            current_section = line[3:].strip()
            section_content = []
        elif current_section:
            section_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(section_content).strip()

    return {
        'title': title,
        'metadata': metadata,
        'sections': sections
    }
```

**Best Practices**:
- Use consistent markdown structure for all task files
- Validate required fields after parsing
- Provide clear error messages for malformed files
- Consider using python-frontmatter library for YAML frontmatter

## DRY_RUN Implementation Pattern

**Challenge**: Test system without executing real actions

**Solution**: Global DRY_RUN flag with simulation logging

**Implementation**:
```python
import os
from typing import Callable, Any

class DryRunContext:
    def __init__(self):
        self.enabled = os.getenv("DRY_RUN", "false").lower() == "true"

    def execute(self, action: Callable, *args, **kwargs) -> Any:
        """Execute action or simulate if DRY_RUN enabled"""
        if self.enabled:
            # Log simulation
            logger.info(f"[DRY_RUN] Would execute: {action.__name__}")
            return None
        else:
            # Execute real action
            return action(*args, **kwargs)

# Global instance
dry_run = DryRunContext()

# Usage
def send_email(to: str, subject: str, body: str):
    """Send email (respects DRY_RUN)"""
    return dry_run.execute(
        _send_email_impl,
        to, subject, body
    )
```

**Best Practices**:
- Check DRY_RUN flag at application startup
- Log all simulated actions with [DRY_RUN] prefix
- Return mock data for simulated operations
- Test both DRY_RUN=true and DRY_RUN=false modes

## Polling vs Event-Driven Architecture

**Decision**: Use polling for main orchestrator loop

**Rationale**:
- Simpler implementation (no event loop complexity)
- Sufficient for Bronze tier performance goals (<5s latency)
- Easier to debug and reason about
- No platform-specific dependencies

**Polling Implementation**:
```python
import time
from pathlib import Path

def orchestrator_loop(vault_path: Path, interval: int = 5):
    """Main orchestrator loop with polling"""
    while True:
        try:
            # Scan for new tasks
            tasks = scan_needs_action(vault_path / "Needs_Action")

            # Process each task
            for task in tasks:
                process_task(task)

            # Sleep until next poll
            time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
            break
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            time.sleep(interval)  # Continue after error
```

**Best Practices**:
- Use configurable poll interval (default 5 seconds)
- Handle KeyboardInterrupt for graceful shutdown
- Continue polling after errors (log and recover)
- Consider exponential backoff for repeated errors

**Future Optimization**: For Silver/Gold tiers, consider event-driven architecture with watchdog for real-time responsiveness.

## Skill Loading Pattern

**Challenge**: Dynamically load skill definitions from .claude/skills/

**Solution**: Parse SKILL.md files and validate schema

**Implementation**:
```python
from pathlib import Path
from typing import Dict, List

class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills: Dict[str, dict] = {}

    def load_all(self):
        """Load all skills from .claude/skills/"""
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                logger.warning(f"Missing SKILL.md in {skill_dir.name}")
                continue

            skill = self.parse_skill(skill_file)
            self.skills[skill_dir.name] = skill

    def parse_skill(self, skill_file: Path) -> dict:
        """Parse SKILL.md and validate schema"""
        content = skill_file.read_text()

        # Extract required sections
        sections = parse_markdown_sections(content)

        required = [
            "Purpose", "Constitutional Alignment", "Inputs",
            "Outputs", "Risk Classification", "Execution Logic",
            "HITL Checkpoint", "Logging Requirements",
            "Failure Handling", "Completion Condition"
        ]

        for section in required:
            if section not in sections:
                raise ValueError(f"Missing required section: {section}")

        return sections
```

**Best Practices**:
- Validate all required sections on load
- Cache loaded skills (avoid re-parsing)
- Provide clear error messages for invalid skills
- Support hot-reloading for development (optional)

## Summary

All technology choices validated and documented. No unresolved clarifications. Ready to proceed to Phase 1 (data model and contracts).

**Key Takeaways**:
- Python 3.11+ with minimal dependencies (dotenv, watchdog, pydantic, pytest)
- File-based operations with atomic writes and optional locking
- Daily JSON log rotation for transparency
- Polling architecture for simplicity (Bronze tier)
- DRY_RUN support for safe testing
- Markdown parsing for human-readable task files
- Skill loading with schema validation

**Next Phase**: Create data-model.md and contracts/ with Pydantic schemas and JSON schemas for validation.
