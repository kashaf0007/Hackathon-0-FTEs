"""
Orchestrator - Main coordination loop for AI Employee system.
Coordinates watchers, reasoning loop, and scheduled tasks.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Fix Windows encoding for emoji support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from scripts.logger import get_logger
from scripts.event_queue import get_event_queue
from scripts.task_analyzer import get_task_analyzer
from scripts.plan_generator import get_plan_generator
from scripts.step_executor import get_step_executor
from scripts.run_watchers import run_all_watchers, load_config
from scripts.approval_workflow import get_approval_workflow
from scripts.risk_classifier import get_risk_classifier


class Orchestrator:
    """
    Main orchestration loop for AI Employee system.

    Responsibilities:
    - Coordinate watcher execution
    - Process event queue
    - Execute reasoning loop
    - Handle scheduled tasks
    - Monitor system health
    - Recover from failures
    """

    def __init__(self, dry_run: bool = None):
        """
        Initialize orchestrator.

        Args:
            dry_run: If True, simulate operations without real execution
        """
        self.dry_run = dry_run if dry_run is not None else (
            os.getenv('DRY_RUN', 'true').lower() == 'true'
        )
        self.logger = get_logger()
        self.event_queue = get_event_queue()
        self.task_analyzer = get_task_analyzer()
        self.plan_generator = get_plan_generator()
        self.step_executor = get_step_executor()
        self.approval_workflow = get_approval_workflow()
        self.risk_classifier = get_risk_classifier()
        self.running = False

    def start(self) -> None:
        """Start the orchestrator."""
        self.running = True

        self.logger.info(
            component="orchestrator",
            action="orchestrator_started",
            actor="orchestrator",
            target="system",
            details={
                'dry_run': self.dry_run,
                'timestamp': datetime.now().isoformat() + 'Z'
            }
        )

        print(f"🚀 AI Employee Orchestrator Started")
        print(f"   DRY_RUN: {self.dry_run}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def stop(self) -> None:
        """Stop the orchestrator."""
        self.running = False

        self.logger.info(
            component="orchestrator",
            action="orchestrator_stopped",
            actor="orchestrator",
            target="system",
            details={'timestamp': datetime.now().isoformat() + 'Z'}
        )

        print("\n🛑 AI Employee Orchestrator Stopped")

    def run_cycle(self) -> Dict[str, Any]:
        """
        Run one orchestration cycle.

        Returns:
            Cycle results dictionary
        """
        cycle_start = time.time()

        self.logger.info(
            component="orchestrator",
            action="cycle_started",
            actor="orchestrator",
            target="system",
            details={'timestamp': datetime.now().isoformat() + 'Z'}
        )

        results = {
            'watchers_run': False,
            'events_processed': 0,
            'plans_created': 0,
            'tasks_completed': 0,
            'errors': []
        }

        try:
            # Step 1: Run watchers to detect new events
            print("📡 Running watchers...")
            watcher_results = self._run_watchers()
            results['watchers_run'] = True
            print(f"   Found {watcher_results.get('events_detected', 0)} new events")

            # Step 2: Process event queue
            print("📋 Processing event queue...")
            events_processed = self._process_event_queue()
            results['events_processed'] = events_processed
            print(f"   Processed {events_processed} events")

            # Step 3: Execute scheduled tasks
            print("⏰ Checking scheduled tasks...")
            scheduled_results = self._execute_scheduled_tasks()
            results['tasks_completed'] = scheduled_results.get('completed', 0)
            print(f"   Completed {scheduled_results.get('completed', 0)} scheduled tasks")

        except Exception as e:
            error_msg = f"Cycle error: {str(e)}"
            results['errors'].append(error_msg)

            self.logger.error(
                component="orchestrator",
                action="cycle_failed",
                actor="orchestrator",
                target="system",
                details={'error': str(e)}
            )

            print(f"   ❌ Error: {str(e)}")

        # Calculate cycle duration
        cycle_duration = time.time() - cycle_start
        results['duration_seconds'] = cycle_duration

        self.logger.info(
            component="orchestrator",
            action="cycle_completed",
            actor="orchestrator",
            target="system",
            details=results
        )

        print(f"✅ Cycle completed in {cycle_duration:.2f}s")
        print()

        return results

    def _run_watchers(self) -> Dict[str, Any]:
        """
        Run all enabled watchers.

        Returns:
            Watcher execution results
        """
        try:
            config = load_config()
            run_all_watchers(config, test_mode=False)

            return {
                'status': 'success',
                'events_detected': len(list(Path('AI_Employee_Vault/Needs_Action').glob('*.json')))
            }

        except Exception as e:
            self.logger.error(
                component="orchestrator",
                action="watchers_failed",
                actor="orchestrator",
                target="watchers",
                details={'error': str(e)}
            )
            return {
                'status': 'failed',
                'error': str(e),
                'events_detected': 0
            }

    def _process_event_queue(self) -> int:
        """
        Process events from the queue.

        Returns:
            Number of events processed
        """
        processed = 0
        max_events_per_cycle = 10  # Limit to prevent overload

        while processed < max_events_per_cycle:
            # Get next event
            result = self.event_queue.pop()
            if not result:
                break

            event, event_file = result

            try:
                # Analyze event
                analysis = self.task_analyzer.analyze_event(event)

                # Determine if plan is needed
                if analysis['requires_plan']:
                    # Create and execute plan
                    self._execute_with_plan(event, analysis)
                else:
                    # Simple execution without plan
                    self._execute_simple(event, analysis)

                processed += 1

            except Exception as e:
                self.logger.error(
                    component="orchestrator",
                    action="event_processing_failed",
                    actor="orchestrator",
                    target=event.get('id', 'unknown'),
                    details={'error': str(e)}
                )

                # Move to Done with error status
                self.event_queue.move_to_done(event_file)

        return processed

    def _execute_with_plan(self, event: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """
        Execute event with structured plan using reasoning-loop skill.

        Args:
            event: Event dictionary
            analysis: Task analysis results
        """
        event_id = event.get('id')

        # Log routing decision (task-orchestrator skill logic)
        self.logger.info(
            component="orchestrator",
            action="event_routed",
            actor="task-orchestrator",
            target=event_id,
            details={
                'routed_to': 'reasoning-loop',
                'reason': 'Complex task requires structured plan',
                'complexity': analysis['complexity'],
                'category': analysis['category']
            }
        )

        # Generate plan (reasoning-loop skill)
        plan_file = self.plan_generator.create_plan(
            objective=f"Handle {analysis['category']} event from {event['source']}",
            context=event.get('content', ''),
            proposed_actions=analysis['suggested_actions'],
            risk_level=analysis.get('risk_level', 'medium'),
            requires_approval=analysis.get('requires_approval', False),
            steps=[
                {'id': f'step_{i+1}', 'description': action, 'status': 'pending'}
                for i, action in enumerate(analysis['suggested_actions'])
            ],
            event_id=event_id
        )

        self.logger.info(
            component="reasoning",
            action="plan_created",
            actor="reasoning-loop",
            target=event_id,
            details={'plan_file': str(plan_file), 'steps': len(analysis['suggested_actions'])}
        )

        # Execute plan steps (reasoning-loop skill with step_executor)
        try:
            steps = [
                {
                    'id': f'step_{i+1}',
                    'description': action,
                    'function': lambda: self._execute_step_action(action, event, analysis),
                    'requires_risk_check': True,
                    'action_type': self._determine_action_type(action),
                    'action_metadata': {'event_id': event_id, 'category': analysis['category']}
                }
                for i, action in enumerate(analysis['suggested_actions'])
            ]

            success, summary = self.step_executor.execute_plan(steps, event_id)

            if success:
                # Mark plan complete
                self.plan_generator.mark_plan_complete(
                    outcome='success',
                    notes=summary
                )

                # Move event to Done
                event_file = Path(f"AI_Employee_Vault/Needs_Action/{event_id}.json")
                if event_file.exists():
                    self.event_queue.move_to_done(event_file, status='completed')

                self.logger.info(
                    component="orchestrator",
                    action="task_completed",
                    actor="task-orchestrator",
                    target=event_id,
                    details={'outcome': 'success', 'summary': summary}
                )
            else:
                # Mark plan failed
                self.plan_generator.mark_plan_complete(
                    outcome='failed',
                    notes=summary
                )

                self.logger.error(
                    component="orchestrator",
                    action="task_failed",
                    actor="task-orchestrator",
                    target=event_id,
                    details={'outcome': 'failed', 'summary': summary}
                )

        except Exception as e:
            self.logger.error(
                component="orchestrator",
                action="plan_execution_failed",
                actor="reasoning-loop",
                target=event_id,
                details={'error': str(e)}
            )
            raise

    def _execute_simple(self, event: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """
        Execute simple event without plan (routes through appropriate skill).

        Args:
            event: Event dictionary
            analysis: Task analysis results
        """
        event_id = event.get('id')

        # Determine which skill to route to based on event type
        skill = self._route_to_skill(event, analysis)

        self.logger.info(
            component="orchestrator",
            action="event_routed",
            actor="task-orchestrator",
            target=event_id,
            details={
                'routed_to': skill,
                'reason': 'Simple task, direct skill execution',
                'complexity': analysis['complexity'],
                'category': analysis['category']
            }
        )

        # Check if approval is needed (approval-guard skill)
        if analysis.get('requires_approval', False):
            risk_level, reason = self.risk_classifier.classify_risk(
                action_type=self._determine_action_type(analysis['suggested_actions'][0]),
                content=event.get('content', ''),
                metadata=event.get('metadata', {})
            )

            if risk_level in ['medium', 'high']:
                # Request approval
                action_id = f"{event['source']}_{event_id}"
                self.approval_workflow.request_approval(
                    action_id=action_id,
                    action_type=self._determine_action_type(analysis['suggested_actions'][0]),
                    description=f"Execute {analysis['category']} action",
                    risk_level=risk_level,
                    action_data={
                        'event': event,
                        'analysis': analysis
                    }
                )

                self.logger.info(
                    component="approval",
                    action="approval_requested",
                    actor="approval-guard",
                    target=event_id,
                    details={'risk_level': risk_level, 'reason': reason}
                )

                # Don't move to Done yet - wait for approval
                return

        # Execute action through appropriate skill
        try:
            self._execute_step_action(analysis['suggested_actions'][0], event, analysis)

            # Move to Done
            event_file = Path(f"AI_Employee_Vault/Needs_Action/{event_id}.json")
            if event_file.exists():
                self.event_queue.move_to_done(event_file, status='completed')

            self.logger.info(
                component="orchestrator",
                action="task_completed",
                actor="task-orchestrator",
                target=event_id,
                details={'skill': skill, 'outcome': 'success'}
            )

        except Exception as e:
            self.logger.error(
                component="orchestrator",
                action="task_failed",
                actor="task-orchestrator",
                target=event_id,
                details={'skill': skill, 'error': str(e)}
            )
            raise

    def _route_to_skill(self, event: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Determine which skill to route event to (task-orchestrator logic).

        Args:
            event: Event dictionary
            analysis: Task analysis results

        Returns:
            Skill name
        """
        source = event.get('source', '')
        category = analysis.get('category', '')

        # Routing rules (from task-orchestrator skill)
        if 'email' in source.lower():
            if category == 'sales':
                return 'reasoning-loop'  # Complex sales inquiry
            else:
                return 'email-mcp-sender'  # Simple email response

        elif 'linkedin' in source.lower():
            if event.get('type') == 'scheduled_post':
                return 'linkedin-post-generator'
            else:
                return 'reasoning-loop'  # Connection requests, messages

        elif source == 'scheduler':
            if 'linkedin' in event.get('type', '').lower():
                return 'linkedin-post-generator'
            else:
                return 'reasoning-loop'

        # Default to reasoning loop for unknown types
        return 'reasoning-loop'

    def _determine_action_type(self, action_description: str) -> str:
        """
        Determine action type from description.

        Args:
            action_description: Action description string

        Returns:
            Action type (email_send, linkedin_post, etc.)
        """
        action_lower = action_description.lower()

        if 'email' in action_lower or 'send' in action_lower:
            return 'email_send'
        elif 'linkedin' in action_lower or 'post' in action_lower:
            return 'linkedin_post'
        elif 'payment' in action_lower or 'pay' in action_lower:
            return 'payment'
        elif 'delete' in action_lower or 'remove' in action_lower:
            return 'file_delete'
        else:
            return 'other'

    def _execute_step_action(self, action: str, event: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """
        Execute a single step action.

        Args:
            action: Action description
            event: Event dictionary
            analysis: Task analysis results
        """
        # This is a placeholder for actual skill execution
        # In production, this would invoke the appropriate MCP server or skill

        if self.dry_run:
            self.logger.info(
                component="orchestrator",
                action="step_simulated",
                actor="orchestrator",
                target=event.get('id'),
                details={'action': action, 'dry_run': True}
            )
        else:
            # Would invoke actual skill/MCP here
            self.logger.info(
                component="orchestrator",
                action="step_executed",
                actor="orchestrator",
                target=event.get('id'),
                details={'action': action}
            )

    def _execute_scheduled_tasks(self) -> Dict[str, Any]:
        """
        Execute scheduled tasks (LinkedIn posts, reports, etc.).

        Returns:
            Execution results
        """
        results = {
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }

        # Check if it's time for LinkedIn post (example)
        # In production, would check schedule configuration
        # For now, just return empty results

        return results

    def run_continuous(self, cycle_interval: int = 300) -> None:
        """
        Run orchestrator continuously.

        Args:
            cycle_interval: Seconds between cycles (default: 300 = 5 minutes)
        """
        self.start()

        try:
            while self.running:
                # Run one cycle
                self.run_cycle()

                # Wait before next cycle
                print(f"⏳ Waiting {cycle_interval}s until next cycle...")
                time.sleep(cycle_interval)

        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        finally:
            self.stop()

    def run_once(self) -> Dict[str, Any]:
        """
        Run orchestrator once (for cron/scheduled execution).

        Returns:
            Cycle results
        """
        self.start()
        results = self.run_cycle()
        self.stop()
        return results


# Global instance
_orchestrator = None


def get_orchestrator() -> Orchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--once', action='store_true', help='Run once and exit (for cron)')
    parser.add_argument('--interval', type=int, default=300, help='Cycle interval in seconds')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without real execution')

    args = parser.parse_args()

    orchestrator = Orchestrator(dry_run=args.dry_run)

    if args.once:
        # Run once for cron/scheduler
        results = orchestrator.run_once()
        sys.exit(0 if not results.get('errors') else 1)
    else:
        # Run continuously
        orchestrator.run_continuous(cycle_interval=args.interval)
