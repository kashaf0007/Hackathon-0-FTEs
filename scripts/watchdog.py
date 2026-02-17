"""
Watchdog - System health monitoring and alerting.
Monitors system components and creates alerts for failures.
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from scripts.logger import get_logger


class Watchdog:
    """
    Monitors system health and creates alerts for failures.

    Monitors:
    - Watcher execution status
    - Event queue processing
    - Approval timeouts
    - Log file growth
    - Disk space
    - System responsiveness
    """

    def __init__(self):
        """Initialize watchdog."""
        self.logger = get_logger()
        self.vault_dir = Path('AI_Employee_Vault')
        self.alerts = []

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check overall system health.

        Returns:
            Health check results
        """
        health = {
            'status': 'healthy',
            'checks': {},
            'alerts': [],
            'timestamp': datetime.now().isoformat() + 'Z'
        }

        # Run all health checks
        checks = [
            ('watchers', self._check_watchers),
            ('event_queue', self._check_event_queue),
            ('approvals', self._check_approvals),
            ('logs', self._check_logs),
            ('disk_space', self._check_disk_space),
            ('stale_tasks', self._check_stale_tasks)
        ]

        for check_name, check_func in checks:
            try:
                result = check_func()
                health['checks'][check_name] = result

                if result['status'] != 'ok':
                    health['status'] = 'degraded' if health['status'] == 'healthy' else 'unhealthy'
                    if result.get('alert'):
                        health['alerts'].append(result['alert'])

            except Exception as e:
                health['checks'][check_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health['status'] = 'unhealthy'

        # Log health check
        self.logger.info(
            component="watchdog",
            action="health_check_completed",
            actor="watchdog",
            target="system",
            details={
                'status': health['status'],
                'alerts_count': len(health['alerts'])
            }
        )

        return health

    def _check_watchers(self) -> Dict[str, Any]:
        """Check watcher execution status."""
        # Check if watchers have run recently (within last hour)
        log_dir = self.vault_dir / 'Logs'
        if not log_dir.exists():
            return {
                'status': 'warning',
                'message': 'Log directory not found',
                'alert': 'Watchdog: Log directory missing'
            }

        # Check today's log file
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f'{today}.json'

        if not log_file.exists():
            return {
                'status': 'warning',
                'message': 'No logs for today',
                'alert': 'Watchdog: No watcher activity logged today'
            }

        # Check last watcher execution time
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Check last few lines for watcher activity
                    recent_watcher_activity = False
                    for line in lines[-50:]:  # Check last 50 log entries
                        if 'watcher' in line.lower():
                            recent_watcher_activity = True
                            break

                    if not recent_watcher_activity:
                        return {
                            'status': 'warning',
                            'message': 'No recent watcher activity',
                            'alert': 'Watchdog: Watchers may not be running'
                        }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error reading logs: {str(e)}'
            }

        return {
            'status': 'ok',
            'message': 'Watchers running normally'
        }

    def _check_event_queue(self) -> Dict[str, Any]:
        """Check event queue status."""
        needs_action_dir = self.vault_dir / 'Needs_Action'

        if not needs_action_dir.exists():
            return {
                'status': 'warning',
                'message': 'Needs_Action directory not found'
            }

        # Count pending events
        pending_events = list(needs_action_dir.glob('*.json'))
        pending_count = len(pending_events)

        # Check for very old events (>7 days)
        old_events = []
        cutoff_time = time.time() - (7 * 24 * 3600)

        for event_file in pending_events:
            if event_file.stat().st_mtime < cutoff_time:
                old_events.append(event_file.name)

        if old_events:
            return {
                'status': 'warning',
                'message': f'{len(old_events)} events older than 7 days',
                'alert': f'Watchdog: {len(old_events)} stale events in queue',
                'old_events': old_events[:5]  # List first 5
            }

        if pending_count > 100:
            return {
                'status': 'warning',
                'message': f'Large queue: {pending_count} pending events',
                'alert': f'Watchdog: Event queue backlog ({pending_count} events)'
            }

        return {
            'status': 'ok',
            'message': f'{pending_count} pending events',
            'pending_count': pending_count
        }

    def _check_approvals(self) -> Dict[str, Any]:
        """Check approval status."""
        pending_dir = self.vault_dir / 'Pending_Approval'

        if not pending_dir.exists():
            return {
                'status': 'ok',
                'message': 'No pending approvals'
            }

        # Count pending approvals
        pending_approvals = list(pending_dir.glob('*.md'))
        pending_count = len(pending_approvals)

        # Check for approvals nearing timeout (>20 hours old)
        near_timeout = []
        timeout_threshold = time.time() - (20 * 3600)

        for approval_file in pending_approvals:
            if approval_file.stat().st_mtime < timeout_threshold:
                near_timeout.append(approval_file.name)

        if near_timeout:
            return {
                'status': 'warning',
                'message': f'{len(near_timeout)} approvals nearing timeout',
                'alert': f'Watchdog: {len(near_timeout)} approvals need attention',
                'near_timeout': near_timeout[:5]
            }

        if pending_count > 10:
            return {
                'status': 'warning',
                'message': f'Many pending approvals: {pending_count}',
                'alert': f'Watchdog: {pending_count} pending approvals'
            }

        return {
            'status': 'ok',
            'message': f'{pending_count} pending approvals',
            'pending_count': pending_count
        }

    def _check_logs(self) -> Dict[str, Any]:
        """Check log file status."""
        log_dir = self.vault_dir / 'Logs'

        if not log_dir.exists():
            return {
                'status': 'warning',
                'message': 'Log directory not found'
            }

        # Check total log size
        total_size = sum(f.stat().st_size for f in log_dir.glob('*.json'))
        total_size_mb = total_size / (1024 * 1024)

        if total_size_mb > 500:  # 500 MB threshold
            return {
                'status': 'warning',
                'message': f'Large log size: {total_size_mb:.1f} MB',
                'alert': f'Watchdog: Log files using {total_size_mb:.1f} MB'
            }

        return {
            'status': 'ok',
            'message': f'Log size: {total_size_mb:.1f} MB',
            'size_mb': total_size_mb
        }

    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            import shutil
            usage = shutil.disk_usage(str(self.vault_dir))
            free_gb = usage.free / (1024 ** 3)
            percent_free = (usage.free / usage.total) * 100

            if percent_free < 10:
                return {
                    'status': 'critical',
                    'message': f'Low disk space: {free_gb:.1f} GB free ({percent_free:.1f}%)',
                    'alert': f'Watchdog: CRITICAL - Only {free_gb:.1f} GB disk space remaining'
                }

            if percent_free < 20:
                return {
                    'status': 'warning',
                    'message': f'Disk space low: {free_gb:.1f} GB free ({percent_free:.1f}%)',
                    'alert': f'Watchdog: Low disk space ({free_gb:.1f} GB remaining)'
                }

            return {
                'status': 'ok',
                'message': f'{free_gb:.1f} GB free ({percent_free:.1f}%)',
                'free_gb': free_gb,
                'percent_free': percent_free
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking disk space: {str(e)}'
            }

    def _check_stale_tasks(self) -> Dict[str, Any]:
        """Check for stale tasks in various directories."""
        stale_count = 0
        stale_locations = []

        # Check Needs_Action for old tasks
        needs_action_dir = self.vault_dir / 'Needs_Action'
        if needs_action_dir.exists():
            cutoff = time.time() - (14 * 24 * 3600)  # 14 days
            stale_files = [
                f for f in needs_action_dir.glob('*.json')
                if f.stat().st_mtime < cutoff
            ]
            if stale_files:
                stale_count += len(stale_files)
                stale_locations.append(f'Needs_Action: {len(stale_files)} files')

        if stale_count > 0:
            return {
                'status': 'warning',
                'message': f'{stale_count} stale tasks found',
                'alert': f'Watchdog: {stale_count} stale tasks need cleanup',
                'locations': stale_locations
            }

        return {
            'status': 'ok',
            'message': 'No stale tasks'
        }

    def create_alert(self, alert_message: str, severity: str = 'warning') -> Path:
        """
        Create an alert file in Needs_Action.

        Args:
            alert_message: Alert message
            severity: Alert severity (info, warning, critical)

        Returns:
            Path to created alert file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alert_file = self.vault_dir / 'Needs_Action' / f'alert_{timestamp}.md'

        content = f"""# System Alert

**Severity**: {severity.upper()}
**Created**: {datetime.now().isoformat()}Z
**Source**: Watchdog

## Alert Message

{alert_message}

## Action Required

Please review this alert and take appropriate action.

## Resolution

- [ ] Issue investigated
- [ ] Action taken
- [ ] Alert resolved

Move this file to Done/ when resolved.
"""

        alert_file.parent.mkdir(parents=True, exist_ok=True)
        alert_file.write_text(content, encoding='utf-8')

        self.logger.warning(
            component="watchdog",
            action="alert_created",
            actor="watchdog",
            target="system",
            details={
                'severity': severity,
                'message': alert_message,
                'alert_file': str(alert_file)
            }
        )

        return alert_file

    def run_health_check(self) -> None:
        """Run health check and create alerts if needed."""
        print("🏥 Running system health check...")

        health = self.check_system_health()

        print(f"   Status: {health['status'].upper()}")
        print(f"   Checks: {len(health['checks'])}")
        print(f"   Alerts: {len(health['alerts'])}")

        # Create alert files for any issues
        for alert in health['alerts']:
            severity = 'critical' if 'CRITICAL' in alert else 'warning'
            self.create_alert(alert, severity)

        print()


# Global instance
_watchdog = None


def get_watchdog() -> Watchdog:
    """Get or create the global watchdog instance."""
    global _watchdog
    if _watchdog is None:
        _watchdog = Watchdog()
    return _watchdog


if __name__ == '__main__':
    watchdog = get_watchdog()
    watchdog.run_health_check()
