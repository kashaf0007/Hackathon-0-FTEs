# Contributing to AI Employee

Thank you for your interest in contributing to the AI Employee project! This document provides guidelines and standards for contributing to this Silver Tier Constitutional FTE implementation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Constitutional Compliance](#constitutional-compliance)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Adding New Features](#adding-new-features)

---

## Code of Conduct

### Our Principles

This project adheres to the Constitutional Principles:

1. **Local-First**: All data stored locally, no cloud dependencies
2. **HITL Safety**: Human-in-the-Loop approval for high-risk actions
3. **Transparency**: Complete audit logging of all actions
4. **Proactivity**: Autonomous monitoring and execution
5. **Persistence**: Tasks continue until complete with retry logic
6. **Cost Efficiency**: Efficient resource usage and scheduling

All contributions must maintain these principles.

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of async programming
- Familiarity with file-based state management

### First Contribution

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

---

## Development Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with test credentials
```

### 3. Run in Test Mode

```bash
DRY_RUN=true python scripts/orchestrator.py --once
```

### 4. Verify Setup

```bash
python scripts/watchdog.py
python scripts/validate_scheduler.py
```

---

## Constitutional Compliance

### MUST Requirements

Every contribution MUST:

1. **Maintain Local-First**:
   - No cloud storage dependencies
   - All state in `AI_Employee_Vault/`
   - File-based persistence only

2. **Enforce HITL Safety**:
   - Risk classification for all actions
   - Approval workflow for medium/high risk
   - No bypassing approval mechanisms

3. **Ensure Transparency**:
   - Log all actions with full metadata
   - Include timestamp, actor, target, status
   - No silent failures

4. **Support DRY_RUN**:
   - All external actions must respect DRY_RUN mode
   - Simulate operations without real execution
   - Log simulated actions clearly

5. **Implement Retry Logic**:
   - Exponential backoff (5s, 15s, 45s)
   - Distinguish transient vs permanent errors
   - Create escalation tasks after max retries

### Validation

Before submitting, verify constitutional compliance:

```bash
# Check for cloud dependencies
grep -r "requests\.\|urllib\|http\.client" your_file.py

# Verify DRY_RUN support
grep -r "DRY_RUN\|dry_run" your_file.py

# Check logging
grep -r "logger\." your_file.py
```

---

## Code Standards

### Python Style

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Google-style docstrings for all public functions
- **Line Length**: Maximum 100 characters

### Example

```python
from typing import Dict, Any, Optional
from pathlib import Path

def process_event(
    event: Dict[str, Any],
    dry_run: bool = False
) -> Optional[Path]:
    """
    Process an event and create a task file.

    Args:
        event: Event dictionary with source, type, content
        dry_run: If True, simulate without real execution

    Returns:
        Path to created task file, or None if dry_run

    Raises:
        ValueError: If event format is invalid
    """
    if not event.get('id'):
        raise ValueError("Event must have 'id' field")

    # Implementation
    pass
```

### File Organization

```
your_module/
├── __init__.py          # Module exports
├── core.py              # Core functionality
├── models.py            # Data models (Pydantic)
├── utils.py             # Utility functions
└── tests/
    └── test_core.py     # Unit tests
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore()`

---

## Testing Requirements

### Unit Tests

All new code must include unit tests:

```python
import pytest
from your_module import process_event

def test_process_event_valid():
    """Test event processing with valid input."""
    event = {
        'id': 'test_001',
        'source': 'test',
        'type': 'test_event',
        'content': 'Test content'
    }
    result = process_event(event, dry_run=True)
    assert result is None  # dry_run returns None

def test_process_event_invalid():
    """Test event processing with invalid input."""
    event = {'source': 'test'}  # Missing 'id'
    with pytest.raises(ValueError):
        process_event(event)
```

### Integration Tests

Test interactions between components:

```python
def test_watcher_to_orchestrator_flow():
    """Test complete flow from watcher to orchestrator."""
    # Create test event
    # Verify task file created
    # Verify orchestrator processes it
    # Verify logs generated
    pass
```

### Test Coverage

- Minimum 80% code coverage
- 100% coverage for critical paths (approval, logging)
- Test both success and failure cases
- Test DRY_RUN mode

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=scripts --cov=AI_Employee_Vault tests/

# Run specific test
pytest tests/test_orchestrator.py::test_event_routing
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(watcher): add WhatsApp watcher support

- Implement WhatsApp watcher class
- Add configuration to watcher_config.json
- Include OAuth2 authentication
- Add unit tests

Closes #123
```

```
fix(approval): handle timeout edge case

- Fix race condition in approval timeout check
- Add test for concurrent approval requests
- Update documentation

Fixes #456
```

### Commit Best Practices

- One logical change per commit
- Write clear, descriptive messages
- Reference issue numbers
- Keep commits atomic and reversible

---

## Pull Request Process

### Before Submitting

1. **Update from main**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Check code style**:
   ```bash
   black scripts/ AI_Employee_Vault/
   flake8 scripts/ AI_Employee_Vault/
   mypy scripts/ AI_Employee_Vault/
   ```

4. **Verify constitutional compliance**:
   ```bash
   python scripts/validate_constitutional_compliance.py
   ```

5. **Update documentation**:
   - Update README.md if adding features
   - Update relevant skill SKILL.md files
   - Add examples to examples.md

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Constitutional Compliance
- [ ] Maintains Local-First principle
- [ ] Enforces HITL for risky actions
- [ ] Includes comprehensive logging
- [ ] Supports DRY_RUN mode
- [ ] Implements retry logic

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Coverage >= 80%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commits are atomic and well-described
```

### Review Process

1. Automated checks run (tests, linting, coverage)
2. Maintainer reviews code
3. Address feedback
4. Approval required from 1+ maintainers
5. Merge to main

---

## Adding New Features

### Skills

To add a new skill:

1. **Create skill directory**:
   ```bash
   mkdir -p .claude/skills/my-skill
   ```

2. **Create required files**:
   - `SKILL.md`: Documentation
   - `prompt.txt`: Skill prompt
   - `examples.md`: Usage examples

3. **Update orchestrator**:
   - Add routing logic in `scripts/orchestrator.py`
   - Update `_route_to_skill()` method

4. **Add tests**:
   ```python
   def test_my_skill_routing():
       """Test that events route to my-skill correctly."""
       pass
   ```

### Watchers

To add a new watcher:

1. **Create watcher class**:
   ```python
   from AI_Employee_Vault.Watchers.watcher_base import WatcherBase

   class MyWatcher(WatcherBase):
       def __init__(self, config: Dict[str, Any]):
           super().__init__('my_watcher', config)

       def poll_once(self) -> List[Dict[str, Any]]:
           """Poll for new events."""
           # Implementation
           pass
   ```

2. **Add configuration**:
   ```json
   {
     "my_watcher": {
       "enabled": true,
       "poll_interval": 300
     }
   }
   ```

3. **Register watcher**:
   - Add to `scripts/run_watchers.py`

4. **Add tests**:
   ```python
   def test_my_watcher_detection():
       """Test watcher detects events correctly."""
       pass
   ```

### MCP Servers

To add a new MCP server:

1. **Create server class**:
   ```python
   from mcp_servers.mcp_base import MCPServer

   class MyMCPServer(MCPServer):
       def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
           """Handle JSON-RPC request."""
           # Implementation
           pass
   ```

2. **Add configuration**:
   ```json
   {
     "my_server": {
       "port": 5003,
       "host": "localhost"
     }
   }
   ```

3. **Create corresponding skill**:
   - Add skill in `.claude/skills/my-mcp-sender/`

4. **Add tests**:
   ```python
   def test_my_mcp_server():
       """Test MCP server handles requests correctly."""
       pass
   ```

---

## Questions?

- **Documentation**: See `specs/` directory
- **Issues**: Check existing issues on GitHub
- **Discussion**: Open a discussion for questions
- **Contact**: See README.md for support information

---

**Thank you for contributing to AI Employee!**

Your contributions help build a more capable, safe, and transparent autonomous assistant.
