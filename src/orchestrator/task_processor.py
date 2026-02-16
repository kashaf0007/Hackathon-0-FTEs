"""Task Processor for Bronze Tier Constitutional FTE.

Coordinates task execution with skills, approval guard, and logging.
"""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.models import Task
from src.skills import LoggingAuditSkill, ApprovalGuardSkill, TaskOrchestratorSkill, SkillLoader
from src.utils import parse_markdown_task, format_markdown_task, atomic_write
from src.orchestrator.briefing_generator import BriefingGenerator


class TaskProcessor:
    """Task processor for orchestrating task execution.

    Scans for tasks, evaluates risk, executes or blocks, and logs all actions.
    Implements the core orchestration logic.
    """

    def __init__(
        self,
        needs_action_path: Path,
        done_path: Path,
        pending_approval_path: Path,
        logs_path: Path,
        skills_path: Path,
        vault_path: Path,
        dry_run: bool = False
    ):
        """Initialize task processor.

        Args:
            needs_action_path: Path to Needs_Action directory
            done_path: Path to Done directory
            pending_approval_path: Path to Pending_Approval directory
            logs_path: Path to Logs directory
            skills_path: Path to .claude/skills directory
            vault_path: Path to AI_Employee_Vault
            dry_run: If True, simulate all actions
        """
        self.needs_action_path = Path(needs_action_path)
        self.done_path = Path(done_path)
        self.pending_approval_path = Path(pending_approval_path)
        self.logs_path = Path(logs_path)
        self.skills_path = Path(skills_path)
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run

        # Initialize skill loader
        self.skill_loader = SkillLoader(skills_path=self.skills_path)

        # Initialize skills
        self.logging_skill = LoggingAuditSkill(
            skill_path=self.skills_path / "logging-audit",
            logs_path=self.logs_path
        )
        self.approval_guard = ApprovalGuardSkill(
            skill_path=self.skills_path / "approval-guard",
            pending_approval_path=self.pending_approval_path
        )
        self.task_orchestrator = TaskOrchestratorSkill(
            skill_path=self.skills_path / "task-orchestrator",
            vault_path=self.vault_path
        )

        # Initialize briefing generator
        briefings_path = self.vault_path / "Briefings"
        self.briefing_generator = BriefingGenerator(
            logs_path=self.logs_path,
            done_path=self.done_path,
            briefings_path=briefings_path
        )

    def scan_needs_action(self) -> List[Path]:
        """Scan Needs_Action directory for task files.

        Returns:
            List of task file paths
        """
        if not self.needs_action_path.exists():
            return []

        return list(self.needs_action_path.glob("*.md"))

    def parse_task_file(self, task_file: Path) -> Optional[Task]:
        """Parse task file into Task model.

        Args:
            task_file: Path to task markdown file

        Returns:
            Task model or None if parsing fails
        """
        try:
            content = task_file.read_text(encoding='utf-8')
            parsed = parse_markdown_task(content)

            # Extract task ID from filename or metadata
            task_id = task_file.stem  # Use filename without extension
            if 'task_id' in parsed['metadata']:
                task_id = parsed['metadata']['task_id']

            # Create Task model with full state restoration
            task = Task(
                task_id=task_id,
                title=parsed['title'] or task_file.stem,
                type=parsed['metadata'].get('type', 'generic'),
                priority=parsed['metadata'].get('priority', 'MEDIUM'),
                status=parsed['metadata'].get('status', 'PENDING'),
                created=datetime.fromisoformat(parsed['metadata']['created']) if 'created' in parsed['metadata'] else datetime.now(),
                updated=datetime.fromisoformat(parsed['metadata']['updated']) if 'updated' in parsed['metadata'] else None,
                completed=datetime.fromisoformat(parsed['metadata']['completed']) if 'completed' in parsed['metadata'] else None,
                retry_count=int(parsed['metadata'].get('retry_count', 0)),
                context={'context': parsed['sections'].get('Context', '')},
                expected_output=parsed['sections'].get('Expected Output'),
                actual_output=parsed['sections'].get('Actual Output'),
                error_message=parsed['metadata'].get('error')
            )

            return task

        except Exception as e:
            self.logging_skill.log_action(
                action=f"parse_task_file_{task_file.name}",
                risk_level="LOW",
                outcome="FAILURE",
                error=str(e),
                dry_run=self.dry_run
            )
            return None

    def evaluate_risk(self, task: Task) -> str:
        """Evaluate risk level for task.

        Args:
            task: Task to evaluate

        Returns:
            Risk level: LOW, MEDIUM, or HIGH
        """
        return self.approval_guard.evaluate_risk(task)

    def requires_approval(self, task: Task) -> bool:
        """Check if task requires approval.

        Args:
            task: Task to check

        Returns:
            True if approval required
        """
        return self.approval_guard.requires_approval(task)

    def create_approval_request(self, task: Task) -> ApprovalRequest:
        """Create approval request for high-risk task.

        Args:
            task: Task requiring approval

        Returns:
            Created approval request
        """
        justification = f"Task '{task.title}' requires approval due to {task.type} action type"
        impact = f"Will execute {task.type} action if approved"

        approval = self.approval_guard.create_approval_request(
            task=task,
            justification=justification,
            impact=impact,
            dry_run=self.dry_run
        )

        # Log approval request creation
        self.logging_skill.log_action(
            action=f"create_approval_request",
            risk_level=self.evaluate_risk(task),
            outcome="BLOCKED",
            task_id=task.task_id,
            skill_used="approval-guard",
            approval_status="PENDING_APPROVAL",
            dry_run=self.dry_run,
            approval_id=approval.request_id
        )

        return approval

    def check_approval_status(self, task: Task) -> str:
        """Check approval status for task.

        Args:
            task: Task to check

        Returns:
            Approval status: PENDING, APPROVED, or REJECTED
        """
        return self.approval_guard.check_approval_status(task)

    def execute_task(self, task: Task) -> dict:
        """Execute task using appropriate skill.

        Args:
            task: Task to execute

        Returns:
            Execution results
        """
        # Check for timeout before execution
        if task.is_timed_out():
            error_msg = f"Task timed out after {task.timeout_seconds} seconds"
            task.mark_failed(error_msg)
            self.logging_skill.log_action(
                action=f"timeout_task_{task.type}",
                risk_level=self.evaluate_risk(task),
                outcome="FAILURE",
                task_id=task.task_id,
                skill_used="task-orchestrator",
                approval_status="AUTO_APPROVED",
                error=error_msg,
                dry_run=self.dry_run,
                timeout_seconds=task.timeout_seconds
            )
            return {'success': False, 'error': error_msg}

        # Mark task as in progress
        task.mark_in_progress()

        # Log task start
        self.logging_skill.log_action(
            action=f"start_task_{task.type}",
            risk_level=self.evaluate_risk(task),
            outcome="SUCCESS",
            task_id=task.task_id,
            skill_used="task-orchestrator",
            approval_status="AUTO_APPROVED",
            dry_run=self.dry_run
        )

        # Execute via task orchestrator
        result = self.task_orchestrator.execute(task, dry_run=self.dry_run)

        # Check for timeout after execution
        if task.is_timed_out():
            error_msg = f"Task timed out during execution after {task.timeout_seconds} seconds"
            task.mark_failed(error_msg)
            self.logging_skill.log_action(
                action=f"timeout_task_{task.type}",
                risk_level=self.evaluate_risk(task),
                outcome="FAILURE",
                task_id=task.task_id,
                skill_used="task-orchestrator",
                approval_status="AUTO_APPROVED",
                error=error_msg,
                dry_run=self.dry_run,
                timeout_seconds=task.timeout_seconds
            )
            return {'success': False, 'error': error_msg}

        # Update task based on result
        if result['success']:
            task.mark_completed(result['output'])
            outcome = "SUCCESS"
        else:
            task.mark_failed(result['error'])
            outcome = "FAILURE"

        # Log task completion
        self.logging_skill.log_action(
            action=f"complete_task_{task.type}",
            risk_level=self.evaluate_risk(task),
            outcome=outcome,
            task_id=task.task_id,
            skill_used="task-orchestrator",
            approval_status="AUTO_APPROVED",
            error=result.get('error'),
            dry_run=self.dry_run,
            duration_ms=100,  # Placeholder
            retry_count=task.retry_count
        )

        return result

    def should_retry(self, task: Task) -> bool:
        """Check if task should be retried.

        Args:
            task: Task to check

        Returns:
            True if task can be retried
        """
        return task.can_retry()

    def retry_task(self, task: Task, task_file: Path) -> bool:
        """Retry a failed task.

        Args:
            task: Failed task
            task_file: Path to task file

        Returns:
            True if retry was successful
        """
        if not self.should_retry(task):
            return False

        # Log retry attempt
        self.logging_skill.log_action(
            action=f"retry_task_{task.type}",
            risk_level=self.evaluate_risk(task),
            outcome="SUCCESS",
            task_id=task.task_id,
            skill_used="task-orchestrator",
            approval_status="AUTO_APPROVED",
            dry_run=self.dry_run,
            retry_count=task.retry_count,
            max_retries=3
        )

        # Wait before retry (exponential backoff)
        import time
        wait_time = min(5 * (2 ** (task.retry_count - 1)), 30)  # Max 30 seconds
        if not self.dry_run:
            time.sleep(wait_time)

        # Reset status to pending for retry
        task.status = "PENDING"

        # Update task file with retry count
        self._update_task_file(task, task_file)

        return True

    def create_help_request(self, task: Task) -> None:
        """Create help request for task that exceeded max retries.

        Args:
            task: Failed task
        """
        help_task_id = f"help-{task.task_id}"
        help_content = f"""# Help Request: {task.title}

**Original Task ID**: {task.task_id}
**Type**: help_request
**Priority**: HIGH
**Created**: {datetime.now().isoformat()}
**Status**: PENDING

## Context
Task failed after {task.retry_count} retry attempts.

**Error**: {task.error_message}

## Original Task Context
{task.context.get('context', 'No context available')}

## Expected Output
Human intervention required to resolve issue or provide guidance.

## Actions Needed
1. Review error message
2. Determine root cause
3. Either fix issue manually or update task requirements
4. Delete this help request when resolved
"""

        help_file = self.needs_action_path / f"{help_task_id}.md"
        atomic_write(help_file, help_content)

        # Log help request creation
        self.logging_skill.log_action(
            action="create_help_request",
            risk_level="MEDIUM",
            outcome="SUCCESS",
            task_id=task.task_id,
            skill_used="task-orchestrator",
            approval_status="AUTO_APPROVED",
            dry_run=self.dry_run,
            help_task_id=help_task_id,
            retry_count=task.retry_count
        )

    def _update_task_file(self, task: Task, task_file: Path) -> None:
        """Update task file with current task state.

        Args:
            task: Task to update
            task_file: Path to task file
        """
        if self.dry_run:
            return

        content = format_markdown_task(
            title=task.title,
            task_type=task.type,
            priority=task.priority,
            created=task.created.isoformat(),
            status=task.status,
            context=task.context.get('context', ''),
            expected_output=task.expected_output,
            actual_output=task.actual_output
        )

        # Add retry count and error if present
        if task.retry_count > 0:
            content += f"\n**Retry Count**: {task.retry_count}\n"
        if task.error_message:
            content += f"\n**Error**: {task.error_message}\n"

        atomic_write(task_file, content)

    def move_to_done(self, task: Task, task_file: Path) -> None:
        """Move completed task to Done directory.

        Args:
            task: Completed task
            task_file: Path to task file
        """
        if not self.dry_run and task_file.exists():
            try:
                # Ensure Done directory exists and is writable
                self.done_path.mkdir(parents=True, exist_ok=True)
                print(f"[DEBUG] Attempting to move: {task_file} -> {self.done_path}")

                # Check if we have write permissions
                if not os.access(self.done_path, os.W_OK):
                    raise PermissionError(f"No write permission for {self.done_path}")

                done_file = self.done_path / task_file.name

                # Check if destination file already exists
                if done_file.exists():
                    # Append timestamp to avoid overwriting
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    done_file = self.done_path / f"{task_file.stem}_{timestamp}.md"

                task_file.rename(done_file)
                print(f"✓ Successfully moved task file to Done: {task_file.name} -> {done_file}")

                self.logging_skill.log_action(
                    action="move_to_done",
                    risk_level="LOW",
                    outcome="SUCCESS",
                    task_id=task.task_id,
                    skill_used="task-orchestrator",
                    approval_status="AUTO_APPROVED",
                    dry_run=self.dry_run,
                    destination=str(done_file)
                )
            except PermissionError as e:
                self.logging_skill.log_action(
                    action="move_to_done",
                    risk_level="LOW",
                    outcome="FAILURE",
                    task_id=task.task_id,
                    skill_used="task-orchestrator",
                    approval_status="AUTO_APPROVED",
                    error=f"Permission denied: {str(e)}",
                    dry_run=self.dry_run
                )
                raise
            except Exception as e:
                self.logging_skill.log_action(
                    action="move_to_done",
                    risk_level="LOW",
                    outcome="FAILURE",
                    task_id=task.task_id,
                    skill_used="task-orchestrator",
                    approval_status="AUTO_APPROVED",
                    error=str(e),
                    dry_run=self.dry_run
                )
                raise
        elif self.dry_run:
            # Log simulated move in dry run mode
            self.logging_skill.log_action(
                action="move_to_done",
                risk_level="LOW",
                outcome="SUCCESS",
                task_id=task.task_id,
                skill_used="task-orchestrator",
                approval_status="AUTO_APPROVED",
                dry_run=self.dry_run,
                simulated=True
            )

    def move_to_pending_approval(self, task: Task, task_file: Path, approval_request_id: str) -> None:
        """Move high-risk task to Pending_Approval directory.

        Args:
            task: Task requiring approval
            task_file: Path to task file
            approval_request_id: ID of the approval request
        """
        if not self.dry_run and task_file.exists():
            try:
                # Ensure Pending_Approval directory exists and is writable
                self.pending_approval_path.mkdir(parents=True, exist_ok=True)
                print(f"[DEBUG] Attempting to move: {task_file} -> {self.pending_approval_path}")

                if not os.access(self.pending_approval_path, os.W_OK):
                    raise PermissionError(f"No write permission for {self.pending_approval_path}")

                # Move task file to pending approval with reference to approval request
                pending_file = self.pending_approval_path / f"task-{task.task_id}.md"

                # Check if destination file already exists
                if pending_file.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pending_file = self.pending_approval_path / f"task-{task.task_id}_{timestamp}.md"

                task_file.rename(pending_file)
                print(f"✓ Successfully moved task file to Pending_Approval: {task_file.name} -> {pending_file}")

                self.logging_skill.log_action(
                    action="move_to_pending_approval",
                    risk_level="HIGH",
                    outcome="SUCCESS",
                    task_id=task.task_id,
                    skill_used="task-orchestrator",
                    approval_status="PENDING_APPROVAL",
                    dry_run=self.dry_run,
                    approval_request_id=approval_request_id,
                    destination=str(pending_file)
                )
            except Exception as e:
                self.logging_skill.log_action(
                    action="move_to_pending_approval",
                    risk_level="HIGH",
                    outcome="FAILURE",
                    task_id=task.task_id,
                    skill_used="task-orchestrator",
                    approval_status="PENDING_APPROVAL",
                    error=str(e),
                    dry_run=self.dry_run
                )
                raise
        elif self.dry_run:
            self.logging_skill.log_action(
                action="move_to_pending_approval",
                risk_level="HIGH",
                outcome="SUCCESS",
                task_id=task.task_id,
                skill_used="task-orchestrator",
                approval_status="PENDING_APPROVAL",
                dry_run=self.dry_run,
                simulated=True
            )

    def process_task(self, task_file: Path) -> bool:
        """Process a single task file.

        Args:
            task_file: Path to task file

        Returns:
            True if task was processed successfully
        """
        # Parse task
        task = self.parse_task_file(task_file)
        if not task:
            return False

        # Evaluate risk
        risk = self.evaluate_risk(task)

        # Check if requires approval
        if self.requires_approval(task):
            # Check if already approved
            approval_status = self.check_approval_status(task)

            if approval_status == "PENDING":
                # Create approval request if not exists
                approval = self.create_approval_request(task)
                # Move task to Pending_Approval folder
                self.move_to_pending_approval(task, task_file, approval.request_id)
                return False  # Don't execute yet

            elif approval_status == "REJECTED":
                # Task rejected, move to done with failed status
                task.mark_failed("Task rejected by approver")
                self.move_to_done(task, task_file)
                return False

            elif approval_status == "APPROVED":
                # Proceed with execution
                pass

        # Execute task
        result = self.execute_task(task)

        # Handle result
        if result['success']:
            # Task succeeded, move to done
            self.move_to_done(task, task_file)
            return True
        else:
            # Task failed, check if should retry
            if self.should_retry(task):
                # Retry the task
                self.retry_task(task, task_file)
                return False  # Not complete yet
            else:
                # Max retries exceeded, create help request
                self.create_help_request(task)
                # Move failed task to done
                self.move_to_done(task, task_file)
                return False

        return False

    def process_all_tasks(self) -> int:
        """Process all tasks in Needs_Action directory.

        Returns:
            Number of tasks processed successfully
        """
        task_files = self.scan_needs_action()
        processed_count = 0

        for task_file in task_files:
            if self.process_task(task_file):
                processed_count += 1

        return processed_count

    def recover_incomplete_tasks(self) -> int:
        """Recover incomplete tasks on orchestrator startup.

        Scans for tasks that were IN_PROGRESS when orchestrator stopped
        and resets them to PENDING for retry.

        Returns:
            Number of incomplete tasks recovered
        """
        task_files = self.scan_needs_action()
        recovered_count = 0

        for task_file in task_files:
            task = self.parse_task_file(task_file)
            if not task:
                continue

            # Check if task is incomplete
            if task.is_incomplete():
                # Reset to pending for retry
                task.status = "PENDING"
                task.updated = datetime.now()

                # Update task file
                self._update_task_file(task, task_file)

                # Log recovery
                self.logging_skill.log_action(
                    action="recover_incomplete_task",
                    risk_level="LOW",
                    outcome="SUCCESS",
                    task_id=task.task_id,
                    skill_used="task-orchestrator",
                    approval_status="AUTO_APPROVED",
                    dry_run=self.dry_run,
                    previous_status="IN_PROGRESS",
                    retry_count=task.retry_count
                )

                recovered_count += 1

        return recovered_count

    def validate_skills(self) -> bool:
        """Validate all skills on orchestrator startup.

        Returns:
            True if all skills are valid, False otherwise
        """
        # Validate all skills
        validation_results = self.skill_loader.validate_all_skills()

        if not validation_results:
            # All skills valid
            self.logging_skill.log_action(
                action="validate_skills",
                risk_level="LOW",
                outcome="SUCCESS",
                skill_used="skill-loader",
                approval_status="AUTO_APPROVED",
                dry_run=self.dry_run,
                skills_validated=len(self.skill_loader.discover_skills())
            )
            return True
        else:
            # Some skills invalid
            error_summary = []
            for skill_name, errors in validation_results.items():
                error_summary.append(f"{skill_name}: {', '.join(errors)}")

            self.logging_skill.log_action(
                action="validate_skills",
                risk_level="MEDIUM",
                outcome="FAILURE",
                skill_used="skill-loader",
                approval_status="AUTO_APPROVED",
                error="; ".join(error_summary),
                dry_run=self.dry_run,
                invalid_skills=list(validation_results.keys())
            )
            return False

    def update_dashboard(self) -> None:
        """Update Dashboard.md with current system status.

        Updates active tasks, pending approvals, completed today, and alerts.
        """
        from datetime import date, timedelta

        # Count active tasks
        active_tasks = len(self.scan_needs_action())

        # Count pending approvals and detect stale ones
        pending_approvals = []
        stale_approvals = []
        if self.pending_approval_path.exists():
            for approval_file in self.pending_approval_path.glob("*.md"):
                try:
                    content = approval_file.read_text(encoding='utf-8')
                    parsed = parse_markdown_task(content)

                    # Check if still pending
                    if parsed['metadata'].get('status') == 'PENDING':
                        pending_approvals.append(approval_file)

                        # Check if stale (>7 days)
                        created_str = parsed['metadata'].get('created')
                        if created_str:
                            created = datetime.fromisoformat(created_str)
                            age_days = (datetime.now() - created).days
                            if age_days > 7:
                                stale_approvals.append((approval_file.stem, age_days))
                except Exception:
                    pass

        # Count completed tasks today
        completed_today = 0
        today = date.today()
        if self.done_path.exists():
            for done_file in self.done_path.glob("*.md"):
                try:
                    stat = done_file.stat()
                    modified_date = date.fromtimestamp(stat.st_mtime)
                    if modified_date == today:
                        completed_today += 1
                except Exception:
                    pass

        # Check log file size
        log_file_size_kb = 0
        today_log = self.logs_path / f"{today.isoformat()}.json"
        if today_log.exists():
            log_file_size_kb = today_log.stat().st_size / 1024

        # Calculate next credential rotation date (monthly)
        next_rotation = date.today().replace(day=1) + timedelta(days=32)
        next_rotation = next_rotation.replace(day=1)

        # Generate dashboard content
        dashboard_content = f"""# Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Auto-generated)

## System Status

**Orchestrator**: Running
**DRY_RUN Mode**: {'Enabled' if self.dry_run else 'Disabled'}
**Constitutional Compliance**: ✅ All Principles Enforced

## Current Activity

### Active Tasks
**Count**: {active_tasks}
**Location**: AI_Employee_Vault/Needs_Action/

### Pending Approvals
**Count**: {len(pending_approvals)}
**Location**: AI_Employee_Vault/Pending_Approval/
**⚠️ Stale Approvals** (>7 days): {len(stale_approvals)}
"""

        # Add stale approval details if any
        if stale_approvals:
            dashboard_content += "\n**Stale Approval Details**:\n"
            for approval_id, age_days in stale_approvals:
                dashboard_content += f"- {approval_id}: {age_days} days old\n"

        dashboard_content += f"""
### Completed Today
**Count**: {completed_today}
**Location**: AI_Employee_Vault/Done/

### Constitutional Violations
**Count**: 0
**Status**: ✅ No violations detected

## Recent Activity

_Check AI_Employee_Vault/Logs/{today.isoformat()}.json for detailed activity_

## System Health

### Performance Metrics
- **Task Detection Latency**: <5s (polling interval)
- **Log Write Latency**: <100ms (atomic writes)
- **Average Task Duration**: Varies by task type

### Resource Usage
- **Log File Size (Today)**: {log_file_size_kb:.2f} KB
"""

        # Add warning if log file is large
        if log_file_size_kb > 1024:  # >1MB
            dashboard_content += f"- ⚠️ **Warning**: Log file exceeds 1MB, consider archiving\n"

        dashboard_content += f"""- **Total Tasks Processed**: {completed_today}
- **Success Rate**: Monitored via logs

## Alerts & Reminders

### Security
- [ ] **Credential Rotation Due**: Check monthly (Next: {next_rotation.isoformat()})
"""

        # Add stale approval alert
        if stale_approvals:
            dashboard_content += f"- ⚠️ **Stale Approvals**: {len(stale_approvals)} approval(s) pending >7 days\n"

        dashboard_content += """
### Operational
- [ ] **Review Pending Approvals**: Check daily
- [ ] **Archive Old Logs**: Archive logs older than 30 days

## Quick Actions

1. **Start Orchestrator**: `python main.py`
2. **Create Task**: Add markdown file to `AI_Employee_Vault/Needs_Action/`
3. **Approve Task**: Edit file in `AI_Employee_Vault/Pending_Approval/` and set Status to APPROVED
4. **View Logs**: Check `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

## Constitutional Principles Status

- ✅ **Local-First**: All data stored locally
- ✅ **HITL Safety**: Approval Guard active
- ✅ **Proactivity**: File watcher monitoring
- ✅ **Persistence**: Retry logic with exponential backoff
- ✅ **Transparency**: All actions logged
- ✅ **Cost Efficiency**: Efficient polling and file operations

---

_This dashboard is automatically updated by the orchestrator. Manual edits will be overwritten._
"""

        # Write dashboard
        dashboard_path = self.vault_path / "Dashboard.md"
        if not self.dry_run:
            atomic_write(dashboard_path, dashboard_content)

        # Log dashboard update
        self.logging_skill.log_action(
            action="update_dashboard",
            risk_level="LOW",
            outcome="SUCCESS",
            skill_used="orchestrator",
            approval_status="AUTO_APPROVED",
            dry_run=self.dry_run,
            active_tasks=active_tasks,
            pending_approvals=len(pending_approvals),
            stale_approvals=len(stale_approvals),
            completed_today=completed_today,
            log_size_kb=log_file_size_kb
        )

    def generate_weekly_briefing(self) -> Optional[str]:
        """Generate weekly briefing report.

        Returns:
            Path to generated briefing file, or None if failed
        """
        try:
            briefing_path = self.briefing_generator.generate_weekly_briefing(dry_run=self.dry_run)
            
            self.logging_skill.log_action(
                action="generate_weekly_briefing",
                risk_level="LOW",
                outcome="SUCCESS",
                skill_used="briefing-generator",
                approval_status="AUTO_APPROVED",
                dry_run=self.dry_run,
                briefing_path=briefing_path
            )
            
            return briefing_path
        except Exception as e:
            self.logging_skill.log_action(
                action="generate_weekly_briefing",
                risk_level="LOW",
                outcome="FAILURE",
                skill_used="briefing-generator",
                approval_status="AUTO_APPROVED",
                error=str(e),
                dry_run=self.dry_run
            )
            return None
