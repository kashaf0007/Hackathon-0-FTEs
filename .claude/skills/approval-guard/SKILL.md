# Approval Guard

## Purpose
Enforce Autonomy Levels & Permission Boundaries by evaluating action risk level, comparing against constitutional thresholds, creating approval requests for high-risk actions, and blocking execution until approved.

## Constitutional Alignment
- **HITL Safety**: Core implementation of Human-in-the-Loop principle
- **Transparency**: All approval decisions logged
- **Local-First**: Approval requests stored as local markdown files

## Inputs
- Task objects with type and metadata
- Task type classification (delete_file, send_email, payment, etc.)
- Constitutional risk thresholds

## Outputs
- Risk level evaluation (LOW, MEDIUM, HIGH)
- Approval request files in AI_Employee_Vault/Pending_Approval/
- Approval status (PENDING, APPROVED, REJECTED)
- Blocked execution signals

## Risk Classification
**LOW** - Evaluation only, blocks execution but doesn't perform risky actions itself.

## Execution Logic
1. **Receive Task**: Get task object from Task Orchestrator
2. **Evaluate Risk**:
   - Check task.type against HIGH_RISK_ACTIONS list (delete_file, send_email, payment, execute_payment, post_social_media, dm_reply, bulk_operation)
   - Check task.type against MEDIUM_RISK_ACTIONS list (move_file_outside_vault, modify_config, create_external_resource)
   - Default to LOW risk for all other actions
3. **Determine Approval Need**:
   - HIGH risk: ALWAYS requires approval
   - MEDIUM risk: ALWAYS requires approval
   - LOW risk: Auto-approved, no blocking
4. **Create Approval Request** (if HIGH/MEDIUM):
   - Generate unique request_id (approval-001, approval-002, etc.)
   - Create ApprovalRequest model with task_id, action, risk_level, justification, impact
   - Write markdown file to Pending_Approval/ with approval template
   - Set status to PENDING
5. **Block Execution**: Return BLOCKED signal to Task Orchestrator
6. **Check Approval Status**: On subsequent checks, parse approval file for status
   - If Status: APPROVED → allow execution
   - If Status: REJECTED → cancel task
   - If Status: PENDING → continue blocking
7. **Log Decision**: Record approval creation, approval decision, and execution block/allow

## HITL Checkpoint
**Always Required For**:
- Any action in HIGH_RISK_ACTIONS list
- Any action in MEDIUM_RISK_ACTIONS list
- Any financial transaction (>$0)
- Any file deletion
- Any external communication (email, social media)

**Never Required For**:
- Drafting (without sending)
- Reading files
- Creating files within vault
- Logging operations
- Moving files within vault

**Approval Process**:
1. Approval Guard creates request file in Pending_Approval/
2. Human manually edits file, changes Status to APPROVED or REJECTED
3. Human adds approver name and decision notes
4. Approval Guard detects status change on next check
5. Execution proceeds or task cancelled based on decision

## Logging Requirements
Must log:
- **Risk Evaluation**: Every risk assessment (task_id, task_type, risk_level)
- **Approval Request Creation**: When request file created (request_id, task_id, risk_level)
- **Execution Blocked**: When high-risk action blocked (task_id, reason)
- **Approval Decision**: When human approves/rejects (request_id, decision, approver)
- **Stale Approvals**: Warning for requests >7 days old

All logs must include:
- Timestamp (ISO 8601)
- Task ID
- Skill used ("approval-guard")
- Risk level (evaluated level)
- Approval status (PENDING_APPROVAL, APPROVED, REJECTED)
- Outcome (BLOCKED for pending, SUCCESS for approved)

## Failure Handling
**File System Errors**:
- If cannot create approval file: log error, default to BLOCKING (safe failure)
- If cannot read approval file: treat as PENDING (safe failure)

**Invalid Approval Files**:
- If approval file malformed: log warning, treat as PENDING
- If status field missing: treat as PENDING

**Stale Approvals**:
- If approval >7 days old: log warning, continue blocking
- If approval >30 days old: log escalation, continue blocking

**Safe Failure Principle**: When in doubt, BLOCK execution. Better to require manual intervention than execute risky action without approval.

## Completion Condition
Approval Guard completes when:
- Risk evaluation performed and logged
- If LOW risk: returns AUTO_APPROVED immediately
- If HIGH/MEDIUM risk: approval request created and execution blocked
- Approval status checked and decision logged
- Task either proceeds (APPROVED) or cancelled (REJECTED)

**Verification**:
- For HIGH/MEDIUM risk: approval file exists in Pending_Approval/
- For APPROVED: task proceeds to execution
- For REJECTED: task moved to Done/ with FAILED status
- All decisions logged with approver identity
