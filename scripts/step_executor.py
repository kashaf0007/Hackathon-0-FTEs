"""
StepExecutor class - Executes plan steps with error handling and retry logic.
Handles step execution, status tracking, error recovery, and completion.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Tuple

from scripts.logger import get_logger
from scripts.plan_generator import get_plan_generator
from scripts.risk_classifier import get_risk_classifier
from scripts.approval_workflow import get_approval_workflow


class StepExecutor:
    """
    Executes plan steps with error handling, retry logic, and status tracking.

    Features:
    - Retry failed steps with exponential backoff
    - Risk assessment and approval integration
    - Progress tracking in Plan.md
    - Error recovery and escalation
    - Comprehensive logging
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_retry_delay: int = 5,
        step_timeout: int = 300
    ):
        """
        Initialize step executor.

        Args:
            max_retries: Maximum retry attempts per step (default: 3)
            base_retry_delay: Base delay in seconds for exponential backoff (default: 5)
            step_timeout: Timeout per step in seconds (default: 300)
        """
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        self.step_timeout = step_timeout
        self.logger = get_logger()
        self.plan_generator = get_plan_generator()
        self.risk_classifier = get_risk_classifier()
        self.approval_workflow = get_approval_workflow()

    def execute_step(
        self,
        step_id: str,
        step_function: Callable[[], Any],
        step_description: str,
        requires_risk_check: bool = False,
        action_type: Optional[str] = None,
        action_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute a single step with error handling and retry logic.

        Args:
            step_id: Step identifier (e.g., "step_1")
            step_function: Function to execute for this step
            step_description: Human-readable description
            requires_risk_check: Whether to check risk and request approval
            action_type: Type of action for risk assessment
            action_metadata: Metadata for risk assessment

        Returns:
            Tuple of (success, error_message)
        """
        start_time = time.time()

        # Update step status to in_progress
        self.plan_generator.update_step_status(
            step_id,
            'in_progress',
            f"Starting execution: {step_description}"
        )

        self.logger.info(
            component="reasoning",
            action="step_started",
            actor="step_executor",
            target=step_id,
            details={"description": step_description}
        )

        # Risk check if required
        if requires_risk_check and action_type:
            approval_needed, approval_id = self._check_risk_and_approval(
                step_id,
                action_type,
                step_description,
                action_metadata or {}
            )

            if approval_needed:
                # Wait for approval
                approved = self._wait_for_approval(step_id, approval_id)
                if not approved:
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.logger.warning(
                        component="reasoning",
                        action="step_blocked",
                        actor="step_executor",
                        target=step_id,
                        details={
                            "reason": "Approval rejected or timeout",
                            "duration_ms": duration_ms
                        }
                    )
                    self.plan_generator.update_step_status(
                        step_id,
                        'failed',
                        "Approval rejected or timeout - step not executed"
                    )
                    return False, "Approval rejected or timeout"

        # Execute step with retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                # Execute the step function
                result = step_function()

                # Success
                duration_ms = int((time.time() - start_time) * 1000)
                self.logger.info(
                    component="reasoning",
                    action="step_completed",
                    actor="step_executor",
                    target=step_id,
                    details={
                        "description": step_description,
                        "duration_ms": duration_ms,
                        "attempts": attempt
                    }
                )

                self.plan_generator.update_step_status(
                    step_id,
                    'completed',
                    f"Completed successfully (attempt {attempt}/{self.max_retries})"
                )

                return True, None

            except Exception as e:
                error_msg = str(e)
                duration_ms = int((time.time() - start_time) * 1000)

                if attempt < self.max_retries:
                    # Retry with exponential backoff
                    retry_delay = self.base_retry_delay * (3 ** (attempt - 1))

                    self.logger.warning(
                        component="reasoning",
                        action="step_retry",
                        actor="step_executor",
                        target=step_id,
                        details={
                            "error": error_msg,
                            "attempt": attempt,
                            "max_retries": self.max_retries,
                            "retry_delay": retry_delay,
                            "duration_ms": duration_ms
                        }
                    )

                    self.plan_generator.update_step_status(
                        step_id,
                        'in_progress',
                        f"Retry {attempt}/{self.max_retries} after error: {error_msg[:100]}"
                    )

                    time.sleep(retry_delay)
                else:
                    # Max retries exhausted
                    self.logger.error(
                        component="reasoning",
                        action="step_failed",
                        actor="step_executor",
                        target=step_id,
                        details={
                            "error": error_msg,
                            "attempts": attempt,
                            "duration_ms": duration_ms
                        }
                    )

                    self.plan_generator.update_step_status(
                        step_id,
                        'failed',
                        f"Failed after {attempt} attempts: {error_msg[:200]}"
                    )

                    return False, error_msg

        return False, "Unknown error"

    def _check_risk_and_approval(
        self,
        step_id: str,
        action_type: str,
        description: str,
        metadata: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check risk level and request approval if needed.

        Args:
            step_id: Step identifier
            action_type: Type of action
            description: Action description
            metadata: Action metadata

        Returns:
            Tuple of (approval_needed, approval_id)
        """
        # Classify risk
        risk_level, reason = self.risk_classifier.classify(
            action_type=action_type,
            content=description,
            metadata=metadata
        )

        self.logger.info(
            component="reasoning",
            action="risk_assessed",
            actor="step_executor",
            target=step_id,
            details={
                "action_type": action_type,
                "risk_level": risk_level,
                "reason": reason
            }
        )

        # Request approval if medium or high risk
        if risk_level in ['medium', 'high']:
            action_id = f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.approval_workflow.request_approval(
                action_id=action_id,
                action_type=action_type,
                description=description,
                risk_level=risk_level,
                action_data=metadata
            )

            self.plan_generator.update_step_status(
                step_id,
                'in_progress',
                f"Waiting for approval (risk: {risk_level})"
            )

            return True, action_id

        return False, None

    def _wait_for_approval(
        self,
        step_id: str,
        approval_id: str,
        poll_interval: int = 60,
        max_wait: int = 3600
    ) -> bool:
        """
        Wait for approval decision.

        Args:
            step_id: Step identifier
            approval_id: Approval request ID
            poll_interval: Seconds between status checks (default: 60)
            max_wait: Maximum wait time in seconds (default: 3600)

        Returns:
            True if approved, False if rejected or timeout
        """
        start_time = time.time()

        while (time.time() - start_time) < max_wait:
            status, _ = self.approval_workflow.check_approval_status(approval_id)

            if status == 'approved':
                self.logger.info(
                    component="reasoning",
                    action="approval_granted",
                    actor="step_executor",
                    target=step_id,
                    details={"approval_id": approval_id}
                )
                return True

            elif status in ['rejected', 'timeout']:
                self.logger.warning(
                    component="reasoning",
                    action="approval_denied",
                    actor="step_executor",
                    target=step_id,
                    details={"approval_id": approval_id, "status": status}
                )
                return False

            # Still pending, wait and check again
            time.sleep(poll_interval)

        # Max wait exceeded
        self.logger.warning(
            component="reasoning",
            action="approval_timeout",
            actor="step_executor",
            target=step_id,
            details={"approval_id": approval_id, "max_wait": max_wait}
        )
        return False

    def execute_plan(
        self,
        steps: list[Dict[str, Any]],
        event_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute all steps in a plan sequentially.

        Args:
            steps: List of step dictionaries with:
                   - id: Step identifier
                   - description: Step description
                   - function: Callable to execute
                   - requires_risk_check: Boolean (optional)
                   - action_type: String (optional)
                   - action_metadata: Dict (optional)
            event_id: Related event ID (optional)

        Returns:
            Tuple of (all_success, summary_dict)
        """
        start_time = time.time()
        total_steps = len(steps)
        completed = 0
        failed = 0
        failed_steps = []

        self.logger.info(
            component="reasoning",
            action="plan_execution_started",
            actor="step_executor",
            target=event_id or "manual",
            details={"total_steps": total_steps}
        )

        for step in steps:
            step_id = step['id']
            step_function = step['function']
            step_description = step['description']
            requires_risk_check = step.get('requires_risk_check', False)
            action_type = step.get('action_type')
            action_metadata = step.get('action_metadata', {})

            success, error = self.execute_step(
                step_id=step_id,
                step_function=step_function,
                step_description=step_description,
                requires_risk_check=requires_risk_check,
                action_type=action_type,
                action_metadata=action_metadata
            )

            if success:
                completed += 1
            else:
                failed += 1
                failed_steps.append({
                    'step_id': step_id,
                    'description': step_description,
                    'error': error
                })

                # Check if failure is blocking
                if step.get('blocking', True):
                    self.logger.error(
                        component="reasoning",
                        action="plan_execution_blocked",
                        actor="step_executor",
                        target=event_id or "manual",
                        details={
                            "blocking_step": step_id,
                            "error": error,
                            "completed": completed,
                            "failed": failed
                        }
                    )
                    break  # Stop execution on blocking failure

        # Calculate results
        duration_ms = int((time.time() - start_time) * 1000)
        all_success = (failed == 0)
        outcome = "success" if all_success else ("partial" if completed > 0 else "failed")

        summary = {
            'total_steps': total_steps,
            'completed': completed,
            'failed': failed,
            'failed_steps': failed_steps,
            'duration_ms': duration_ms,
            'outcome': outcome
        }

        self.logger.info(
            component="reasoning",
            action="plan_execution_completed",
            actor="step_executor",
            target=event_id or "manual",
            details=summary
        )

        # Mark plan as complete
        completion_notes = self._generate_completion_notes(summary)
        self.plan_generator.mark_plan_complete(outcome, completion_notes)

        return all_success, summary

    def _generate_completion_notes(self, summary: Dict[str, Any]) -> str:
        """Generate completion notes from execution summary."""
        notes = []

        notes.append(f"**Execution Summary**")
        notes.append(f"- Total Steps: {summary['total_steps']}")
        notes.append(f"- Completed: {summary['completed']}")
        notes.append(f"- Failed: {summary['failed']}")
        notes.append(f"- Duration: {summary['duration_ms']}ms")
        notes.append(f"- Outcome: {summary['outcome']}")

        if summary['failed_steps']:
            notes.append(f"\n**Failed Steps**:")
            for failed_step in summary['failed_steps']:
                notes.append(f"- {failed_step['step_id']}: {failed_step['error'][:100]}")

        return '\n'.join(notes)

    def create_escalation_task(
        self,
        step_id: str,
        description: str,
        error: str,
        event_id: Optional[str] = None
    ) -> Path:
        """
        Create escalation task for human review.

        Args:
            step_id: Failed step identifier
            description: Step description
            error: Error message
            event_id: Related event ID (optional)

        Returns:
            Path to created escalation task file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_file = Path(f'AI_Employee_Vault/Needs_Action/escalation_{timestamp}.md')

        content = f"""# ESCALATION: Step Failed After Retries

**Event ID**: {event_id or 'Unknown'}
**Step**: {step_id}
**Description**: {description}
**Failure**: {error}

## Action Required

1. Review error details below
2. Determine root cause
3. Take manual action if needed
4. Update Plan.md when resolved
5. Move this file to Done/ when complete

## Error Details

```
{error}
```

## Context

- Step ID: {step_id}
- Max retries: {self.max_retries}
- Created: {datetime.now().isoformat()}Z

## Next Steps

- [ ] Investigate root cause
- [ ] Take corrective action
- [ ] Update systems if needed
- [ ] Resume or cancel task
- [ ] Document resolution
"""

        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(content, encoding='utf-8')

        self.logger.warning(
            component="reasoning",
            action="escalation_created",
            actor="step_executor",
            target=step_id,
            details={
                "event_id": event_id,
                "error": error[:200],
                "task_file": str(task_file)
            }
        )

        return task_file


# Global instance
_step_executor = None


def get_step_executor() -> StepExecutor:
    """Get or create the global step executor instance."""
    global _step_executor
    if _step_executor is None:
        import os
        max_retries = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
        step_timeout = int(os.getenv('STEP_TIMEOUT_SECONDS', '300'))
        _step_executor = StepExecutor(
            max_retries=max_retries,
            step_timeout=step_timeout
        )
    return _step_executor
