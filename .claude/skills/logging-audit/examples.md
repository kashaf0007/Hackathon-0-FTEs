# Logging & Audit Skill - Examples

## Example 1: Event Detection and Classification

**Scenario**: Gmail watcher detects new email from potential customer

**Log Entry**:
```json
{
  "timestamp": "2026-02-18T10:15:23Z",
  "component": "watcher",
  "action": "event_detected",
  "actor": "gmail_watcher",
  "target": "gmail_20260218_001",
  "status": "success",
  "details": {
    "duration_ms": 234,
    "event_type": "new_message",
    "from": "john@techcorp.com",
    "subject": "Interested in AI automation services",
    "classification": "sales_inquiry"
  }
}
```

**Constitutional Check**: ✅ PASS
- Transparency: Event logged with full metadata
- Local-First: Stored in local logs/ directory
- No PII: Email address is business contact (not sensitive)

---

## Example 2: Approval Request Created

**Scenario**: LinkedIn post generator creates post requiring approval

**Log Entry**:
```json
{
  "timestamp": "2026-02-18T10:20:45Z",
  "component": "approval",
  "action": "approval_requested",
  "actor": "linkedin-post-generator",
  "target": "linkedin_post_20260218_002",
  "status": "success",
  "details": {
    "duration_ms": 156,
    "risk_level": "medium",
    "action_type": "linkedin_post",
    "requires_approval": true,
    "approval_file": "AI_Employee_Vault/Pending_Approval/linkedin_post_20260218_002.md",
    "timeout_hours": 24
  }
}
```

**Constitutional Check**: ✅ PASS
- HITL: Approval required for public posting
- Transparency: Approval request logged
- Persistence: Timeout mechanism ensures task doesn't stall

---

## Example 3: MCP Action Executed (DRY_RUN)

**Scenario**: Email MCP server sends email in DRY_RUN mode

**Log Entry**:
```json
{
  "timestamp": "2026-02-18T10:25:12Z",
  "component": "mcp",
  "action": "email_sent",
  "actor": "email-mcp-sender",
  "target": "email_20260218_003",
  "status": "success",
  "details": {
    "duration_ms": 89,
    "dry_run": true,
    "to": "client@example.com",
    "subject": "Re: Your inquiry about AI automation",
    "body_length": 456,
    "message_id": "DRY_RUN_SIMULATED"
  }
}
```

**Constitutional Check**: ✅ PASS
- Transparency: DRY_RUN mode clearly logged
- Local-First: No external API called in DRY_RUN
- No sensitive data: Email content summarized (length only)

---

## Example 4: Reasoning Loop Plan Created

**Scenario**: Reasoning loop creates Plan.md for complex sales inquiry

**Log Entry**:
```json
{
  "timestamp": "2026-02-18T10:30:00Z",
  "component": "reasoning",
  "action": "plan_created",
  "actor": "reasoning-loop",
  "target": "plan_20260218_004",
  "status": "success",
  "details": {
    "duration_ms": 1234,
    "event_id": "gmail_20260218_001",
    "objective": "Respond to sales inquiry and schedule consultation",
    "steps_count": 6,
    "risk_level": "medium",
    "requires_approval": true,
    "plan_file": "AI_Employee_Vault/Plan.md"
  }
}
```

**Constitutional Check**: ✅ PASS
- Proactivity: AI autonomously created execution plan
- Transparency: Plan creation logged with full context
- HITL: Approval required for sensitive steps

---

## Example 5: Step Execution with Retry

**Scenario**: Step execution fails, retries, then succeeds

**Log Entries**:
```json
{
  "timestamp": "2026-02-18T10:35:00Z",
  "component": "reasoning",
  "action": "step_execution_started",
  "actor": "step_executor",
  "target": "step_3",
  "status": "success",
  "details": {
    "duration_ms": 45,
    "step_description": "Send personalized email response",
    "requires_risk_check": true
  }
}
```

```json
{
  "timestamp": "2026-02-18T10:35:05Z",
  "component": "reasoning",
  "action": "step_execution_failed",
  "actor": "step_executor",
  "target": "step_3",
  "status": "error",
  "details": {
    "duration_ms": 5234,
    "error": "Network timeout",
    "retry_count": 1,
    "max_retries": 3,
    "next_retry_delay_seconds": 5
  }
}
```

```json
{
  "timestamp": "2026-02-18T10:35:15Z",
  "component": "reasoning",
  "action": "step_execution_completed",
  "actor": "step_executor",
  "target": "step_3",
  "status": "success",
  "details": {
    "duration_ms": 1567,
    "retry_count": 1,
    "total_attempts": 2,
    "outcome": "Email sent successfully"
  }
}
```

**Constitutional Check**: ✅ PASS
- Persistence: Retry logic ensures task completion
- Transparency: All attempts logged with timing
- Error handling: Transient errors handled gracefully

---

## Example 6: Constitutional Violation Detected

**Scenario**: Skill attempts to send email without approval

**Log Entry**:
```json
{
  "timestamp": "2026-02-18T10:40:00Z",
  "component": "approval",
  "action": "constitutional_violation",
  "actor": "email-mcp-sender",
  "target": "email_20260218_005",
  "status": "error",
  "details": {
    "duration_ms": 12,
    "violation_type": "HITL_BYPASS",
    "description": "Attempted to send email to new contact without approval",
    "risk_level": "medium",
    "action_blocked": true,
    "escalation_created": true,
    "escalation_file": "AI_Employee_Vault/Needs_Action/ESCALATION_20260218_005.md"
  }
}
```

**Constitutional Check**: ❌ VIOLATION DETECTED AND BLOCKED
- HITL: Violation detected and prevented
- Transparency: Violation logged with full context
- Accountability: Escalation task created for review

---

## Example 7: Approval Timeout

**Scenario**: LinkedIn post approval times out after 24 hours

**Log Entry**:
```json
{
  "timestamp": "2026-02-19T10:20:45Z",
  "component": "approval",
  "action": "approval_timeout",
  "actor": "approval_workflow",
  "target": "linkedin_post_20260218_002",
  "status": "warning",
  "details": {
    "duration_ms": 89,
    "timeout_hours": 24,
    "action_type": "linkedin_post",
    "auto_rejected": true,
    "escalation_created": true,
    "escalation_file": "AI_Employee_Vault/Needs_Action/TIMEOUT_20260218_002.md"
  }
}
```

**Constitutional Check**: ⚠️ WARNING
- HITL: Approval timeout handled correctly
- Persistence: Task not abandoned, escalation created
- Transparency: Timeout logged with reason

---

## Example 8: Performance Metrics

**Scenario**: Daily performance summary

**Log Entry**:
```json
{
  "timestamp": "2026-02-18T23:59:59Z",
  "component": "orchestrator",
  "action": "daily_summary",
  "actor": "watchdog",
  "target": "system",
  "status": "success",
  "details": {
    "duration_ms": 234,
    "events_processed": 47,
    "approvals_requested": 12,
    "approvals_granted": 10,
    "approvals_rejected": 1,
    "approvals_timeout": 1,
    "emails_sent": 8,
    "linkedin_posts": 1,
    "plans_created": 5,
    "plans_completed": 4,
    "errors_encountered": 2,
    "success_rate": 95.7,
    "avg_response_time_ms": 1234,
    "queue_depth": 3
  }
}
```

**Constitutional Check**: ✅ PASS
- Transparency: Complete system metrics logged
- Cost Efficiency: Performance tracked for optimization
- Accountability: Success rate and errors visible

---

## Example 9: Logging Failure with Recovery

**Scenario**: Log write fails, retry succeeds

**Log Entries** (to stderr):
```
[2026-02-18T11:00:00Z] ERROR: Failed to write log entry (attempt 1/3): Disk full
[2026-02-18T11:00:01Z] INFO: Retrying log write (attempt 2/3)
[2026-02-18T11:00:01Z] SUCCESS: Log entry written successfully
```

**Escalation Task Created**:
```markdown
# ALERT: Logging System Issue

**Timestamp**: 2026-02-18T11:00:00Z
**Issue**: Disk full - log write failed
**Resolution**: Retry succeeded after 1 second
**Action Required**: Check disk space and implement log rotation

**Details**:
- Log directory: AI_Employee_Vault/Logs/
- Current disk usage: 95%
- Recommendation: Run log rotation script
```

**Constitutional Check**: ✅ PASS
- Transparency: Logging failure logged to stderr
- Persistence: Retry logic ensures log is written
- System never blocked: Operation continued despite logging issue

---

## Example 10: Multi-Component Workflow

**Scenario**: Complete workflow from event detection to completion

**Log Entries**:
```json
[
  {
    "timestamp": "2026-02-18T12:00:00Z",
    "component": "watcher",
    "action": "event_detected",
    "actor": "gmail_watcher",
    "target": "gmail_20260218_010",
    "status": "success",
    "details": {"duration_ms": 234, "event_type": "new_message"}
  },
  {
    "timestamp": "2026-02-18T12:00:05Z",
    "component": "orchestrator",
    "action": "event_routed",
    "actor": "task-orchestrator",
    "target": "gmail_20260218_010",
    "status": "success",
    "details": {"duration_ms": 89, "routed_to": "reasoning-loop"}
  },
  {
    "timestamp": "2026-02-18T12:00:10Z",
    "component": "reasoning",
    "action": "plan_created",
    "actor": "reasoning-loop",
    "target": "plan_20260218_010",
    "status": "success",
    "details": {"duration_ms": 1234, "steps_count": 4}
  },
  {
    "timestamp": "2026-02-18T12:00:15Z",
    "component": "reasoning",
    "action": "step_execution_completed",
    "actor": "step_executor",
    "target": "step_1",
    "status": "success",
    "details": {"duration_ms": 567, "step_description": "Analyze email intent"}
  },
  {
    "timestamp": "2026-02-18T12:00:20Z",
    "component": "approval",
    "action": "approval_requested",
    "actor": "approval-guard",
    "target": "email_20260218_010",
    "status": "success",
    "details": {"duration_ms": 156, "risk_level": "medium"}
  },
  {
    "timestamp": "2026-02-18T12:30:00Z",
    "component": "approval",
    "action": "approval_granted",
    "actor": "human",
    "target": "email_20260218_010",
    "status": "success",
    "details": {"duration_ms": 45, "approval_time_minutes": 30}
  },
  {
    "timestamp": "2026-02-18T12:30:05Z",
    "component": "mcp",
    "action": "email_sent",
    "actor": "email-mcp-sender",
    "target": "email_20260218_010",
    "status": "success",
    "details": {"duration_ms": 1567, "message_id": "msg_abc123"}
  },
  {
    "timestamp": "2026-02-18T12:30:10Z",
    "component": "orchestrator",
    "action": "task_completed",
    "actor": "task-orchestrator",
    "target": "gmail_20260218_010",
    "status": "success",
    "details": {
      "duration_ms": 1810000,
      "total_duration_minutes": 30,
      "steps_completed": 4,
      "approvals_required": 1,
      "outcome": "Email sent successfully"
    }
  }
]
```

**Constitutional Check**: ✅ PASS
- Transparency: Complete audit trail from start to finish
- HITL: Approval workflow enforced
- Persistence: Task completed successfully
- Local-First: All logs stored locally
- Accountability: Every decision traceable

---

## Testing Checklist

- [ ] All log entries follow JSON format
- [ ] Timestamps are ISO 8601 with Z suffix
- [ ] Component names match system architecture
- [ ] Action names are descriptive and consistent
- [ ] Status values are success/warning/error only
- [ ] Duration tracked in milliseconds
- [ ] No passwords or API keys logged
- [ ] No PII logged (email content summarized)
- [ ] Constitutional violations flagged
- [ ] Performance metrics tracked
- [ ] Retry logic logged correctly
- [ ] Approval workflow logged completely
- [ ] Error context captured fully
- [ ] Escalations created for failures
- [ ] Logging failures never block system
