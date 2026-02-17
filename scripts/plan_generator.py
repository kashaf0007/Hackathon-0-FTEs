"""
PlanGenerator class - Creates and updates structured execution plans.
Generates Plan.md with objectives, steps, and progress tracking.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from scripts.logger import get_logger
from scripts.file_utils import atomic_write


class PlanGenerator:
    """
    Generates and updates structured execution plans in Plan.md format.

    Plan structure:
    - Objective: What needs to be accomplished
    - Context: Background information and constraints
    - Proposed Actions: High-level action items
    - Risk Assessment: Risk level and approval requirements
    - Execution Steps: Detailed step-by-step breakdown
    - Progress Tracking: Status of each step
    """

    def __init__(self):
        """Initialize plan generator."""
        self.plan_file = Path('AI_Employee_Vault/Plan.md')
        self.logger = get_logger()

    def create_plan(
        self,
        objective: str,
        context: str,
        proposed_actions: List[str],
        risk_level: str,
        requires_approval: bool,
        steps: List[Dict[str, Any]],
        event_id: Optional[str] = None
    ) -> Path:
        """
        Create a new execution plan.

        Args:
            objective: What needs to be accomplished
            context: Background information
            proposed_actions: List of high-level actions
            risk_level: Risk level (low, medium, high)
            requires_approval: Whether approval is needed
            steps: List of execution steps with format:
                   [{"id": "step_1", "description": "...", "status": "pending"}]
            event_id: Related event ID (optional)

        Returns:
            Path to created plan file
        """
        created_at = datetime.now()

        # Count step statuses
        total_steps = len(steps)
        completed = sum(1 for s in steps if s.get('status') == 'completed')
        in_progress = sum(1 for s in steps if s.get('status') == 'in_progress')
        pending = sum(1 for s in steps if s.get('status') == 'pending')
        failed = sum(1 for s in steps if s.get('status') == 'failed')

        # Build plan content
        content = f"""# Current Execution Plan

**Status**: Active
**Created**: {created_at.isoformat()}Z
**Last Updated**: {created_at.isoformat()}Z
**Related Event**: {event_id or 'None'}

---

## Objective

{objective}

## Context

{context}

## Proposed Actions

{self._format_actions(proposed_actions)}

## Risk Assessment

- **Risk Level**: {risk_level}
- **Requires Approval**: {'Yes' if requires_approval else 'No'}

## Execution Steps

{self._format_steps(steps)}

## Progress Tracking

- **Total Steps**: {total_steps}
- **Completed**: {completed}
- **In Progress**: {in_progress}
- **Pending**: {pending}
- **Failed**: {failed}

## Notes

*Plan created and ready for execution*

---

**Last Updated**: {created_at.isoformat()}Z
"""

        # Write plan file
        atomic_write(str(self.plan_file), content)

        # Log plan creation
        self.logger.info(
            component="reasoning",
            action="plan_created",
            actor="plan_generator",
            target=event_id or "manual",
            details={
                "objective": objective[:100],  # Truncate for logging
                "risk_level": risk_level,
                "total_steps": total_steps,
                "requires_approval": requires_approval
            }
        )

        return self.plan_file

    def update_step_status(
        self,
        step_id: str,
        new_status: str,
        notes: Optional[str] = None
    ) -> None:
        """
        Update the status of a specific step in the plan.

        Args:
            step_id: Step identifier
            new_status: New status (pending, in_progress, completed, failed)
            notes: Optional notes about the status change
        """
        if not self.plan_file.exists():
            self.logger.warning(
                component="reasoning",
                action="plan_update_failed",
                actor="plan_generator",
                target=step_id,
                details={"reason": "Plan file does not exist"}
            )
            return

        # Read current plan
        with open(self.plan_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update step status in content
        # Find the step line and update its status marker
        lines = content.split('\n')
        updated_lines = []
        step_found = False

        for line in lines:
            if f"**{step_id}**" in line:
                step_found = True
                # Update status marker
                if new_status == 'completed':
                    line = line.replace('⏳', '✅').replace('🔄', '✅').replace('❌', '✅')
                elif new_status == 'in_progress':
                    line = line.replace('⏳', '🔄').replace('✅', '🔄').replace('❌', '🔄')
                elif new_status == 'failed':
                    line = line.replace('⏳', '❌').replace('🔄', '❌').replace('✅', '❌')
                elif new_status == 'pending':
                    line = line.replace('✅', '⏳').replace('🔄', '⏳').replace('❌', '⏳')

            updated_lines.append(line)

        if not step_found:
            self.logger.warning(
                component="reasoning",
                action="step_not_found",
                actor="plan_generator",
                target=step_id,
                details={"status": new_status}
            )
            return

        # Update progress tracking section
        updated_content = '\n'.join(updated_lines)
        updated_content = self._recalculate_progress(updated_content)

        # Update timestamp
        now = datetime.now().isoformat() + 'Z'
        updated_content = updated_content.replace(
            '**Last Updated**: ',
            f'**Last Updated**: {now}\n\n_Previous update: '
        )

        # Add notes if provided
        if notes:
            notes_section = f"\n\n### Step Update: {step_id}\n\n{notes}\n"
            # Insert before final separator
            updated_content = updated_content.replace(
                '\n---\n\n**Last Updated**:',
                notes_section + '\n---\n\n**Last Updated**:'
            )

        # Write updated plan
        atomic_write(str(self.plan_file), updated_content)

        # Log update
        self.logger.info(
            component="reasoning",
            action="step_updated",
            actor="plan_generator",
            target=step_id,
            details={"new_status": new_status, "notes": notes}
        )

    def _format_actions(self, actions: List[str]) -> str:
        """Format proposed actions as numbered list."""
        if not actions:
            return "*No actions defined*"
        return '\n'.join(f"{i+1}. {action}" for i, action in enumerate(actions))

    def _format_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Format execution steps with status indicators."""
        if not steps:
            return "*No steps defined*"

        formatted = []
        for step in steps:
            step_id = step.get('id', 'unknown')
            description = step.get('description', 'No description')
            status = step.get('status', 'pending')

            # Status emoji
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(status, '⏳')

            formatted.append(f"{status_emoji} **{step_id}**: {description}")

        return '\n'.join(formatted)

    def _recalculate_progress(self, content: str) -> str:
        """Recalculate progress tracking numbers based on step statuses."""
        # Count status emojis
        completed = content.count('✅')
        in_progress = content.count('🔄')
        failed = content.count('❌')
        pending = content.count('⏳')
        total = completed + in_progress + failed + pending

        # Update progress section
        lines = content.split('\n')
        updated_lines = []
        in_progress_section = False

        for line in lines:
            if '## Progress Tracking' in line:
                in_progress_section = True
            elif in_progress_section and line.startswith('##'):
                in_progress_section = False

            if in_progress_section:
                if '**Total Steps**:' in line:
                    line = f"- **Total Steps**: {total}"
                elif '**Completed**:' in line:
                    line = f"- **Completed**: {completed}"
                elif '**In Progress**:' in line:
                    line = f"- **In Progress**: {in_progress}"
                elif '**Pending**:' in line:
                    line = f"- **Pending**: {pending}"
                elif '**Failed**:' in line:
                    line = f"- **Failed**: {failed}"

            updated_lines.append(line)

        return '\n'.join(updated_lines)

    def mark_plan_complete(self, outcome: str, notes: Optional[str] = None) -> None:
        """
        Mark the current plan as complete.

        Args:
            outcome: Outcome description (success, partial, failed)
            notes: Optional completion notes
        """
        if not self.plan_file.exists():
            return

        with open(self.plan_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update status
        content = content.replace('**Status**: Active', f'**Status**: Completed ({outcome})')

        # Add completion notes
        if notes:
            completion_section = f"\n\n## Completion Notes\n\n{notes}\n"
            content = content.replace(
                '\n---\n\n**Last Updated**:',
                completion_section + '\n---\n\n**Last Updated**:'
            )

        # Update timestamp
        now = datetime.now().isoformat() + 'Z'
        content = content.replace(
            '**Last Updated**: ',
            f'**Last Updated**: {now}\n\n_Completed: '
        )

        atomic_write(str(self.plan_file), content)

        self.logger.info(
            component="reasoning",
            action="plan_completed",
            actor="plan_generator",
            target="current_plan",
            details={"outcome": outcome, "notes": notes}
        )


# Global instance
_plan_generator = None


def get_plan_generator() -> PlanGenerator:
    """Get or create the global plan generator instance."""
    global _plan_generator
    if _plan_generator is None:
        _plan_generator = PlanGenerator()
    return _plan_generator
