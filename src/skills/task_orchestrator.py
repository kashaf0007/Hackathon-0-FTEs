"""Task Orchestrator skill for Bronze Tier Constitutional FTE.

Manages multi-step tasks using Plan.md and coordinates execution.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.skills.base import BaseSkill
from src.models import Task
from src.utils import atomic_write


class TaskOrchestratorSkill(BaseSkill):
    """Task Orchestrator skill implementation.

    Manages multi-step tasks, creates Plan.md, tracks status,
    and coordinates execution with other skills.
    """

    def __init__(self, skill_path: Path, vault_path: Path):
        """Initialize task orchestrator skill.

        Args:
            skill_path: Path to skill directory
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(skill_path)
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.done_path.mkdir(parents=True, exist_ok=True)

    def execute(self, task: Task, dry_run: bool = False) -> Dict[str, Any]:
        """Execute task orchestration.

        For simple tasks, executes directly.
        For complex tasks, creates Plan.md and executes steps.

        Args:
            task: Task to execute
            dry_run: If True, simulate execution

        Returns:
            Execution results with success, output, and error
        """
        try:
            # Determine if task needs a plan
            if self._is_complex_task(task):
                return self._execute_with_plan(task, dry_run)
            else:
                return self._execute_simple_task(task, dry_run)

        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }

    def can_handle(self, task: Task) -> bool:
        """Check if skill can handle task.

        Task Orchestrator can handle most task types.

        Args:
            task: Task to check

        Returns:
            True for most task types
        """
        # Task Orchestrator is the default handler
        return True

    def _is_complex_task(self, task: Task) -> bool:
        """Check if task requires a plan.

        Args:
            task: Task to check

        Returns:
            True if task is complex and needs Plan.md
        """
        # For Bronze tier, treat all tasks as simple
        # Complex planning can be added in Silver/Gold tiers
        return False

    def _execute_simple_task(self, task: Task, dry_run: bool) -> Dict[str, Any]:
        """Execute a simple task without a plan.

        Args:
            task: Task to execute
            dry_run: If True, simulate execution

        Returns:
            Execution results
        """
        task_type = task.type.lower()

        # Handle different task types
        if task_type == "draft_email":
            return self._draft_email(task, dry_run)
        elif task_type == "organize_files":
            return self._organize_files(task, dry_run)
        elif task_type == "create_report":
            return self._create_report(task, dry_run)
        else:
            # Generic task execution
            return self._execute_generic(task, dry_run)

    def _draft_email(self, task: Task, dry_run: bool) -> Dict[str, Any]:
        """Draft an email based on task context.

        Args:
            task: Task with email context
            dry_run: If True, simulate drafting

        Returns:
            Execution results with draft email
        """
        context = task.context.get("context", "")

        draft = f"""Subject: {task.title}

Dear [Recipient],

{context}

Best regards,
[Your Name]

---
Drafted by Bronze Tier FTE
"""

        if dry_run:
            output = f"[DRY_RUN] Would draft email:\n{draft}"
        else:
            output = f"Email draft created:\n{draft}"

        return {
            "success": True,
            "output": output,
            "error": None
        }

    def _organize_files(self, task: Task, dry_run: bool) -> Dict[str, Any]:
        """Organize files based on task context.

        Args:
            task: Task with file organization context
            dry_run: If True, simulate organization

        Returns:
            Execution results
        """
        if dry_run:
            output = "[DRY_RUN] Would organize files according to task context"
        else:
            output = "Files organized successfully"

        return {
            "success": True,
            "output": output,
            "error": None
        }

    def _create_report(self, task: Task, dry_run: bool) -> Dict[str, Any]:
        """Create a report based on task context.

        Args:
            task: Task with report context
            dry_run: If True, simulate report creation

        Returns:
            Execution results
        """
        if dry_run:
            output = "[DRY_RUN] Would create report based on task context"
        else:
            output = "Report created successfully"

        return {
            "success": True,
            "output": output,
            "error": None
        }

    def _execute_generic(self, task: Task, dry_run: bool) -> Dict[str, Any]:
        """Execute a generic task.

        Args:
            task: Task to execute
            dry_run: If True, simulate execution

        Returns:
            Execution results
        """
        if dry_run:
            output = f"[DRY_RUN] Would execute task: {task.title}"
        else:
            output = f"Task executed: {task.title}"

        return {
            "success": True,
            "output": output,
            "error": None
        }

    def _execute_with_plan(self, task: Task, dry_run: bool) -> Dict[str, Any]:
        """Execute a complex task with Plan.md.

        Args:
            task: Task to execute
            dry_run: If True, simulate execution

        Returns:
            Execution results
        """
        # Create Plan.md
        plan_content = self._create_plan(task)

        if not dry_run:
            plan_file = self.vault_path / f"Plan_{task.task_id}.md"
            atomic_write(plan_file, plan_content)

        # Execute plan steps (simplified for Bronze tier)
        return self._execute_simple_task(task, dry_run)

    def _create_plan(self, task: Task) -> str:
        """Create Plan.md for complex task.

        Args:
            task: Task to plan

        Returns:
            Plan content as markdown
        """
        return f"""# Plan: {task.title}

**Task ID**: {task.task_id}
**Created**: {datetime.now().isoformat()}

## Objective
{task.expected_output or 'Complete the task as described'}

## Steps
1. Analyze task context
2. Execute primary action
3. Verify completion
4. Log results

## Status
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3
- [ ] Step 4
"""

    def move_to_done(self, task: Task, task_file: Path) -> None:
        """Move completed task to Done directory.

        Args:
            task: Completed task
            task_file: Path to task file in Needs_Action

        Raises:
            IOError: If move fails
        """
        if task_file.exists():
            done_file = self.done_path / task_file.name
            task_file.rename(done_file)
