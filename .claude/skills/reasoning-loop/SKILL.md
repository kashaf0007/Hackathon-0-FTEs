# Reasoning Loop Skill

**Version**: 1.0.0
**Status**: Active
**Category**: Task Execution & Planning
**Priority**: Critical

## Purpose

The Reasoning Loop is the core intelligence component that analyzes complex tasks, creates structured execution plans, executes steps systematically, and tracks progress until completion.

## Constitutional Alignment
- **Proactivity**: Autonomously breaks down and executes complex tasks
- **Persistence**: Continues execution until task completion or explicit failure
- **Transparency**: All reasoning steps and decisions are logged
- **HITL Safety**: Integrates with Approval Guard for risky actions
- **Local-First**: All plans and state stored locally in Plan.md

## Capabilities

- **Task Analysis**: Classify events by complexity, category, and priority
- **Plan Generation**: Create structured multi-step execution plans
- **Step Execution**: Execute plan steps systematically with error handling
- **Progress Tracking**: Update Plan.md after each step completion
- **Risk Integration**: Assess risk and request approval when needed
- **Error Recovery**: Handle failures with retry logic and escalation

## When to Use

This skill is invoked when:

1. **Complex Events**: Multi-step tasks requiring structured planning
2. **Sales Opportunities**: Lead qualification and follow-up workflows
3. **Complaints**: Careful handling requiring multiple steps
4. **Critical Priority**: Urgent tasks requiring immediate structured response
5. **Multi-Step Workflows**: Any task with 4+ execution steps

## Input Format

```json
{
  "event_id": "event_20260217_001",
  "source": "gmail|linkedin|whatsapp",
  "type": "new_message|connection_request|etc",
  "content": "Event content text",
  "metadata": {
    "from": "sender@example.com",
    "subject": "Email subject",
    "priority": "high|medium|low"
  }
}
```

## Output Format

```json
{
  "plan_created": true,
  "plan_file": "AI_Employee_Vault/Plan.md",
  "complexity": "simple|complex|routine|critical",
  "category": "sales|support|complaint|general|routine",
  "priority": "low|medium|high|urgent",
  "estimated_steps": 5,
  "requires_approval": true,
  "status": "in_progress|completed|failed"
}
```

## Execution Flow

### Phase 1: Analysis
1. **Receive Event**: Get event from event queue
2. **Analyze Task**: Use TaskAnalyzer to classify complexity, category, priority
3. **Determine Strategy**: Decide if plan is needed or simple response suffices
4. **Assess Risk**: Use RiskClassifier to determine if approval needed

### Phase 2: Planning
1. **Generate Objective**: Extract clear objective from event
2. **Gather Context**: Collect relevant background information
3. **Propose Actions**: Generate high-level action items
4. **Break Down Steps**: Create detailed step-by-step execution plan
5. **Create Plan.md**: Write structured plan using PlanGenerator

### Phase 3: Execution
1. **Execute Step**: Run current step with appropriate tools/actions
2. **Check Status**: Verify step completion or detect failure
3. **Update Plan**: Mark step status in Plan.md
4. **Handle Errors**: Retry on failure or escalate if needed
5. **Check Approval**: If step requires approval, wait for human decision
6. **Continue Loop**: Move to next step until all complete

### Phase 4: Completion
1. **Verify Completion**: Ensure all steps executed successfully
2. **Mark Complete**: Update Plan.md with completion status
3. **Move to Done**: Move event file to Done/ directory
4. **Log Outcome**: Record final status and metrics
5. **Clean Up**: Archive plan if needed

## Task Classification

### Simple Tasks (No Plan Needed)
- Single-step responses
- Routine acknowledgments
- Read-only operations
- Internal file operations

**Handling**: Direct execution without Plan.md

### Complex Tasks (Plan Required)
- Multi-step workflows
- Sales opportunities
- Complaint handling
- Project requests

**Handling**: Full planning and execution loop

### Routine Tasks (Predefined Plan)
- Scheduled posts
- Weekly reports
- Automated follow-ups

**Handling**: Execute predefined workflow template

### Critical Tasks (Urgent Plan)
- Emergency requests
- High-priority complaints
- Time-sensitive opportunities

**Handling**: Expedited planning and execution

## Integration Points

- **Event Queue**: Receives events from `scripts/event_queue.py`
- **Task Analyzer**: Uses `scripts/task_analyzer.py` for classification
- **Plan Generator**: Uses `scripts/plan_generator.py` for Plan.md management
- **Risk Classifier**: Uses `scripts/risk_classifier.py` for risk assessment
- **Approval Workflow**: Uses `scripts/approval_workflow.py` for HITL approval
- **Step Executor**: Uses `scripts/step_executor.py` for step execution
- **Logger**: Logs all reasoning and execution events

## Error Handling

### Step Execution Failures
- **Retry Logic**: Retry failed steps up to 3 times with exponential backoff
- **Escalation**: After 3 failures, mark step as failed and log for human review
- **Partial Success**: Continue with remaining steps if failure is non-blocking

### Plan Generation Failures
- **Fallback**: If plan generation fails, attempt simple response
- **Logging**: Log failure details for debugging
- **Human Notification**: Create task in Needs_Action/ for human review

### Approval Timeouts
- **Wait Strategy**: Poll approval status every 60 seconds
- **Timeout Handling**: If approval times out, mark task as failed
- **Notification**: Log timeout event and move to Done/ with failed status

### Resource Errors
- **File Locks**: Retry file operations with exponential backoff
- **API Limits**: Respect rate limits and queue for later
- **Network Errors**: Retry with backoff, escalate after 3 failures

## Logging Requirements

Must log all reasoning loop events:
- **Event Analysis**: Classification results (complexity, category, priority)
- **Plan Creation**: Plan file path, objective, estimated steps
- **Step Execution**: Step ID, status, duration, outcome
- **Approval Requests**: Action ID, risk level, approval status
- **Completion**: Final status, total duration, steps completed/failed
- **Errors**: Failure details, retry attempts, escalation decisions

Log format:
```json
{
  "timestamp": "2026-02-17T10:30:00Z",
  "component": "reasoning",
  "action": "event_analyzed|plan_created|step_executed|task_completed",
  "actor": "reasoning_loop",
  "target": "event_id",
  "status": "success|warning|error",
  "details": {
    "complexity": "complex",
    "steps_completed": 5,
    "duration_ms": 12345
  }
}
```

## Examples

See `examples.md` for detailed scenarios covering:
- Sales opportunity workflow
- Complaint handling workflow
- Support request workflow
- Routine task execution
- Error recovery scenarios
- Approval integration
- Multi-step plan execution

## Testing

Run tests with:
```bash
python -m pytest tests/test_reasoning_loop.py -v
```

Test coverage includes:
- Task classification accuracy
- Plan generation for all complexity levels
- Step execution with success/failure scenarios
- Error recovery and retry logic
- Approval workflow integration
- Progress tracking accuracy
- Completion handling

## Configuration

Environment variables:
- `MAX_RETRY_ATTEMPTS`: Maximum retries per step (default: 3)
- `STEP_TIMEOUT_SECONDS`: Timeout per step (default: 300)
- `APPROVAL_POLL_INTERVAL`: Seconds between approval checks (default: 60)
- `DRY_RUN`: If "true", simulate execution without real actions

## Dependencies

- `scripts/task_analyzer.py`: Event classification
- `scripts/plan_generator.py`: Plan.md creation and updates
- `scripts/step_executor.py`: Step execution logic
- `scripts/risk_classifier.py`: Risk assessment
- `scripts/approval_workflow.py`: HITL approval
- `scripts/event_queue.py`: Event management
- `scripts/logger.py`: Audit logging

## Maintenance

- Monitor task completion rates and adjust classification rules
- Review failed tasks weekly to improve error handling
- Update action templates based on common patterns
- Tune retry logic based on failure analysis
- Optimize step execution for performance

## Version History

- **1.0.0** (2026-02-17): Initial implementation for Silver Tier
  - Task analysis with 4 complexity levels
  - Structured plan generation
  - Step-by-step execution with progress tracking
  - Error recovery with retry logic
  - Approval workflow integration
  - Complete audit logging

## Completion Condition

Reasoning Loop completes when:
- Event analyzed and classified
- Plan created (if needed) and logged
- All steps executed or failed with retry exhaustion
- Plan.md updated with final status
- Event moved to Done/ directory
- All decisions and outcomes logged

**Verification**:
- Plan.md exists with complete execution history
- All steps marked as completed or failed
- Event file in Done/ directory
- Complete audit trail in logs
