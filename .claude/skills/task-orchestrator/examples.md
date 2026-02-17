# Task Orchestrator Skill - Examples

## Example 1: Simple Email Response (Auto-Send)

**Input Task**:
```json
{
  "id": "gmail_20260218_001",
  "source": "gmail",
  "type": "new_message",
  "content": "Thanks for the update!",
  "metadata": {
    "from": "regular.client@example.com",
    "contact_history": "frequent"
  }
}
```

**Orchestration Decision**:
```json
{
  "routing": {
    "skill": "email-mcp-sender",
    "reason": "Simple response to frequent contact",
    "requires_plan": false,
    "requires_approval": false
  }
}
```

**Execution**: Direct skill invocation → Email sent → Task moved to Done/

---

## Example 2: Complex Sales Inquiry (Multi-Step)

**Input Task**:
```json
{
  "id": "gmail_20260218_002",
  "source": "gmail",
  "type": "new_message",
  "content": "Interested in your AI automation services. Need pricing and demo.",
  "metadata": {
    "from": "john@techcorp.com",
    "contact_history": "new"
  }
}
```

**Orchestration Decision**:
```json
{
  "routing": {
    "skill": "reasoning-loop",
    "reason": "Complex sales inquiry requires multi-step workflow",
    "requires_plan": true,
    "requires_approval": true
  }
}
```

**Execution Flow**:
1. Invoke reasoning-loop skill
2. Reasoning-loop creates Plan.md with 6 steps
3. Reasoning-loop executes steps sequentially
4. Step 3 requires approval (email to new contact)
5. Wait for approval
6. Continue execution after approval
7. Complete and move to Done/

---

## Example 3: Scheduled LinkedIn Post

**Input Task**:
```json
{
  "id": "scheduled_20260218_003",
  "source": "scheduler",
  "type": "weekly_linkedin_post",
  "content": "Generate weekly LinkedIn post",
  "metadata": {
    "schedule": "weekly",
    "day": "Monday"
  }
}
```

**Orchestration Decision**:
```json
{
  "routing": {
    "skill": "linkedin-post-generator",
    "reason": "Scheduled content generation",
    "requires_plan": false,
    "requires_approval": true
  }
}
```

**Execution**: linkedin-post-generator → Draft created → Approval requested → Post published

---

## Example 4: Concurrent Task Processing

**Scenario**: Multiple independent tasks in queue

**Tasks**:
1. Email response (frequent contact)
2. Dashboard update
3. Health check
4. LinkedIn post (requires approval)

**Orchestration Strategy**:
- Tasks 1, 2, 3 run in parallel (independent, no shared resources)
- Task 4 runs separately (requires approval, blocks its own workflow only)

**Execution**:
```
10:00:00 - Start all 4 tasks
10:00:01 - Tasks 1, 2, 3 executing in parallel
10:00:01 - Task 4 creates approval request
10:00:15 - Task 1 completes (email sent)
10:00:20 - Task 2 completes (dashboard updated)
10:00:25 - Task 3 completes (health check done)
10:00:30 - Task 4 waiting for approval...
11:00:00 - Task 4 approved and published
```

---

## Example 5: Error Recovery with Retry

**Input Task**: Email send

**Execution Log**:
```
10:00:00 - Route to email-mcp-sender
10:00:05 - Skill invocation: email-mcp-sender
10:00:10 - ERROR: Network timeout
10:00:10 - Retry 1/3 (wait 5s)
10:00:15 - Skill invocation: email-mcp-sender
10:00:20 - ERROR: Network timeout
10:00:20 - Retry 2/3 (wait 15s)
10:00:35 - Skill invocation: email-mcp-sender
10:00:40 - SUCCESS: Email sent
10:00:40 - Move to Done/
```

**State Transitions**: Pending → In Progress → Retrying → Completed

---

## Example 6: Permanent Failure with Escalation

**Input Task**: Invalid task format

**Execution Log**:
```
10:00:00 - Parse task file
10:00:01 - ERROR: Invalid JSON format
10:00:01 - Permanent error detected (no retry)
10:00:01 - Create escalation task in Needs_Action/
10:00:01 - Move original task to Done/ with FAILED status
```

**Escalation Task Created**:
```markdown
# ESCALATION: Task Processing Failed

**Original Task**: gmail_20260218_005
**Error**: Invalid JSON format in task file
**Action Required**: Fix task file format and resubmit
```

---

## Example 7: Resource Management (Queue Full)

**Scenario**: 10 tasks already running (max concurrency reached)

**New Task Arrives**: Email response

**Orchestration Decision**:
```json
{
  "status": "queued",
  "reason": "Max concurrency reached (10/10)",
  "queue_position": 1,
  "estimated_wait": "30 seconds"
}
```

**Execution**: Wait for slot to open → Process when available

---

## Example 8: Priority Handling

**Tasks in Queue**:
1. Low priority: Weekly report
2. Medium priority: Email response
3. High priority: Sales inquiry
4. Urgent priority: Customer complaint

**Orchestration Order**:
1. Process urgent first (customer complaint)
2. Process high next (sales inquiry)
3. Process medium (email response)
4. Process low last (weekly report)

---

## Example 9: Approval Timeout Handling

**Input Task**: LinkedIn post requiring approval

**Execution Log**:
```
Monday 09:00 - Post generated
Monday 09:01 - Approval requested
Monday 09:01 - State: Waiting Approval
... 24 hours pass ...
Tuesday 09:01 - Approval timeout detected
Tuesday 09:01 - Auto-reject post
Tuesday 09:01 - Move to Done/ with TIMEOUT status
Tuesday 09:01 - Create escalation task
```

---

## Example 10: State Tracking Throughout Workflow

**Task**: Complex sales inquiry

**State Transitions**:
```
10:00:00 - Pending (in Needs_Action/)
10:00:05 - In Progress (reasoning-loop invoked)
10:00:10 - In Progress (Plan.md created)
10:00:15 - In Progress (executing step 1)
10:00:20 - In Progress (executing step 2)
10:00:25 - Waiting Approval (step 3 requires approval)
10:30:00 - In Progress (approval granted, continuing)
10:30:05 - In Progress (executing step 4)
10:30:10 - In Progress (executing step 5)
10:30:15 - In Progress (executing step 6)
10:30:20 - Completed (moved to Done/)
```

**Total Duration**: 30 minutes 20 seconds
**Steps Completed**: 6/6
**Approvals Required**: 1
**Outcome**: Success

---

## Testing Checklist

- [ ] Simple tasks route to correct skills
- [ ] Complex tasks invoke reasoning-loop
- [ ] Approval-required tasks block correctly
- [ ] Concurrent tasks execute in parallel
- [ ] Sequential tasks respect dependencies
- [ ] Retry logic works for transient errors
- [ ] Permanent errors create escalations
- [ ] Resource limits prevent overload
- [ ] Priority ordering works correctly
- [ ] State transitions logged accurately
- [ ] Approval timeouts handled properly
- [ ] All tasks eventually reach Done/
