# Research & Technology Decisions: Silver Tier

**Feature**: Silver Tier - Functional Business Assistant
**Date**: 2026-02-17
**Status**: Completed

## Overview

This document captures research findings and technology decisions for Silver Tier implementation. Each decision includes rationale, alternatives considered, and implementation guidance.

## 1. MCP Framework Selection

### Decision: Custom JSON-RPC Implementation

**Rationale**:
- MCP (Model Context Protocol) is relatively new and evolving
- Custom implementation provides full control over logging, DRY_RUN mode, and error handling
- Simplicity: JSON-RPC over stdio/HTTP is straightforward to implement
- No external dependencies reduces complexity and maintenance burden

**Alternatives Considered**:
- **Anthropic's MCP SDK**: Official implementation but may be overkill for simple use cases, adds dependency
- **Existing JSON-RPC libraries**: Generic libraries lack domain-specific features (DRY_RUN, action logging)
- **REST API**: More complex than JSON-RPC, requires HTTP server setup

**Implementation Approach**:
```python
# Base MCP server structure
class MCPServer:
    def __init__(self, name, dry_run=False):
        self.name = name
        self.dry_run = dry_run
        self.logger = setup_logger(name)

    def handle_request(self, method, params):
        if self.dry_run:
            self.logger.info(f"DRY_RUN: Would execute {method} with {params}")
            return {"status": "simulated", "method": method}
        return self.execute(method, params)

    def execute(self, method, params):
        raise NotImplementedError
```

**References**:
- JSON-RPC 2.0 Specification: https://www.jsonrpc.org/specification
- Anthropic MCP Documentation: https://modelcontextprotocol.io/

---

## 2. Gmail API Integration

### Decision: Official google-api-python-client with OAuth2

**Rationale**:
- Official library is well-maintained and documented
- OAuth2 flow stores credentials locally (meets Local-First principle)
- Rate limits are generous for personal use (250 quota units/user/second)
- Supports incremental authorization and token refresh

**Alternatives Considered**:
- **IMAP/SMTP**: Simpler but less reliable, no structured data, security concerns
- **Third-party wrappers**: Add abstraction layer without significant benefit
- **Gmail API via REST**: More complex than using official client library

**Implementation Approach**:
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)
```

**Setup Requirements**:
1. Create Google Cloud project
2. Enable Gmail API
3. Create OAuth2 credentials (Desktop app)
4. Download credentials.json
5. Run authentication flow once to generate token.json
6. Add token.json to .gitignore

**Rate Limits**:
- 250 quota units/user/second
- 1 billion quota units/day
- messages.list: 5 units per request
- Mitigation: Implement exponential backoff, batch requests

**References**:
- Gmail API Python Quickstart: https://developers.google.com/gmail/api/quickstart/python
- OAuth2 for Desktop Apps: https://developers.google.com/identity/protocols/oauth2/native-app

---

## 3. WhatsApp Automation

### Decision: whatsapp-web.js (Node.js) with Python Bridge

**Rationale**:
- Most reliable WhatsApp Web automation library
- Session persistence through QR code authentication
- Lower detection risk than Selenium (uses official WhatsApp Web client)
- Active community and regular updates

**Alternatives Considered**:
- **Selenium/Playwright**: Higher detection risk, more brittle, requires browser automation
- **Official WhatsApp Business API**: Requires business verification, costs money, overkill for personal use
- **yowsup (Python)**: Outdated, high ban risk, no longer maintained

**Implementation Approach**:
```javascript
// Node.js WhatsApp bridge server
const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { headless: true }
});

client.on('qr', (qr) => {
    console.log('QR Code:', qr);
});

client.on('ready', () => {
    console.log('WhatsApp client ready');
});

client.on('message', async (msg) => {
    // Forward to Python watcher via HTTP
    await fetch('http://localhost:5001/whatsapp-event', {
        method: 'POST',
        body: JSON.stringify({
            from: msg.from,
            body: msg.body,
            timestamp: msg.timestamp
        })
    });
});

client.initialize();
```

```python
# Python watcher receives events from Node bridge
from flask import Flask, request
app = Flask(__name__)

@app.route('/whatsapp-event', methods=['POST'])
def handle_whatsapp_event():
    event = request.json
    create_task_file(event)
    return {'status': 'received'}
```

**Setup Requirements**:
1. Install Node.js and whatsapp-web.js
2. Run initial authentication (scan QR code)
3. Session stored in .wwebjs_auth/ (add to .gitignore)
4. Start Node bridge server
5. Python watcher connects to bridge

**Detection Risk Mitigation**:
- Use LocalAuth for persistent sessions
- Add random delays between actions
- Limit message sending rate
- Monitor for ban warnings

**References**:
- whatsapp-web.js: https://github.com/pedroslopez/whatsapp-web.js
- WhatsApp Web Protocol: https://github.com/sigalor/whatsapp-web-reveng

---

## 4. LinkedIn API/Automation

### Decision: Hybrid Approach - Official API for Reading, Selenium for Posting

**Rationale**:
- LinkedIn API requires partner program approval for posting (difficult to obtain)
- Official API good for reading profile, connections, messages
- Selenium automation for posting is reliable with proper rate limiting
- Hybrid approach balances reliability and capability

**Alternatives Considered**:
- **Official API only**: Requires partner approval, limited posting capabilities
- **Selenium only**: Works but higher detection risk, more brittle
- **Third-party services**: Violates Local-First principle, costs money

**Implementation Approach**:
```python
# LinkedIn API for reading (if approved)
import requests

def get_linkedin_profile(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    return response.json()

# Selenium for posting (fallback)
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def post_to_linkedin(content, dry_run=False):
    if dry_run:
        logger.info(f"DRY_RUN: Would post to LinkedIn: {content}")
        return

    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/login')

    # Login (credentials from .env)
    driver.find_element(By.ID, 'username').send_keys(os.getenv('LINKEDIN_EMAIL'))
    driver.find_element(By.ID, 'password').send_keys(os.getenv('LINKEDIN_PASSWORD'))
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    time.sleep(3)  # Wait for login

    # Navigate to post creation
    driver.get('https://www.linkedin.com/feed/')
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Start a post"]').click()

    time.sleep(2)

    # Enter content
    editor = driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]')
    editor.send_keys(content)

    time.sleep(2)

    # Post
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Post"]').click()

    time.sleep(3)
    driver.quit()
```

**Setup Requirements**:
1. LinkedIn account credentials in .env
2. ChromeDriver installed
3. Session cookies stored locally
4. Rate limiting: max 1 post per day

**Detection Risk Mitigation**:
- Use real browser (not headless) for initial setup
- Store session cookies to avoid repeated logins
- Add human-like delays (2-5 seconds between actions)
- Limit to 1 post per day
- Always go through approval workflow

**References**:
- LinkedIn API Documentation: https://docs.microsoft.com/en-us/linkedin/
- Selenium Python Docs: https://selenium-python.readthedocs.io/

---

## 5. Scheduling Strategy

### Decision: OS-Native Scheduling (cron/Task Scheduler/launchd)

**Rationale**:
- Most reliable: OS scheduler survives Python process crashes
- No additional dependencies or background processes
- Cross-platform support (Windows/Linux/Mac)
- Simple to configure and debug

**Alternatives Considered**:
- **Python APScheduler**: Requires persistent Python process, single point of failure
- **Celery**: Overkill for simple scheduling, requires message broker
- **systemd timers**: Linux-only, more complex than cron

**Implementation Approach**:

**Linux/Mac (cron)**:
```bash
# Run watchers every 10 minutes
*/10 * * * * cd /path/to/project && python scripts/run_watchers.py >> logs/cron.log 2>&1

# Run reasoning loop every 10 minutes
*/10 * * * * cd /path/to/project && python scripts/orchestrator.py >> logs/cron.log 2>&1

# Generate LinkedIn post weekly (Sunday 9 AM)
0 9 * * 0 cd /path/to/project && python scripts/linkedin_scheduler.py >> logs/cron.log 2>&1

# Update dashboard daily (8 AM)
0 8 * * * cd /path/to/project && python scripts/update_dashboard.py >> logs/cron.log 2>&1
```

**Windows (Task Scheduler)**:
```powershell
# Create scheduled task for watchers
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/run_watchers.py" -WorkingDirectory "C:\path\to\project"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "AI_Employee_Watchers" -Action $action -Trigger $trigger
```

**Mac (launchd)**:
```xml
<!-- ~/Library/LaunchAgents/com.aiemployee.watchers.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiemployee.watchers</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/project/scripts/run_watchers.py</string>
    </array>
    <key>StartInterval</key>
    <integer>600</integer>
</dict>
</plist>
```

**Setup Script**:
```bash
#!/bin/bash
# scripts/scheduler_setup.sh

OS=$(uname -s)

if [ "$OS" = "Linux" ] || [ "$OS" = "Darwin" ]; then
    echo "Setting up cron jobs..."
    (crontab -l 2>/dev/null; cat scripts/crontab.txt) | crontab -
elif [ "$OS" = "MINGW"* ] || [ "$OS" = "MSYS"* ]; then
    echo "Setting up Windows Task Scheduler..."
    powershell -File scripts/setup_windows_scheduler.ps1
fi
```

**References**:
- Cron Tutorial: https://crontab.guru/
- Windows Task Scheduler: https://docs.microsoft.com/en-us/windows/win32/taskschd/
- launchd Tutorial: https://www.launchd.info/

---

## 6. Event Bus Pattern

### Decision: File-Based JSON Queue

**Rationale**:
- Simplest approach: no external dependencies
- Atomic file operations prevent race conditions
- Human-readable for debugging
- Meets Local-First principle
- Easy to implement file locking

**Alternatives Considered**:
- **SQLite**: Adds dependency, overkill for simple queue
- **Redis/RabbitMQ**: Requires external service, violates simplicity
- **Python Queue**: Requires persistent process, not cross-process

**Implementation Approach**:
```python
import json
import os
import fcntl
from datetime import datetime
from pathlib import Path

class EventQueue:
    def __init__(self, queue_dir='AI_Employee_Vault/Needs_Action'):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def push(self, event):
        """Add event to queue with atomic write"""
        event_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event['source']}"
        event_file = self.queue_dir / f"{event_id}.json"

        # Atomic write with temp file
        temp_file = event_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(event, f, indent=2)
        temp_file.rename(event_file)

        return event_id

    def pop(self):
        """Get next event from queue (FIFO)"""
        files = sorted(self.queue_dir.glob('*.json'))
        if not files:
            return None

        event_file = files[0]
        with open(event_file, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            event = json.load(f)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return event, event_file

    def move_to_done(self, event_file):
        """Move processed event to Done/"""
        done_dir = Path('AI_Employee_Vault/Done')
        done_dir.mkdir(parents=True, exist_ok=True)
        event_file.rename(done_dir / event_file.name)
```

**File Locking Strategy**:
- Use fcntl (Unix) or msvcrt (Windows) for file locking
- Prevent concurrent access to same event file
- Timeout after 30 seconds if lock not acquired

**References**:
- Python fcntl: https://docs.python.org/3/library/fcntl.html
- Atomic File Operations: https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python

---

## 7. Risk Classification

### Decision: Rule-Based Classification with Keyword Matching

**Rationale**:
- Explainable: humans can understand why action was flagged
- No training data required
- Fast and deterministic
- Easy to update rules based on feedback

**Alternatives Considered**:
- **ML-Based**: Requires training data, less explainable, overkill
- **LLM-Based**: Expensive, latency, requires API calls
- **Hardcoded Lists**: Too rigid, difficult to maintain

**Implementation Approach**:
```python
class RiskClassifier:
    HIGH_RISK_KEYWORDS = [
        'payment', 'transfer', 'invoice', 'legal', 'contract',
        'medical', 'health', 'condolence', 'lawsuit', 'terminate'
    ]

    MEDIUM_RISK_KEYWORDS = [
        'email', 'send', 'post', 'publish', 'share', 'reply',
        'new contact', 'unknown', 'first time'
    ]

    SENSITIVE_CONTEXTS = [
        'emotional', 'conflict', 'negotiation', 'complaint'
    ]

    def classify(self, action_type, content, metadata):
        """Classify action risk level"""
        content_lower = content.lower()

        # Check for high-risk keywords
        if any(keyword in content_lower for keyword in self.HIGH_RISK_KEYWORDS):
            return 'HIGH', 'Contains high-risk keywords'

        # Check payment thresholds
        if action_type == 'payment':
            amount = metadata.get('amount', 0)
            if amount > 500:
                return 'HIGH', f'Payment amount ${amount} exceeds threshold'
            if metadata.get('new_payee'):
                return 'HIGH', 'New payee requires approval'

        # Check for medium-risk keywords
        if any(keyword in content_lower for keyword in self.MEDIUM_RISK_KEYWORDS):
            return 'MEDIUM', 'Contains medium-risk keywords'

        # Check for sensitive contexts
        if any(context in content_lower for context in self.SENSITIVE_CONTEXTS):
            return 'MEDIUM', 'Sensitive context detected'

        # Social media always requires approval
        if action_type in ['linkedin_post', 'twitter_post']:
            return 'MEDIUM', 'Social media post requires approval'

        return 'LOW', 'No risk indicators detected'
```

**Rule Update Process**:
1. Monitor false positives/negatives in logs
2. Update keyword lists based on feedback
3. Add new rules for edge cases
4. Document rule changes in ADR

**References**:
- Risk Assessment Patterns: https://martinfowler.com/articles/domain-oriented-observability.html

---

## 8. Approval Workflow Patterns

### Decision: File Movement Between Directories

**Rationale**:
- Human-friendly: users can see pending approvals in file explorer
- Atomic: file move is atomic operation on most filesystems
- Audit trail: file timestamps show when approval occurred
- Simple: no database or status flags needed

**Alternatives Considered**:
- **Status Flags in JSON**: Requires file editing, not atomic
- **Approval Database**: Adds complexity, violates simplicity
- **Git-Based Workflow**: Overkill, requires git knowledge

**Implementation Approach**:
```python
class ApprovalWorkflow:
    def __init__(self):
        self.pending_dir = Path('AI_Employee_Vault/Pending_Approval')
        self.approved_dir = Path('AI_Employee_Vault/Approved')
        self.rejected_dir = Path('AI_Employee_Vault/Rejected')

        for dir in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            dir.mkdir(parents=True, exist_ok=True)

    def request_approval(self, action_id, action_type, description, risk_level):
        """Create approval request file"""
        approval_file = self.pending_dir / f"{action_id}.md"

        content = f"""# Approval Request: {action_type}

**Action ID**: {action_id}
**Risk Level**: {risk_level}
**Created**: {datetime.now().isoformat()}

## Description

{description}

## Instructions

To approve this action:
1. Review the description above
2. Move this file to: AI_Employee_Vault/Approved/
3. The system will execute the action automatically

To reject this action:
1. Move this file to: AI_Employee_Vault/Rejected/
2. The system will cancel the action

**Timeout**: This request will expire in 24 hours if not approved.
"""

        with open(approval_file, 'w') as f:
            f.write(content)

        return approval_file

    def check_approval_status(self, action_id):
        """Check if action has been approved"""
        approved_file = self.approved_dir / f"{action_id}.md"
        rejected_file = self.rejected_dir / f"{action_id}.md"
        pending_file = self.pending_dir / f"{action_id}.md"

        if approved_file.exists():
            return 'APPROVED'
        elif rejected_file.exists():
            return 'REJECTED'
        elif pending_file.exists():
            # Check timeout (24 hours)
            age = time.time() - pending_file.stat().st_mtime
            if age > 86400:  # 24 hours
                pending_file.rename(self.rejected_dir / pending_file.name)
                return 'TIMEOUT'
            return 'PENDING'
        else:
            return 'NOT_FOUND'
```

**User Experience**:
1. System creates approval file in Pending_Approval/
2. User receives notification (optional: desktop notification, email)
3. User opens file, reads description
4. User drags file to Approved/ or Rejected/
5. System detects file movement and proceeds

**Timeout Handling**:
- Default timeout: 24 hours
- Configurable per action type
- Expired approvals moved to Rejected/
- Timeout logged for audit

**References**:
- File System Patterns: https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard

---

## Summary of Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| MCP Framework | Custom JSON-RPC | Full control, no dependencies, simple |
| Gmail Integration | google-api-python-client | Official, reliable, local credentials |
| WhatsApp Automation | whatsapp-web.js + Python bridge | Most reliable, session persistence |
| LinkedIn Automation | Hybrid (API + Selenium) | Balances capability and reliability |
| Scheduling | OS-native (cron/Task Scheduler) | Most reliable, survives crashes |
| Event Queue | File-based JSON | Simple, atomic, human-readable |
| Risk Classification | Rule-based keywords | Explainable, fast, no training needed |
| Approval Workflow | File movement | Human-friendly, atomic, audit trail |

## Implementation Priority

1. **Phase 0** (Foundation): Event queue, logging, file operations
2. **Phase 1** (Watchers): Gmail watcher (easiest), then LinkedIn, then WhatsApp
3. **Phase 2** (Skills): Reasoning loop, risk classifier, approval guard
4. **Phase 3** (MCP): Email MCP server, LinkedIn MCP server
5. **Phase 4** (Integration): LinkedIn post generator, orchestrator
6. **Phase 5** (Automation): Scheduler setup, watchdog monitoring

## Next Steps

1. Create data-model.md with entity schemas
2. Create contracts/ with MCP server specifications
3. Create quickstart.md with setup instructions
4. Update agent context with technology stack
5. Generate tasks.md with implementation tasks
