"""File operations utilities for Bronze Tier Constitutional FTE.

Provides safe file operations including atomic writes and markdown parsing.
"""

import tempfile
import shutil
import re
from pathlib import Path
from typing import Dict, Any, Optional


def atomic_write(path: Path, content: str) -> None:
    """Write file atomically to prevent partial reads.

    Uses write-to-temp-then-rename pattern for atomicity.

    Args:
        path: Target file path
        content: Content to write

    Raises:
        IOError: If write fails
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (same filesystem)
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp"
    )

    try:
        with open(fd, 'w', encoding='utf-8') as f:
            f.write(content)

        # Atomic rename (POSIX guarantees atomicity)
        shutil.move(temp_path, path)
    except Exception as e:
        # Clean up temp file on error
        Path(temp_path).unlink(missing_ok=True)
        raise IOError(f"Failed to write {path}: {e}") from e


def parse_markdown_task(content: str) -> Dict[str, Any]:
    """Parse markdown task file with metadata.

    Extracts title, metadata (bold key-value pairs), and sections.

    Args:
        content: Markdown file content

    Returns:
        Dictionary with 'title', 'metadata', and 'sections'

    Example:
        >>> content = '''# Task: Draft Email
        ... **Type**: draft_email
        ... **Priority**: MEDIUM
        ... ## Context
        ... Email details here
        ... '''
        >>> result = parse_markdown_task(content)
        >>> result['title']
        'Task: Draft Email'
        >>> result['metadata']['type']
        'draft_email'
    """
    lines = content.split('\n')

    # Extract title (first # heading)
    title = None
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Extract metadata (bold key-value pairs: **Key**: value)
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
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(section_content).strip()
            # Start new section
            current_section = line[3:].strip()
            section_content = []
        elif current_section:
            section_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(section_content).strip()

    return {
        'title': title,
        'metadata': metadata,
        'sections': sections
    }


def format_markdown_task(
    title: str,
    task_type: str,
    priority: str,
    created: str,
    status: str,
    context: str,
    expected_output: Optional[str] = None,
    actual_output: Optional[str] = None
) -> str:
    """Format task data as markdown.

    Args:
        title: Task title
        task_type: Task type
        priority: Priority level (LOW/MEDIUM/HIGH)
        created: ISO 8601 timestamp
        status: Task status
        context: Task context description
        expected_output: Expected result description
        actual_output: Actual result (if completed)

    Returns:
        Formatted markdown string
    """
    md = f"""# Task: {title}

**Type**: {task_type}
**Priority**: {priority}
**Created**: {created}
**Status**: {status}

## Context
{context}
"""

    if expected_output:
        md += f"\n## Expected Output\n{expected_output}\n"

    if actual_output:
        md += f"\n## Actual Output\n{actual_output}\n"

    return md


def format_markdown_approval(
    request_id: str,
    task_id: str,
    created: str,
    risk_level: str,
    action: str,
    justification: str,
    impact: str,
    status: str = "PENDING",
    approver: Optional[str] = None,
    decision: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """Format approval request as markdown.

    Args:
        request_id: Unique request ID
        task_id: Associated task ID
        created: ISO 8601 timestamp
        risk_level: MEDIUM or HIGH
        action: Action description
        justification: Why needed
        impact: What will happen
        status: PENDING/APPROVED/REJECTED
        approver: Who approved/rejected
        decision: APPROVE/REJECT
        notes: Approver notes

    Returns:
        Formatted markdown string
    """
    md = f"""# Approval Request: {request_id}

**Task ID**: {task_id}
**Created**: {created}
**Risk Level**: {risk_level}
**Action**: {action}

## Justification
{justification}

## Impact
{impact}

## Approval
**Status**: {status}
**Approver**: {approver or '[leave blank]'}
**Decision**: {decision or '[APPROVE|REJECT]'}
**Notes**: {notes or '[optional]'}
"""
    return md
