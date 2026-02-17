# Approval Guard Skill

**Version**: 1.0.0
**Status**: Active
**Category**: Safety & Governance
**Priority**: Critical

## Purpose

The Approval Guard is a critical safety component that enforces Human-in-the-Loop (HITL) safety by ensuring all medium and high-risk actions require explicit human approval before execution.

## Constitutional Alignment
- **HITL Safety**: Core implementation of Human-in-the-Loop principle
- **Transparency**: All approval decisions logged with complete audit trail
- **Local-First**: Approval requests stored as local markdown files
- **Proactivity**: Detects risks before they cause harm
- **Accountability**: Clear audit trail of who approved what

## Capabilities

- **Risk Assessment**: Classify actions into low, medium, or high risk based on content, type, and metadata
- **Approval Enforcement**: Block medium/high risk actions until approved by human
- **Request Generation**: Create clear, human-readable approval requests in Markdown format
- **Status Monitoring**: Track approval decisions (approved, rejected, pending, timeout)
- **Audit Logging**: Maintain complete audit trail of all decisions

## Inputs

```json
{
  "action_id": "unique_action_identifier",
  "action_type": "email_send|linkedin_post|payment|file_delete|etc",
  "content": "Description of what will be done",
  "metadata": {
    "to": "recipient@example.com",
    "amount": 750.00,
    "contact_history": "new|frequent",
    "new_payee": true,
    "visibility": "public|private",
    "file_path": "/path/to/file"
  }
}
```

## Outputs

```json
{
  "risk_level": "low|medium|high",
  "requires_approval": true|false,
  "reason": "Clear explanation of risk classification",
  "approval_request_file": "AI_Employee_Vault/Pending_Approval/action_id.md",
  "action": "proceed|wait_for_approval|reject"
}
```

## Risk Classification

### High Risk (ALWAYS require approval)
- Financial transactions > $500
- New payees (first transaction)
- File deletions or destructive operations
- Legal, medical, or emotional content
- Contract modifications
- Keywords: payment, transfer, delete, legal, medical, terminate

### Medium Risk (ALWAYS require approval)
- Financial transactions $50-$500
- Emails to new contacts
- Social media posts (LinkedIn, Twitter, etc.)
- Public communications
- Sensitive contexts (conflict, negotiation, complaint)
- Keywords: email, send, post, publish, new contact, external

### Low Risk (Can auto-execute)
- Emails to frequent contacts (5+ previous interactions)
- Internal file operations (read, create within vault)
- Routine tasks with no external impact
- Read-only operations

### Default to Safety
When uncertain about risk level, ALWAYS require approval. Better to be cautious than to execute a risky action without human oversight.

## Approval Workflow

1. **Request Creation**: Generate approval request file in `AI_Employee_Vault/Pending_Approval/`
2. **Human Review**: Human moves file to `Approved/` or `Rejected/`
3. **Status Check**: System polls for file movement
4. **Execution**: Proceed if approved, cancel if rejected
5. **Timeout**: Auto-reject after 24 hours if no decision

## Execution Logic

1. **Receive Action Request**: Get action details from event processing or task orchestrator
2. **Evaluate Risk**: Use `scripts/risk_classifier.py` to classify based on keywords and metadata
3. **Determine Approval Need**:
   - HIGH risk: ALWAYS requires approval
   - MEDIUM risk: ALWAYS requires approval
   - LOW risk: Auto-approved, no blocking
4. **Create Approval Request** (if HIGH/MEDIUM):
   - Generate unique action_id
   - Use `ApprovalWorkflow.request_approval()` to create Markdown file
   - File includes: description, risk assessment, action details, instructions
   - Set expiration time (default: 24 hours)
5. **Block Execution**: Return wait_for_approval signal
6. **Check Approval Status**: Poll using `ApprovalWorkflow.check_approval_status()`
   - If file in Approved/ → allow execution
   - If file in Rejected/ → cancel task
   - If file in Pending_Approval/ → continue blocking
   - If timeout expired → auto-reject and move to Rejected/
7. **Log Decision**: Record all risk assessments and approval decisions

## HITL Checkpoint

**Always Required For**:
- LinkedIn posting
- Email sending (to new contacts)
- Any payment or financial transaction
- Any irreversible action (file deletion, contract modification)
- Legal, medical, or emotional content
- Public communications

**Never Required For**:
- Drafting (without sending)
- Reading files
- Creating files within vault
- Logging operations
- Moving files within vault
- Emails to frequent contacts (5+ previous interactions)

**Approval Process**:
1. Approval Guard creates request file in `Pending_Approval/` with clear description and risk assessment
2. Human reviews the request file
3. Human moves file to `Approved/` (to approve) or `Rejected/` (to reject)
4. Approval Guard detects file movement on next status check
5. Execution proceeds if approved, cancelled if rejected
6. Auto-reject after timeout (default: 24 hours)

## Logging Requirements

Must log all approval-related events:
- **Risk Evaluation**: Every risk assessment with action_id, action_type, risk_level, reason
- **Approval Request Creation**: When request file created with action_id, risk_level, expires_at
- **Execution Blocked**: When action blocked pending approval with action_id, reason
- **Approval Decision**: When human approves/rejects with action_id, decision, file_path
- **Timeout Events**: When approval request expires with action_id, timeout_hours

All logs use the standard logging format:
```json
{
  "timestamp": "2026-02-17T10:30:00Z",
  "component": "approval",
  "action": "approval_requested|approval_granted|approval_rejected|approval_timeout",
  "actor": "approval_workflow|human|system",
  "target": "action_id",
  "status": "success|warning|error",
  "details": {
    "action_type": "email_send",
    "risk_level": "medium",
    "expires_at": "2026-02-18T10:30:00Z"
  }
}
```

## Error Handling

**File System Errors**:
- If cannot create approval file: log error, default to BLOCKING (safe failure)
- If cannot read approval file: treat as PENDING (safe failure)
- If cannot move file: log error, continue blocking

**Invalid Approval Files**:
- If approval file malformed: log warning, treat as PENDING
- If metadata missing: log warning, treat as PENDING
- If expires_at invalid: use file modification time + timeout_hours

**Timeout Handling**:
- Check expiration on every status check
- Auto-move to Rejected/ when expired
- Log timeout event with action_id and timeout_hours

**Safe Failure Principle**: When in doubt, BLOCK execution. Better to require manual intervention than execute risky action without approval.

## Integration Points

- **Event Queue**: Receives action requests from `scripts/event_queue.py`
- **Approval Workflow**: Uses `scripts/approval_workflow.py` for file management
- **Logger**: Logs all decisions via `scripts/logger.py`
- **Risk Classifier**: Uses `scripts/risk_classifier.py` for keyword-based classification
- **Task Orchestrator**: Returns approval status to orchestrator for execution control
- **MCP Servers**: Blocks MCP action execution until approval granted

## Examples

See `examples.md` for 10 detailed scenarios covering:
- Email to new contact (medium risk)
- LinkedIn post (medium risk)
- Payment to new vendor (high risk)
- Email to frequent contact (low risk)
- File deletion (high risk)
- Approval timeout handling
- Approval granted/rejected flows
- Missing metadata handling
- DRY_RUN mode testing

## Testing

Run tests with:
```bash
python -m pytest tests/test_approval_guard.py -v
```

Test coverage includes:
- Risk classification accuracy for all risk levels
- Approval file creation with correct format
- Status checking (approved/rejected/pending/timeout)
- Timeout mechanism (24-hour default)
- File movement detection
- Edge cases (missing metadata, malformed files)
- DRY_RUN mode simulation

## Configuration

Environment variables:
- `APPROVAL_TIMEOUT_HOURS`: Hours before auto-reject (default: 24)
- `DRY_RUN`: If "true", simulate approval workflow without real execution

Configuration in `AI_Employee_Vault/Watchers/watcher_config.json`:
```json
{
  "approval": {
    "timeout_hours": 24,
    "auto_reject_on_timeout": true
  }
}
```

## Dependencies

- `scripts/approval_workflow.py`: Approval file management and status checking
- `scripts/risk_classifier.py`: Risk assessment logic with keyword matching
- `scripts/logger.py`: Audit logging with JSON format
- `scripts/file_utils.py`: Atomic file operations with cross-platform locking

## Maintenance

- Review risk keywords quarterly based on false positive/negative rates
- Update examples as new scenarios emerge
- Monitor approval timeout rates and adjust if needed
- Audit approval decisions for compliance
- Update risk thresholds based on business requirements

## Version History

- **1.0.0** (2026-02-17): Initial implementation for Silver Tier
  - Risk classification (low/medium/high)
  - File-based approval workflow with drag-and-drop
  - 24-hour timeout mechanism with auto-reject
  - Complete audit logging
  - Integration with ApprovalWorkflow class
  - 10 example scenarios with test cases

## Completion Condition

Approval Guard completes when:
- Risk evaluation performed and logged
- If LOW risk: returns proceed immediately
- If HIGH/MEDIUM risk: approval request created and execution blocked
- Approval status checked and decision logged
- Action either proceeds (approved) or cancelled (rejected/timeout)

**Verification**:
- For HIGH/MEDIUM risk: approval file exists in `Pending_Approval/`
- For APPROVED: file moved to `Approved/` and action proceeds
- For REJECTED: file moved to `Rejected/` and action cancelled
- All decisions logged with complete audit trail
