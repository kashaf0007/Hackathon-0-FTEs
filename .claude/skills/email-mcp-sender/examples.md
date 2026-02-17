# Email MCP Sender Skill - Examples

## Example 1: Email to New Contact (Requires Approval)

**Input**:
```json
{
  "to": "john.smith@techcorp.com",
  "subject": "Re: Inquiry about AI automation services",
  "body": "Hi John,\n\nThank you for your interest in our AI automation services. I'd be happy to provide pricing information and schedule a demo.\n\nOur pricing tiers are:\n- Starter: $500/month\n- Professional: $1,500/month\n- Enterprise: Custom pricing\n\nWould you be available for a 30-minute demo next week? Please let me know your preferred time.\n\nBest regards,\nAI Employee",
  "from_name": "AI Employee",
  "contact_history": "new",
  "context": "Sales inquiry response"
}
```

**Execution Flow**:
1. Validate email address → Valid
2. Assess risk → Medium (new contact)
3. Create approval request in Pending_Approval/
4. Wait for human approval...
5. Human moves file to Approved/
6. Send email via MCP server
7. Receive message_id from Gmail API
8. Log successful send

**Output**:
```json
{
  "status": "sent",
  "message_id": "18d4f2a3b5c6e7f8",
  "to": "john.smith@techcorp.com",
  "subject": "Re: Inquiry about AI automation services",
  "requires_approval": true,
  "approval_id": "email_20260217_001",
  "approval_status": "approved"
}
```

---

## Example 2: Email to Frequent Contact (Auto-Send)

**Input**:
```json
{
  "to": "regular.client@example.com",
  "subject": "Re: Project Status Update",
  "body": "Thanks for the update. Everything looks good. I'll review the details and get back to you by tomorrow.\n\nBest,\nAI Employee",
  "from_name": "AI Employee",
  "contact_history": "frequent",
  "context": "Follow-up to existing thread"
}
```

**Execution Flow**:
1. Validate email address → Valid
2. Assess risk → Low (frequent contact)
3. No approval needed
4. Send email via MCP server immediately
5. Receive message_id
6. Log successful send

**Output**:
```json
{
  "status": "sent",
  "message_id": "19e5g3b4c6d7f8h9",
  "to": "regular.client@example.com",
  "subject": "Re: Project Status Update",
  "requires_approval": false,
  "approval_status": "auto_approved"
}
```

---

## Example 3: Email Send Failure with Retry

**Scenario**: Network timeout during send, retry succeeds

**Execution Log**:
```
10:30:00 - Validate email: valid
10:30:00 - Assess risk: low (frequent contact)
10:30:00 - Attempt 1: Send via MCP
10:30:05 - ERROR: Network timeout
10:30:05 - Retry 1/3 (wait 5s)
10:30:10 - Attempt 2: Send via MCP
10:30:15 - SUCCESS: Email sent
10:30:15 - Message ID: 20f6h4c5d7e8g9i0
```

**Output**:
```json
{
  "status": "sent",
  "message_id": "20f6h4c5d7e8g9i0",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "requires_approval": false,
  "attempts": 2,
  "retry_count": 1
}
```

---

## Example 4: Invalid Email Address

**Input**:
```json
{
  "to": "invalid-email",
  "subject": "Test",
  "body": "Test message"
}
```

**Execution Flow**:
1. Validate email address → Invalid format
2. Return error immediately
3. Do not attempt send
4. Log validation failure

**Output**:
```json
{
  "status": "failed",
  "error": "Invalid email address format",
  "to": "invalid-email",
  "validation": {
    "valid": false,
    "reason": "Invalid email format"
  }
}
```

---

## Example 5: Approval Timeout

**Scenario**: Email requires approval but no decision within 24 hours

**Execution Flow**:
1. Validate email → Valid
2. Assess risk → Medium (new contact)
3. Create approval request at 10:00 on Day 1
4. Wait for approval...
5. Check status at 10:00 on Day 2 (24 hours later)
6. Timeout detected
7. Move approval file to Rejected/
8. Cancel email send
9. Create escalation task in Needs_Action/

**Output**:
```json
{
  "status": "failed",
  "error": "Approval timeout - no decision within 24 hours",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "requires_approval": true,
  "approval_id": "email_20260217_002",
  "approval_status": "timeout",
  "escalation_task": "AI_Employee_Vault/Needs_Action/escalation_20260218_100000.md"
}
```

---

## Example 6: Bulk Email (Multiple Recipients)

**Input**:
```json
{
  "to": "client1@example.com",
  "cc": ["client2@example.com", "client3@example.com"],
  "subject": "Monthly Newsletter",
  "body": "Dear clients,\n\nHere's our monthly update...",
  "from_name": "AI Employee",
  "contact_history": "mixed"
}
```

**Risk Assessment**:
- Multiple recipients → Medium risk
- Requires approval even if some contacts are frequent

**Execution Flow**:
1. Validate all email addresses → All valid
2. Assess risk → Medium (bulk email)
3. Create approval request
4. Wait for approval
5. Send to all recipients via MCP
6. Log send with all recipients

---

## Example 7: HTML Email

**Input**:
```json
{
  "to": "client@example.com",
  "subject": "Welcome to Our Service",
  "body": "<html><body><h1>Welcome!</h1><p>Thank you for signing up.</p></body></html>",
  "html": true,
  "from_name": "AI Employee",
  "contact_history": "new"
}
```

**Execution Flow**:
1. Validate email → Valid
2. Assess risk → Medium (new contact + HTML)
3. Create approval request with HTML preview
4. Wait for approval
5. Send HTML email via MCP
6. Log successful send

---

## Example 8: DRY_RUN Mode

**Environment**: `DRY_RUN=true`

**Input**:
```json
{
  "to": "test@example.com",
  "subject": "Test Email",
  "body": "This is a test",
  "contact_history": "new"
}
```

**Execution Flow**:
1. Validate email → Valid
2. Assess risk → Medium (new contact)
3. Create approval request (simulated)
4. Simulate approval granted
5. Simulate email send (no actual API call)
6. Return simulated message_id
7. Log all operations with "simulated" flag

**Output**:
```json
{
  "status": "sent",
  "message_id": "simulated_msg_001",
  "to": "test@example.com",
  "subject": "Test Email",
  "requires_approval": true,
  "approval_status": "approved",
  "simulated": true,
  "note": "DRY_RUN mode - no actual email sent"
}
```

---

## Example 9: Authentication Error

**Scenario**: Gmail OAuth token expired

**Execution Flow**:
1. Validate email → Valid
2. Assess risk → Low (frequent contact)
3. Attempt send via MCP
4. ERROR: Authentication failed (401)
5. Retry 1: Still fails
6. Retry 2: Still fails
7. Retry 3: Still fails
8. Create escalation task
9. Log authentication error

**Output**:
```json
{
  "status": "failed",
  "error": "Authentication failed - Gmail token expired",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "attempts": 3,
  "escalation_task": "AI_Employee_Vault/Needs_Action/escalation_20260217_103000.md",
  "action_required": "Refresh Gmail OAuth token"
}
```

---

## Example 10: Rate Limit Exceeded

**Scenario**: Gmail API rate limit reached

**Execution Flow**:
1. Validate email → Valid
2. Assess risk → Low
3. Attempt send via MCP
4. ERROR: Rate limit exceeded (429)
5. Queue email for later
6. Log rate limit warning
7. Schedule retry in 60 seconds

**Output**:
```json
{
  "status": "queued",
  "error": "Rate limit exceeded - queued for retry",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "retry_after": 60,
  "queued_at": "2026-02-17T10:30:00Z"
}
```

---

## Testing Checklist

- [ ] Email address validation works correctly
- [ ] Risk classification accurate for new vs frequent contacts
- [ ] Approval workflow blocks sends to new contacts
- [ ] Auto-send works for frequent contacts
- [ ] Retry logic handles transient failures
- [ ] Authentication errors are escalated
- [ ] Rate limits are handled gracefully
- [ ] Bulk emails require approval
- [ ] HTML emails are sent correctly
- [ ] DRY_RUN mode simulates without sending
- [ ] All operations are logged
- [ ] Message IDs are returned and tracked
- [ ] Approval timeout creates escalation tasks
