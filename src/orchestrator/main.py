"""Main orchestrator for Bronze Tier Constitutional FTE.

Continuous task loop that monitors, evaluates, executes, and logs.
"""

import sys
import time
import signal
from pathlib import Path

from src.orchestrator.config import Config
from src.orchestrator.task_processor import TaskProcessor
from src.watchers import FileWatcher


class Orchestrator:
    """Main orchestrator for Bronze Tier FTE.

    Implements continuous polling loop with graceful shutdown.
    Enforces all constitutional principles.
    """

    def __init__(self, config: Config):
        """Initialize orchestrator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.running = False
        self.task_processor = TaskProcessor(
            needs_action_path=config.needs_action_path,
            done_path=config.done_path,
            pending_approval_path=config.pending_approval_path,
            logs_path=config.logs_path,
            skills_path=config.skills_path,
            vault_path=config.vault_path,
            dry_run=config.dry_run
        )

        # Initialize file watcher for demo workflow
        self.file_watcher = FileWatcher(
            name="demo-file-watcher",
            monitored_path=Path("monitored"),
            needs_action_path=config.needs_action_path,
            file_pattern="*.txt",
            task_type="draft_email",
            enabled=True
        )

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        print(f"\n[{self._timestamp()}] Received shutdown signal, stopping gracefully...")
        self.stop()

    def _timestamp(self) -> str:
        """Get current timestamp for logging.

        Returns:
            ISO 8601 timestamp string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def start(self) -> None:
        """Start the orchestrator loop.

        Continuously monitors for tasks and processes them.
        Implements Ralph Wiggum persistence - keeps running until stopped.
        """
        self.running = True

        print(f"[{self._timestamp()}] Bronze Tier FTE Orchestrator starting...")
        print(f"[{self._timestamp()}] DRY_RUN mode: {self.config.dry_run}")
        print(f"[{self._timestamp()}] Log level: {self.config.log_level}")
        print(f"[{self._timestamp()}] Poll interval: {self.config.poll_interval}s")
        print(f"[{self._timestamp()}] Max retries: {self.config.max_retries}")
        print(f"[{self._timestamp()}] Monitoring: {self.config.needs_action_path}")
        print(f"[{self._timestamp()}] Done folder: {self.config.done_path}")
        print(f"[{self._timestamp()}] Pending Approval folder: {self.config.pending_approval_path}")
        print()

        # Ensure directories exist
        self.config.ensure_directories()

        # Validate all skills
        print(f"[{self._timestamp()}] Validating skills...")
        skills_valid = self.task_processor.validate_skills()
        if not skills_valid:
            print(f"[{self._timestamp()}] WARNING: Some skills failed validation (check logs)")
        else:
            print(f"[{self._timestamp()}] All skills validated successfully")
        print()

        # Recover incomplete tasks from previous run
        print(f"[{self._timestamp()}] Checking for incomplete tasks...")
        recovered = self.task_processor.recover_incomplete_tasks()
        if recovered > 0:
            print(f"[{self._timestamp()}] Recovered {recovered} incomplete task(s)")
        print()

        # Start file watcher
        print(f"[{self._timestamp()}] Starting file watcher on: monitored/")
        self.file_watcher.start()

        # Log startup
        self.task_processor.logging_skill.log_action(
            action="orchestrator_start",
            risk_level="LOW",
            outcome="SUCCESS",
            skill_used="orchestrator",
            approval_status="AUTO_APPROVED",
            dry_run=self.config.dry_run,
            poll_interval=self.config.poll_interval,
            max_retries=self.config.max_retries,
            watcher_enabled=self.file_watcher.is_running(),
            recovered_tasks=recovered
        )

        print(f"[{self._timestamp()}] Starting orchestrator loop (press Ctrl+C to stop)...")
        print()

        # Track cycles for periodic dashboard updates
        cycle_count = 0

        # Main orchestration loop
        while self.running:
            try:
                # Process all tasks in Needs_Action
                processed = self.task_processor.process_all_tasks()

                if processed > 0:
                    print(f"[{self._timestamp()}] Processed {processed} task(s)")
                    # Update dashboard after processing tasks
                    self.task_processor.update_dashboard()

                # Update dashboard periodically (every 12 cycles = ~1 minute with 5s interval)
                cycle_count += 1
                if cycle_count >= 12:
                    self.task_processor.update_dashboard()
                    cycle_count = 0

                # Sleep until next poll
                time.sleep(self.config.poll_interval)

            except KeyboardInterrupt:
                # Graceful shutdown on Ctrl+C
                print(f"\n[{self._timestamp()}] KeyboardInterrupt received, stopping...")
                self.stop()
                break

            except Exception as e:
                # Log error and continue
                print(f"[{self._timestamp()}] ERROR: {e}")
                self.task_processor.logging_skill.log_action(
                    action="orchestrator_error",
                    risk_level="MEDIUM",
                    outcome="FAILURE",
                    error=str(e),
                    skill_used="orchestrator",
                    approval_status="AUTO_APPROVED",
                    dry_run=self.config.dry_run
                )
                # Continue after error (persistence)
                time.sleep(self.config.poll_interval)

    def stop(self) -> None:
        """Stop the orchestrator gracefully."""
        self.running = False

        # Stop file watcher
        print(f"[{self._timestamp()}] Stopping file watcher...")
        self.file_watcher.stop()

        # Log shutdown
        self.task_processor.logging_skill.log_action(
            action="orchestrator_stop",
            risk_level="LOW",
            outcome="SUCCESS",
            skill_used="orchestrator",
            approval_status="AUTO_APPROVED",
            dry_run=self.config.dry_run
        )

        print(f"[{self._timestamp()}] Orchestrator stopped")


def main():
    """Main entry point for orchestrator."""
    # Load configuration
    config = Config()

    # Create and start orchestrator
    orchestrator = Orchestrator(config)

    try:
        orchestrator.start()
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
