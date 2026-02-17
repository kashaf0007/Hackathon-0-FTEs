# Reasoning Loop Skill - Examples

## Example 1: Sales Opportunity - Complex Multi-Step Workflow

**Input Event**:
```json
{
  "event_id": "gmail_20260217_001",
  "source": "gmail",
  "type": "new_message",
  "content": "Hi, I'm interested in your AI automation services. Can you send me pricing information and schedule a demo? We're looking to automate our customer support workflows. Thanks, John Smith, CTO at TechCorp",
  "metadata": {
    "from": "john.smith@techcorp.com",
    "subject": "Inquiry about AI automation services",
    "contact_history": "new"
  }
}
```

**Analysis Output**:
```json
{
  "complexity": "complex",
  "category": "sales",
  "priority": "high",
  "requires_plan": true,
  "estimated_steps": 6,
  "reason": "Sales opportunity requires multi-step qualification and follow-up"
}
```

**Generated Plan** (Plan.md):
```markdown
# Current Execution Plan

**Status**: Active
**Created**: 2026-02-17T10:30:00Z

## Objective
Qualify sales lead from TechCorp and provide pricing/demo information

## Context
New inbound lead from CTO at TechCorp interested in AI automation for customer support

## Proposed Actions
1. Research TechCorp company profile
2. Draft personalized response with pricing tiers
3. Offer demo scheduling options
4. Provide case studies relevant to customer support automation
5. Schedule follow-up reminder

## Risk Assessment
- **Risk Level**: medium
- **Requires Approval**: Yes (email to new contact)

## Execution Steps
⏳ **step_1**: Research TechCorp company profile and size
⏳ **step_2**: Draft personalized email response
⏳ **step_3**: Request approval for email send
⏳ **step_4**: Send email (after approval)
⏳ **step_5**: Log opportunity in CRM
⏳ **step_6**: Schedule 3-day follow-up reminder

## Progress Tracking
- **Total Steps**: 6
- **Completed**: 0
- **In Progress**: 0
- **Pending**: 6
- **Failed**: 0
```

**Execution Flow**:
1. Step 1 executes → Research completed → Status: ✅
2. Step 2 executes → Email drafted → Status: ✅
3. Step 3 executes → Approval request created in Pending_Approval/ → Status: 🔄
4. Wait for human approval...
5. Human moves file to Approved/
6. Step 4 executes → Email sent via MCP → Status: ✅
7. Step 5 executes → CRM updated → Status: ✅
8. Step 6 executes → Reminder scheduled → Status: ✅
9. Plan marked complete with outcome: "success"

---

## Example 2: Complaint Handling - Critical Priority

**Input Event**:
```json
{
  "event_id": "linkedin_20260217_002",
  "source": "linkedin",
  "type": "new_message",
  "content": "URGENT: Your service has been down for 3 hours and we're losing customers. This is completely unacceptable. I need an immediate response and compensation for this outage.",
  "metadata": {
    "from": "Sarah Johnson",
    "company": "RetailCo",
    "contact_history": "frequent"
  }
}
```

**Analysis Output**:
```json
{
  "complexity": "critical",
  "category": "complaint",
  "priority": "urgent",
  "requires_plan": true,
  "estimated_steps": 7,
  "reason": "Urgent complaint requires immediate structured response"
}
```

**Generated Plan**:
```markdown
## Objective
Resolve urgent service outage complaint and restore customer satisfaction

## Execution Steps
⏳ **step_1**: Acknowledge complaint immediately
⏳ **step_2**: Investigate current service status
⏳ **step_3**: Draft apology and explanation
⏳ **step_4**: Propose compensation (requires approval)
⏳ **step_5**: Escalate to technical team
⏳ **step_6**: Send response (after approval)
⏳ **step_7**: Schedule follow-up in 24 hours
```

**Execution with Error Recovery**:
1. Step 1 → Immediate acknowledgment sent → ✅
2. Step 2 → Service status check fails (API timeout) → ❌
3. Retry step 2 (attempt 2) → Success → ✅
4. Step 3 → Apology drafted → ✅
5. Step 4 → Compensation proposal created → Approval requested → 🔄
6. Human approves compensation
7. Step 5 → Technical team notified → ✅
8. Step 6 → Response sent → ✅
9. Step 7 → Follow-up scheduled → ✅

---

## Example 3: Simple Task - No Plan Needed

**Input Event**:
```json
{
  "event_id": "gmail_20260217_003",
  "source": "gmail",
  "type": "new_message",
  "content": "Thanks for the update. Looks good!",
  "metadata": {
    "from": "regular.client@example.com",
    "subject": "Re: Project Status Update",
    "contact_history": "frequent"
  }
}
```

**Analysis Output**:
```json
{
  "complexity": "simple",
  "category": "general",
  "priority": "low",
  "requires_plan": false,
  "estimated_steps": 1,
  "reason": "Simple acknowledgment, no action needed"
}
```

**Execution**:
- No Plan.md created
- Direct response: "You're welcome! Let me know if you need anything else."
- Event moved to Done/
- Total execution time: <5 seconds

---

## Example 4: Routine Task - Predefined Workflow

**Input Event**:
```json
{
  "event_id": "scheduled_20260217_004",
  "source": "scheduler",
  "type": "weekly_linkedin_post",
  "content": "Generate weekly LinkedIn post about AI automation benefits",
  "metadata": {
    "schedule": "weekly",
    "day": "Monday",
    "time": "09:00"
  }
}
```

**Analysis Output**:
```json
{
  "complexity": "routine",
  "category": "routine",
  "priority": "low",
  "requires_plan": true,
  "estimated_steps": 4,
  "reason": "Routine task with predefined workflow"
}
```

**Generated Plan**:
```markdown
## Objective
Generate and publish weekly LinkedIn post about AI automation

## Execution Steps
⏳ **step_1**: Read Business_Goals.md for content direction
⏳ **step_2**: Generate post content aligned with goals
⏳ **step_3**: Request approval for public post
⏳ **step_4**: Publish to LinkedIn (after approval)
```

---

## Example 5: Error Recovery - Retry Logic

**Scenario**: Email send fails due to network error

**Execution Log**:
```
10:30:00 - step_4: Send email via MCP
10:30:05 - ERROR: Network timeout
10:30:05 - Retry attempt 1/3 (wait 5s)
10:30:10 - ERROR: Connection refused
10:30:10 - Retry attempt 2/3 (wait 15s)
10:30:25 - ERROR: Network timeout
10:30:25 - Retry attempt 3/3 (wait 45s)
10:31:10 - SUCCESS: Email sent
10:31:10 - step_4: Status updated to ✅
```

**Plan.md Update**:
```markdown
### Step Update: step_4

Encountered network errors during email send. Successfully sent after 3 retry attempts.
Total retry duration: 70 seconds.
```

---

## Example 6: Approval Integration

**Scenario**: Medium-risk action requires approval

**Step Execution**:
```python
# Step 3: Send email to new contact
risk_level, reason = risk_classifier.classify(
    action_type="email_send",
    content=email_draft,
    metadata={"to": "new.contact@example.com", "contact_history": "new"}
)
# Returns: ("medium", "Email to new contact requires approval")

if risk_level in ["medium", "high"]:
    approval_file = approval_workflow.request_approval(
        action_id="email_20260217_001",
        action_type="email_send",
        description="Send pricing information to new sales lead",
        risk_level=risk_level,
        action_data={"to": "new.contact@example.com", "subject": "..."}
    )

    # Update step status to waiting for approval
    plan_generator.update_step_status("step_3", "in_progress",
        "Waiting for approval in Pending_Approval/")

    # Wait for approval (polling)
    status, file_path = approval_workflow.wait_for_approval(
        action_id="email_20260217_001",
        poll_interval=60
    )

    if status == "approved":
        # Proceed with email send
        execute_email_send()
        plan_generator.update_step_status("step_3", "completed")
    else:
        # Approval rejected or timeout
        plan_generator.update_step_status("step_3", "failed",
            f"Approval {status}: email not sent")
```

---

## Example 7: Partial Success - Continue Despite Failure

**Scenario**: Non-critical step fails but workflow continues

**Plan Execution**:
```markdown
✅ **step_1**: Research company profile
✅ **step_2**: Draft email response
✅ **step_3**: Send email
❌ **step_4**: Log to CRM (CRM API unavailable)
✅ **step_5**: Schedule follow-up reminder
```

**Completion Notes**:
```
Outcome: Partial success
- 4 of 5 steps completed successfully
- Step 4 failed: CRM API unavailable (logged for manual retry)
- Core objective achieved: Email sent and follow-up scheduled
- Action required: Manually log opportunity in CRM when API restored
```

---

## Example 8: Escalation - Retry Exhausted

**Scenario**: Critical step fails after all retries

**Execution Log**:
```
11:00:00 - step_2: Send payment via MCP
11:00:05 - ERROR: Payment gateway timeout
11:00:05 - Retry 1/3 (wait 5s)
11:00:10 - ERROR: Payment gateway timeout
11:00:10 - Retry 2/3 (wait 15s)
11:00:25 - ERROR: Payment gateway timeout
11:00:25 - Retry 3/3 (wait 45s)
11:01:10 - ERROR: Payment gateway timeout
11:01:10 - ESCALATION: Creating task for human review
```

**Escalation Task Created** (Needs_Action/):
```markdown
# ESCALATION: Payment Failed After Retries

**Event ID**: payment_20260217_001
**Step**: step_2 (Send payment)
**Failure**: Payment gateway timeout after 3 retry attempts
**Impact**: Payment of $500 to vendor not completed

## Action Required
1. Check payment gateway status
2. Verify vendor account details
3. Manually process payment or reschedule
4. Update Plan.md when resolved

## Error Details
- Gateway: Stripe
- Amount: $500.00
- Payee: Vendor LLC
- Error: Connection timeout (60s)
- Retry attempts: 3
- Total duration: 70 seconds
```

---

## Testing Checklist

- [ ] Simple tasks execute without creating Plan.md
- [ ] Complex tasks generate structured plans
- [ ] Critical tasks execute with high priority
- [ ] Routine tasks follow predefined workflows
- [ ] Step status updates correctly in Plan.md
- [ ] Retry logic works for transient failures
- [ ] Escalation creates tasks after retry exhaustion
- [ ] Approval integration blocks execution correctly
- [ ] Partial success continues with remaining steps
- [ ] All execution events are logged
- [ ] Plan completion marks final status correctly
- [ ] Error recovery handles all failure types
