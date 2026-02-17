"""
LinkedIn Scheduler - Schedules and executes LinkedIn post generation.
Handles weekly/daily post scheduling with configurable timing.
"""

import time
from datetime import datetime, timedelta
from typing import Optional
import schedule

from scripts.logger import get_logger
from scripts.post_generator import get_post_generator


class LinkedInScheduler:
    """
    Schedules LinkedIn post generation and publishing.

    Features:
    - Configurable schedule (daily, weekly, custom)
    - Automatic post generation
    - Approval workflow integration
    - Error handling and retry
    """

    def __init__(self, schedule_config: Optional[dict] = None):
        """
        Initialize LinkedIn scheduler.

        Args:
            schedule_config: Schedule configuration dictionary
                            (default: weekly Monday 9am)
        """
        self.logger = get_logger()
        self.post_generator = get_post_generator()
        self.schedule_config = schedule_config or {
            'frequency': 'weekly',
            'day': 'monday',
            'time': '09:00'
        }

    def setup_schedule(self) -> None:
        """Setup the posting schedule based on configuration."""
        frequency = self.schedule_config.get('frequency', 'weekly')
        time_str = self.schedule_config.get('time', '09:00')

        if frequency == 'daily':
            schedule.every().day.at(time_str).do(self.generate_and_publish_post)
            self.logger.info(
                component="scheduler",
                action="schedule_configured",
                actor="linkedin_scheduler",
                target="linkedin",
                details={'frequency': 'daily', 'time': time_str}
            )

        elif frequency == 'weekly':
            day = self.schedule_config.get('day', 'monday').lower()
            getattr(schedule.every(), day).at(time_str).do(self.generate_and_publish_post)
            self.logger.info(
                component="scheduler",
                action="schedule_configured",
                actor="linkedin_scheduler",
                target="linkedin",
                details={'frequency': 'weekly', 'day': day, 'time': time_str}
            )

        elif frequency == 'custom':
            # Custom cron-like schedule
            interval = self.schedule_config.get('interval_hours', 168)  # Default: weekly
            schedule.every(interval).hours.do(self.generate_and_publish_post)
            self.logger.info(
                component="scheduler",
                action="schedule_configured",
                actor="linkedin_scheduler",
                target="linkedin",
                details={'frequency': 'custom', 'interval_hours': interval}
            )

    def generate_and_publish_post(self) -> dict:
        """
        Generate and publish a LinkedIn post.

        Returns:
            Result dictionary with status and details
        """
        self.logger.info(
            component="scheduler",
            action="scheduled_post_triggered",
            actor="linkedin_scheduler",
            target="linkedin",
            details={'timestamp': datetime.now().isoformat() + 'Z'}
        )

        try:
            # Generate post
            post = self.post_generator.generate_post(tone='professional')

            # Create draft
            draft_file = self.post_generator.create_draft(post)

            # Publish (with approval workflow)
            result = self.post_generator.publish_post(post, wait_for_approval=True)

            self.logger.info(
                component="scheduler",
                action="scheduled_post_completed",
                actor="linkedin_scheduler",
                target="linkedin",
                details={
                    'status': result['status'],
                    'post_id': result.get('post_id'),
                    'draft_file': str(draft_file)
                }
            )

            return result

        except Exception as e:
            self.logger.error(
                component="scheduler",
                action="scheduled_post_failed",
                actor="linkedin_scheduler",
                target="linkedin",
                details={'error': str(e)}
            )
            return {
                'status': 'failed',
                'error': str(e)
            }

    def run(self, max_iterations: Optional[int] = None) -> None:
        """
        Run the scheduler.

        Args:
            max_iterations: Maximum iterations (None = run forever)
        """
        self.setup_schedule()

        self.logger.info(
            component="scheduler",
            action="scheduler_started",
            actor="linkedin_scheduler",
            target="linkedin",
            details={
                'frequency': self.schedule_config.get('frequency'),
                'max_iterations': max_iterations
            }
        )

        iteration = 0
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

            if max_iterations:
                iteration += 1
                if iteration >= max_iterations:
                    self.logger.info(
                        component="scheduler",
                        action="scheduler_stopped",
                        actor="linkedin_scheduler",
                        target="linkedin",
                        details={'iterations': iteration}
                    )
                    break

    def run_once(self) -> dict:
        """
        Run post generation once (for testing or manual trigger).

        Returns:
            Result dictionary
        """
        self.logger.info(
            component="scheduler",
            action="manual_post_triggered",
            actor="linkedin_scheduler",
            target="linkedin",
            details={'timestamp': datetime.now().isoformat() + 'Z'}
        )

        return self.generate_and_publish_post()


# Global instance
_linkedin_scheduler = None


def get_linkedin_scheduler() -> LinkedInScheduler:
    """Get or create the global LinkedIn scheduler instance."""
    global _linkedin_scheduler
    if _linkedin_scheduler is None:
        import os
        import json

        # Load schedule config from environment or config file
        schedule_config = None
        config_file = 'AI_Employee_Vault/Watchers/watcher_config.json'

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    schedule_config = config.get('linkedin_scheduler', {
                        'frequency': 'weekly',
                        'day': 'monday',
                        'time': '09:00'
                    })
            except Exception:
                pass

        _linkedin_scheduler = LinkedInScheduler(schedule_config)

    return _linkedin_scheduler


if __name__ == '__main__':
    # Run scheduler
    scheduler = get_linkedin_scheduler()
    print("LinkedIn Scheduler started")
    print(f"Schedule: {scheduler.schedule_config}")
    print("Press Ctrl+C to stop")

    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\nScheduler stopped")
