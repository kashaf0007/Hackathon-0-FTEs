# Logging & Audit

## Purpose
Guarantee Transparency principle by logging every action to AI_Employee_Vault/Logs/YYYY-MM-DD.json with complete metadata (timestamp, action, skill used, risk classification, approval status, outcome), flagging constitutional violations, and maintaining complete audit trail.

## Constitutional Alignment
- **Transparency**: Core implementation - makes all actions visible and auditable
- **Local-First**: All logs stored locally in vault
- **Cost Efficiency**: File-based logging, no external services

## Inputs
- Action descriptions (what was done)
- Task IDs (which task triggered action)
- Skill names (which skill performed action)
- Risk levels (LOW, MEDIUM, HIGH)
- Approval statuses (AUTO_APPROVED, PENDING_APPROVAL, APPROVED, REJECTED)
- Outcomes (SUCCESS, FAILURE, BLOCKED)
- Error messages (if action failed)
- Metadata (duration_ms, retry_count, etc.)

## Outputs
- Daily log files: AI_Employee_Vault/Logs/YYYY-MM-DD.json
- JSON array of log entries with complete metadata
- Constitutional compliance flags
- Violation counts and alerts

## Risk Classification
**LOW** - Logging only, no external actions. Records information without modifying system state (except log files).

## Execution Logic
1. **Receive Log Request**: Get action details from any skill or orchestrator
2. **Create Log Entry**: Build LogEntry model with all required fields
   - timestamp: Current time (ISO 8601, UTC)
   - task_id: Associated task (if any)
   - action: Description of what was done
   - skill_used: Which skill performed action
   - risk_level: Risk classification
   - approval_status: Approval state
   - outcome: SUCCESS, FAILURE, or BLOCKED
   - error: Error message (if failed)
   - constitutional_compliance: True unless violation detected
   - dry_run: Whether this was simulated
   - metadata: Additional context (duration, retries, etc.)
3. **Determine Log File**: Calculate today's date, format as YYYY-MM-DD.json
4. **Read Existing Logs**: Load current day's log file (if exists)
5. **Append Entry**: Add new entry to array
6. **Write Atomically**: Use atomic_write to prevent corruption
7. **Flag Violations**: If constitutional_compliance=false, increment violation counter

## HITL Checkpoint
Logging & Audit does NOT require approval (LOW risk). It operates automatically for all actions.

**Exception**: If logging itself fails repeatedly, create alert in Needs_Action/ for human review.

## Logging Requirements
Logging & Audit logs its own operations:
- **Log File Creation**: When new daily log file created
- **Log Write Success**: Confirmation of successful log entry
- **Log Write Failure**: If atomic write fails (with error details)
- **Violation Detection**: When constitutional_compliance=false entry logged

Meta-logging (logging about logging) uses same format:
- action: "log_write" or "log_file_create"
- skill_used: "logging-audit"
- risk_level: LOW
- outcome: SUCCESS or FAILURE

## Failure Handling
**File System Errors**:
- If log directory doesn't exist: create it automatically
- If log file corrupted: start fresh array (log corruption event)
- If disk full: log to stderr, create alert in Needs_Action/

**Atomic Write Failures**:
- Retry up to 3 times with 1s delay
- If all retries fail: log to stderr, continue operation (don't block system)
- Create alert file in Needs_Action/ for human review

**Log Rotation**:
- New file created automatically each day (YYYY-MM-DD.json)
- Old logs preserved indefinitely (manual archival after 30 days recommended)
- If log file >10MB: log warning (but continue writing)

**Safe Failure Principle**: Logging failures should NEVER block system operation. Log to stderr and continue.

## Completion Condition
Logging & Audit completes when:
- Log entry successfully written to daily log file
- File written atomically (no partial writes)
- Entry includes all required fields
- Constitutional compliance evaluated and flagged
- `<promise>LOG_COMPLETE</promise>` marker emitted (internal)

**Verification**:
- Log file exists: AI_Employee_Vault/Logs/YYYY-MM-DD.json
- File is valid JSON array
- Entry contains all required fields (timestamp, action, risk_level, approval_status, outcome)
- Entry is appended (not overwriting previous entries)
- File size increased by entry size

**Audit Trail Verification**:
- Every action has corresponding log entry
- No gaps in timestamps (within poll_interval)
- All task_ids referenced in logs have corresponding task files
- All approval_status values match approval files
- Constitutional violations flagged and counted
