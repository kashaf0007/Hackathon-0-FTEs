# Task Orchestrator

## Purpose
Manage multi-step tasks using Plan.md, break tasks into steps, track status, coordinate execution with other skills, and move completed tasks to Done/.

## Constitutional Alignment
- **Persistence**: Continues task execution until completion or explicit failure
- **Transparency**: Logs all state transitions
- **Local-First**: All operations on local file system

## Inputs
- Task files in AI_Employee_Vault/Needs_Action/
- Task metadata (type, priority, context)
- Expected output requirements

## Outputs
- Plan.md files for complex tasks (in AI_Employee_Vault/)
- Completed tasks moved to AI_Employee_Vault/Done/
- Task execution results (success/failure)
- State transition logs

## Risk Classification
**LOW** - Orchestration only, no external actions. Coordinates other skills but doesn't perform high-risk operations itself.

## Execution Logic
1. **Parse Task**: Read task file from Needs_Action/, extract metadata and context
2. **Assess Complexity**: Determine if task needs Plan.md (multi-step) or can execute directly
3. **Create Plan** (if complex): Generate Plan.md with steps, objectives, and status tracking
4. **Execute Task**:
   - For draft_email: Generate email draft based on context
   - For organize_files: Organize files according to rules
   - For create_report: Generate report from data
   - For generic: Execute based on task type
5. **Track Status**: Update task status (PENDING → IN_PROGRESS → COMPLETED/FAILED)
6. **Log Transitions**: Record all state changes via Logging & Audit skill
7. **Move to Done**: On completion, move task file to Done/ directory
8. **Handle Errors**: On failure, increment retry count and log error details

## HITL Checkpoint
Task Orchestrator itself doesn't require approval (LOW risk). However, it coordinates with Approval Guard to check if the task being orchestrated requires approval before execution.

**Approval Flow**:
- Task Orchestrator receives task
- Calls Approval Guard to evaluate risk
- If HIGH/MEDIUM risk: blocks and waits for approval
- If LOW risk or approved: proceeds with execution

## Logging Requirements
Must log:
- **Task Start**: When task begins processing (task_id, type, priority)
- **State Transitions**: Every status change (PENDING → IN_PROGRESS → COMPLETED)
- **Execution Results**: Success/failure with output or error message
- **Task Completion**: When task moves to Done/ (task_id, duration, outcome)
- **Retry Attempts**: If task fails and retries (retry_count, error)

All logs must include:
- Timestamp (ISO 8601)
- Task ID
- Skill used ("task-orchestrator")
- Risk level (LOW)
- Approval status (AUTO_APPROVED)
- Outcome (SUCCESS/FAILURE)

## Failure Handling
**Transient Failures** (retry up to 3 times):
- File lock conflicts
- Temporary file system errors
- Parsing errors in task files

**Permanent Failures** (no retry):
- Invalid task schema
- Missing required fields
- Skill not found

**Failure Response**:
1. Log error with full context
2. If retryable: increment retry_count, wait 5s, retry
3. If max retries exceeded (3): create help request in Needs_Action/
4. If permanent: move to Done/ with FAILED status and error message

## Completion Condition
Task is complete when:
- Task file successfully moved to Done/ directory
- Task status set to COMPLETED or FAILED
- Completion logged with outcome and output
- `<promise>TASK_COMPLETE</promise>` marker emitted in logs

**Verification**:
- Task file no longer exists in Needs_Action/
- Task file exists in Done/ with final status
- Log entry shows completion with task_id and outcome
