"""
Update Dashboard - Updates Dashboard.md with current system status.
Provides daily summary of system activity and health.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json

from scripts.logger import get_logger
from scripts.watchdog import get_watchdog


class DashboardUpdater:
    """
    Updates Dashboard.md with current system status.

    Updates:
    - System health status
    - Recent activity summary
    - Pending approvals count
    - Event queue status
    - Recent completions
    - Alerts and warnings
    """

    def __init__(self):
        """Initialize dashboard updater."""
        self.logger = get_logger()
        self.watchdog = get_watchdog()
        self.dashboard_file = Path('AI_Employee_Vault/Dashboard.md')
        self.vault_dir = Path('AI_Employee_Vault')

    def update_dashboard(self) -> None:
        """Update the dashboard with current status."""
        print("📊 Updating dashboard...")

        # Gather data
        health = self.watchdog.check_system_health()
        activity = self._get_recent_activity()
        stats = self._get_statistics()

        # Generate dashboard content
        content = self._generate_dashboard_content(health, activity, stats)

        # Write dashboard
        self.dashboard_file.write_text(content, encoding='utf-8')

        self.logger.info(
            component="dashboard",
            action="dashboard_updated",
            actor="dashboard_updater",
            target=str(self.dashboard_file),
            details={
                'health_status': health['status'],
                'alerts_count': len(health['alerts'])
            }
        )

        print(f"   ✅ Dashboard updated: {self.dashboard_file}")

    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity summary."""
        activity = {
            'events_today': 0,
            'tasks_completed_today': 0,
            'approvals_pending': 0,
            'recent_completions': []
        }

        # Count events processed today
        done_dir = self.vault_dir / 'Done'
        if done_dir.exists():
            today = datetime.now().date()
            today_files = [
                f for f in done_dir.glob('*.json')
                if datetime.fromdate(f.stat().st_mtime).date() == today
            ]
            activity['events_today'] = len(today_files)

        # Count pending approvals
        pending_dir = self.vault_dir / 'Pending_Approval'
        if pending_dir.exists():
            activity['approvals_pending'] = len(list(pending_dir.glob('*.md')))

        # Get recent completions
        if done_dir.exists():
            recent_files = sorted(
                done_dir.glob('*.json'),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )[:5]

            for file in recent_files:
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        activity['recent_completions'].append({
                            'source': data.get('source', 'unknown'),
                            'type': data.get('type', 'unknown'),
                            'timestamp': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                        })
                except Exception:
                    pass

        return activity

    def _get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = {
            'total_events_processed': 0,
            'total_approvals_granted': 0,
            'total_approvals_rejected': 0,
            'uptime_days': 0
        }

        # Count total events in Done
        done_dir = self.vault_dir / 'Done'
        if done_dir.exists():
            stats['total_events_processed'] = len(list(done_dir.glob('*.json')))

        # Count approvals
        approved_dir = self.vault_dir / 'Approved'
        if approved_dir.exists():
            stats['total_approvals_granted'] = len(list(approved_dir.glob('*.md')))

        rejected_dir = self.vault_dir / 'Rejected'
        if rejected_dir.exists():
            stats['total_approvals_rejected'] = len(list(rejected_dir.glob('*.md')))

        # Calculate uptime (days since first log)
        log_dir = self.vault_dir / 'Logs'
        if log_dir.exists():
            log_files = list(log_dir.glob('*.json'))
            if log_files:
                oldest_log = min(log_files, key=lambda f: f.stat().st_mtime)
                uptime_seconds = datetime.now().timestamp() - oldest_log.stat().st_mtime
                stats['uptime_days'] = int(uptime_seconds / (24 * 3600))

        return stats

    def _generate_dashboard_content(
        self,
        health: Dict[str, Any],
        activity: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> str:
        """Generate dashboard markdown content."""
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌'
        }.get(health['status'], '❓')

        content = f"""# AI Employee Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**System Status**: {status_emoji} {health['status'].upper()}

---

## System Health

{self._format_health_checks(health)}

## Today's Activity

- **Events Processed**: {activity['events_today']}
- **Tasks Completed**: {activity['tasks_completed_today']}
- **Pending Approvals**: {activity['approvals_pending']}

## Recent Completions

{self._format_recent_completions(activity['recent_completions'])}

## System Statistics

- **Total Events Processed**: {stats['total_events_processed']}
- **Approvals Granted**: {stats['total_approvals_granted']}
- **Approvals Rejected**: {stats['total_approvals_rejected']}
- **System Uptime**: {stats['uptime_days']} days

## Active Alerts

{self._format_alerts(health['alerts'])}

---

## Quick Links

- [Business Goals](Business_Goals.md)
- [Current Plan](Plan.md)
- [Pending Approvals](Pending_Approval/)
- [Needs Action](Needs_Action/)
- [Completed Tasks](Done/)
- [System Logs](Logs/)

---

*Dashboard automatically updated daily*
"""

        return content

    def _format_health_checks(self, health: Dict[str, Any]) -> str:
        """Format health check results."""
        lines = []

        for check_name, result in health['checks'].items():
            status_emoji = {
                'ok': '✅',
                'warning': '⚠️',
                'error': '❌',
                'critical': '🔴'
            }.get(result.get('status', 'unknown'), '❓')

            check_label = check_name.replace('_', ' ').title()
            message = result.get('message', 'No details')

            lines.append(f"- **{check_label}**: {status_emoji} {message}")

        return '\n'.join(lines) if lines else "*No health checks available*"

    def _format_recent_completions(self, completions: List[Dict[str, Any]]) -> str:
        """Format recent completions list."""
        if not completions:
            return "*No recent completions*"

        lines = []
        for completion in completions:
            lines.append(
                f"- **{completion['source']}** - {completion['type']} "
                f"({completion['timestamp']})"
            )

        return '\n'.join(lines)

    def _format_alerts(self, alerts: List[str]) -> str:
        """Format active alerts."""
        if not alerts:
            return "✅ *No active alerts*"

        lines = []
        for alert in alerts:
            lines.append(f"- ⚠️ {alert}")

        return '\n'.join(lines)


# Global instance
_dashboard_updater = None


def get_dashboard_updater() -> DashboardUpdater:
    """Get or create the global dashboard updater instance."""
    global _dashboard_updater
    if _dashboard_updater is None:
        _dashboard_updater = DashboardUpdater()
    return _dashboard_updater


if __name__ == '__main__':
    updater = get_dashboard_updater()
    updater.update_dashboard()
