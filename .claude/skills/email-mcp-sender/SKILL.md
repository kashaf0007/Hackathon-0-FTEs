# Email MCP Sender Skill

**Version**: 1.0.0
**Status**: Active
**Category**: External Communication
**Priority**: High

## Purpose

The Email MCP Sender skill provides a safe, controlled interface for sending emails through the Email MCP server with built-in approval workflows and comprehensive logging.

## Constitutional Alignment
- **HITL Safety**: All emails to new contacts require approval
- **Transparency**: All email sends are logged with full details
- **Local-First**: Email drafts stored locally before sending
- **Proactivity**: Automatically handles email composition and sending

## Capabilities

- **Email Composition**: Draft professional emails based on context
- **Address Validation**: Validate email addresses before sending
- **Approval Integration**: Request approval for emails to new contacts
- **Send via MCP**: Execute email send through Email MCP server
- **Status Tracking**: Check delivery status of sent emails
- **Error Handling**: Retry failed sends with exponential backoff

## When to Use

This skill is invoked when:

1. **Responding to Inquiries**: Reply to customer/client emails
2. **Sales Follow-ups**: Send follow-up emails to leads
3. **Support Responses**: Provide support via email
4. **Automated Notifications**: Send scheduled or triggered emails
5. **Any Email Communication**: All outbound email must use this skill

## Input Format

```json
{
  "to": "recipient@example.com",
  "subject": "Email subject line",
  "body": "Email body content",
  "from_name": "AI Employee",
  "cc": ["cc1@example.com"],
  "bcc": ["bcc1@example.com"],
  "html": false,
  "contact_history": "new|frequent",
  "context": "Additional context for approval"
}
```

## Output Format

```json
{
  "status": "sent|pending_approval|failed",
  "message_id": "gmail_message_id",
  "to": "recipient@example.com",
  "subject": "Email subject",
  "requires_approval": true,
  "approval_id": "email_20260217_001"
}
```

## Execution Flow

### Phase 1: Validation
1. **Validate Email Address**: Check recipient address format
2. **Check Contact History**: Determine if recipient is new or frequent
3. **Assess Risk**: Classify risk level (new contact = medium risk)

### Phase 2: Approval (if needed)
1. **Create Approval Request**: Generate approval file in Pending_Approval/
2. **Wait for Decision**: Poll for human approval
3. **Handle Rejection**: Cancel send if rejected or timeout

### Phase 3: Sending
1. **Call MCP Server**: Execute send_email via Email MCP server
2. **Handle Response**: Process success or error response
3. **Retry on Failure**: Retry with exponential backoff if transient error
4. **Log Outcome**: Record send status and message ID

### Phase 4: Verification
1. **Check Status**: Verify email was delivered
2. **Update Records**: Log final delivery status
3. **Move to Done**: Archive event file

## Risk Classification

### Medium Risk (Requires Approval)
- Emails to new contacts (contact_history = "new")
- Emails with attachments
- Bulk emails (multiple recipients)
- Emails containing sensitive information

### Low Risk (Auto-send)
- Emails to frequent contacts (5+ previous interactions)
- Automated acknowledgments
- Internal notifications

## Integration Points

- **MCP Client**: Uses `scripts/mcp_client.py` to call Email MCP server
- **Risk Classifier**: Uses `scripts/risk_classifier.py` for risk assessment
- **Approval Workflow**: Uses `scripts/approval_workflow.py` for HITL approval
- **Logger**: Logs all email operations via `scripts/logger.py`
- **Email MCP Server**: Executes actual email send via `mcp_servers/email_server.py`

## Error Handling

### Validation Errors
- Invalid email format → Return error, do not send
- Missing required fields → Return error with details

### Send Failures
- Network timeout → Retry up to 3 times with exponential backoff
- Authentication error → Log error, escalate to human
- Rate limit exceeded → Queue for later, log warning

### Approval Timeout
- No decision within 24 hours → Auto-reject, log timeout
- Create task in Needs_Action/ for human review

## Logging Requirements

Must log all email operations:
- **Email Drafted**: Content length, recipient, subject
- **Validation**: Address validation result
- **Risk Assessment**: Risk level and reason
- **Approval Request**: Approval ID, risk level
- **Send Attempt**: Recipient, subject, outcome
- **Delivery Status**: Message ID, delivery confirmation
- **Errors**: Failure details, retry attempts

Log format:
```json
{
  "timestamp": "2026-02-17T10:30:00Z",
  "component": "mcp",
  "action": "email_sent",
  "actor": "email_mcp_sender",
  "target": "recipient@example.com",
  "status": "success",
  "details": {
    "message_id": "msg_123",
    "subject": "Email subject",
    "requires_approval": false
  }
}
```

## Examples

See `examples.md` for detailed scenarios covering:
- Email to new contact (requires approval)
- Email to frequent contact (auto-send)
- Email send failure with retry
- Approval timeout handling
- Bulk email sending
- HTML email formatting

## Testing

Run tests with:
```bash
python -m pytest tests/test_email_mcp_sender.py -v
```

Test coverage includes:
- Email address validation
- Risk classification accuracy
- Approval workflow integration
- MCP server communication
- Error handling and retry logic
- DRY_RUN mode simulation

## Configuration

Environment variables:
- `GMAIL_CREDENTIALS_FILE`: Path to Gmail OAuth2 credentials
- `GMAIL_TOKEN_FILE`: Path to Gmail OAuth2 token (default: gmail_token.json)
- `DRY_RUN`: If "true", simulate email sends without real execution
- `MAX_RETRY_ATTEMPTS`: Maximum retries per send (default: 3)

## Dependencies

- `scripts/mcp_client.py`: MCP client for server communication
- `scripts/risk_classifier.py`: Risk assessment
- `scripts/approval_workflow.py`: HITL approval
- `scripts/logger.py`: Audit logging
- `mcp_servers/email_server.py`: Email MCP server

## Maintenance

- Monitor email delivery rates and adjust retry logic
- Review approval rates for new contacts
- Update risk classification rules based on patterns
- Audit failed sends weekly for systemic issues

## Version History

- **1.0.0** (2026-02-17): Initial implementation for Silver Tier
  - Email composition and sending via MCP
  - Approval workflow for new contacts
  - Retry logic with exponential backoff
  - Complete audit logging
  - DRY_RUN mode support

## Completion Condition

Email send completes when:
- Email validated and risk assessed
- Approval obtained (if required)
- Email sent via MCP server (or simulated in DRY_RUN)
- Delivery status confirmed
- All operations logged

**Verification**:
- Message ID returned from Gmail API
- Delivery status confirmed
- Complete audit trail in logs
- Approval file in Approved/ (if approval required)
