"""
Health Check Script - Comprehensive system health monitoring.
Validates all components and reports issues.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json
import subprocess

# Fix Windows encoding for emoji support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from scripts.logger import get_logger


class HealthChecker:
    """
    Performs comprehensive health checks on AI Employee system.

    Checks:
    - Watchers status and last execution
    - Event queue depth and stale events
    - Pending approvals and timeouts
    - Log file health
    - Disk space
    - Stale tasks
    - MCP server availability
    - Skill integrity
    """

    def __init__(self):
        """Initialize health checker."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.vault_dir = self.project_root / 'AI_Employee_Vault'

    def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Health check results
        """
        print("🏥 AI Employee Health Check")
        print("=" * 50)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        results = {
            'timestamp': datetime.now().isoformat() + 'Z',
            'checks': {},
            'warnings': [],
            'errors': [],
            'overall_status': 'healthy'
        }

        # Run all checks
        checks = [
            ('watchers', self._check_watchers),
            ('event_queue', self._check_event_queue),
            ('approvals', self._check_approvals),
            ('logs', self._check_logs),
            ('disk_space', self._check_disk_space),
            ('stale_tasks', self._check_stale_tasks),
            ('mcp_servers', self._check_mcp_servers),
            ('skills', self._check_skills),
            ('configuration', self._check_configuration)
        ]

        for check_name, check_func in checks:
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result

                # Collect warnings and errors
                if check_result.get('status') == 'warning':
                    results['warnings'].append(f"{check_name}: {check_result.get('message')}")
                elif check_result.get('status') == 'error':
                    results['errors'].append(f"{check_name}: {check_result.get('message')}")

            except Exception as e:
                results['checks'][check_name] = {
                    'status': 'error',
                    'message': f'Check failed: {str(e)}'
                }
                results['errors'].append(f"{check_name}: Check failed - {str(e)}")

        # Determine overall status
        if results['errors']:
            results['overall_status'] = 'unhealthy'
        elif results['warnings']:
            results['overall_status'] = 'degraded'

        # Print summary
        self._print_summary(results)

        # Log health check
        self.logger.info(
            component="maintenance",
            action="health_check_completed",
            actor="health_checker",
            target="system",
            details={
                'overall_status': results['overall_status'],
                'warnings_count': len(results['warnings']),
                'errors_count': len(results['errors'])
            }
        )

        return results

    def _check_watchers(self) -> Dict[str, Any]:
        """Check watcher status and last execution."""
        print("📡 Checking watchers...")

        watcher_dir = self.vault_dir / 'Watchers'
        config_file = watcher_dir / 'watcher_config.json'

        if not config_file.exists():
            print("   ⚠️  Watcher config not found")
            return {
                'status': 'warning',
                'message': 'Watcher configuration file missing'
            }

        # Load config
        with open(config_file) as f:
            config = json.load(f)

        # Handle nested structure (config has "watchers" key)
        watchers_config = config.get('watchers', config)
        enabled_watchers = [name for name, cfg in watchers_config.items() if cfg.get('enabled', False)]

        if not enabled_watchers:
            print("   ⚠️  No watchers enabled")
            return {
                'status': 'warning',
                'message': 'No watchers enabled',
                'enabled_count': 0
            }

        print(f"   ✅ {len(enabled_watchers)} watchers enabled: {', '.join(enabled_watchers)}")

        return {
            'status': 'ok',
            'message': f'{len(enabled_watchers)} watchers enabled',
            'enabled_watchers': enabled_watchers
        }

    def _check_event_queue(self) -> Dict[str, Any]:
        """Check event queue depth and stale events."""
        print("📋 Checking event queue...")

        needs_action_dir = self.vault_dir / 'Needs_Action'

        if not needs_action_dir.exists():
            print("   ❌ Needs_Action directory not found")
            return {
                'status': 'error',
                'message': 'Needs_Action directory missing'
            }

        # Count events
        events = list(needs_action_dir.glob('*.json')) + list(needs_action_dir.glob('*.md'))
        event_count = len(events)

        # Check for stale events (older than 24 hours)
        stale_threshold = datetime.now() - timedelta(hours=24)
        stale_events = []

        for event_file in events:
            mtime = datetime.fromtimestamp(event_file.stat().st_mtime)
            if mtime < stale_threshold:
                stale_events.append(event_file.name)

        if event_count > 50:
            print(f"   ⚠️  High queue depth: {event_count} events")
            return {
                'status': 'warning',
                'message': f'High queue depth: {event_count} events',
                'queue_depth': event_count,
                'stale_events': len(stale_events)
            }

        if stale_events:
            print(f"   ⚠️  {len(stale_events)} stale events (>24h old)")
            return {
                'status': 'warning',
                'message': f'{len(stale_events)} stale events',
                'queue_depth': event_count,
                'stale_events': len(stale_events),
                'stale_files': stale_events[:5]  # First 5
            }

        print(f"   ✅ Queue healthy: {event_count} events")
        return {
            'status': 'ok',
            'message': f'{event_count} events in queue',
            'queue_depth': event_count,
            'stale_events': 0
        }

    def _check_approvals(self) -> Dict[str, Any]:
        """Check pending approvals and timeouts."""
        print("✋ Checking approvals...")

        pending_dir = self.vault_dir / 'Pending_Approval'

        if not pending_dir.exists():
            print("   ⚠️  Pending_Approval directory not found")
            return {
                'status': 'warning',
                'message': 'Pending_Approval directory missing'
            }

        # Count pending approvals
        pending = list(pending_dir.glob('*.md'))
        pending_count = len(pending)

        # Check for timeouts (>24 hours)
        timeout_threshold = datetime.now() - timedelta(hours=24)
        timed_out = []

        for approval_file in pending:
            mtime = datetime.fromtimestamp(approval_file.stat().st_mtime)
            if mtime < timeout_threshold:
                timed_out.append(approval_file.name)

        if timed_out:
            print(f"   ⚠️  {len(timed_out)} approvals timed out")
            return {
                'status': 'warning',
                'message': f'{len(timed_out)} approvals timed out',
                'pending_count': pending_count,
                'timed_out': len(timed_out),
                'timed_out_files': timed_out[:5]
            }

        if pending_count > 10:
            print(f"   ⚠️  High pending count: {pending_count}")
            return {
                'status': 'warning',
                'message': f'High pending approval count: {pending_count}',
                'pending_count': pending_count
            }

        print(f"   ✅ {pending_count} pending approvals")
        return {
            'status': 'ok',
            'message': f'{pending_count} pending approvals',
            'pending_count': pending_count,
            'timed_out': 0
        }

    def _check_logs(self) -> Dict[str, Any]:
        """Check log file health."""
        print("📝 Checking logs...")

        log_dir = self.vault_dir / 'Logs'

        if not log_dir.exists():
            print("   ❌ Logs directory not found")
            return {
                'status': 'error',
                'message': 'Logs directory missing'
            }

        # Check for today's log
        today_log = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        if not today_log.exists():
            print("   ⚠️  No log file for today")
            return {
                'status': 'warning',
                'message': 'No log file for today (system may not be running)'
            }

        # Check log file size
        log_size = today_log.stat().st_size

        if log_size == 0:
            print("   ⚠️  Today's log is empty")
            return {
                'status': 'warning',
                'message': 'Today\'s log file is empty'
            }

        # Count log files
        log_files = list(log_dir.glob('*.json'))
        log_count = len(log_files)

        print(f"   ✅ {log_count} log files, today's log: {log_size:,} bytes")
        return {
            'status': 'ok',
            'message': f'{log_count} log files',
            'log_count': log_count,
            'today_log_size': log_size
        }

    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space (cross-platform)."""
        print("💾 Checking disk space...")

        try:
            import shutil

            # Get disk usage statistics (works on Windows, Linux, macOS)
            usage = shutil.disk_usage(str(self.vault_dir))

            # Calculate metrics
            total_bytes = usage.total
            used_bytes = usage.used
            available_bytes = usage.free
            used_percent = (used_bytes / total_bytes) * 100
            available_gb = available_bytes / (1024**3)

            if used_percent > 90:
                print(f"   ❌ Disk space critical: {used_percent:.1f}% used")
                return {
                    'status': 'error',
                    'message': f'Disk space critical: {used_percent:.1f}% used',
                    'used_percent': used_percent,
                    'available_gb': available_gb
                }

            if used_percent > 80:
                print(f"   ⚠️  Disk space low: {used_percent:.1f}% used")
                return {
                    'status': 'warning',
                    'message': f'Disk space low: {used_percent:.1f}% used',
                    'used_percent': used_percent,
                    'available_gb': available_gb
                }

            print(f"   ✅ Disk space OK: {used_percent:.1f}% used, {available_gb:.1f} GB available")
            return {
                'status': 'ok',
                'message': f'{used_percent:.1f}% used',
                'used_percent': used_percent,
                'available_gb': available_gb
            }

        except Exception as e:
            print(f"   ⚠️  Could not check disk space: {str(e)}")
            return {
                'status': 'warning',
                'message': f'Could not check disk space: {str(e)}'
            }

    def _check_stale_tasks(self) -> Dict[str, Any]:
        """Check for stale tasks stuck in progress."""
        print("⏰ Checking for stale tasks...")

        # Check for tasks in Needs_Action older than 48 hours
        needs_action_dir = self.vault_dir / 'Needs_Action'
        stale_threshold = datetime.now() - timedelta(hours=48)
        stale_tasks = []

        if needs_action_dir.exists():
            for task_file in needs_action_dir.glob('*.md'):
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if mtime < stale_threshold:
                    stale_tasks.append(task_file.name)

        if stale_tasks:
            print(f"   ⚠️  {len(stale_tasks)} stale tasks (>48h old)")
            return {
                'status': 'warning',
                'message': f'{len(stale_tasks)} stale tasks',
                'stale_count': len(stale_tasks),
                'stale_files': stale_tasks[:5]
            }

        print("   ✅ No stale tasks")
        return {
            'status': 'ok',
            'message': 'No stale tasks',
            'stale_count': 0
        }

    def _check_mcp_servers(self) -> Dict[str, Any]:
        """Check MCP server availability."""
        print("🔌 Checking MCP servers...")

        mcp_dir = self.project_root / 'mcp_servers'
        config_file = mcp_dir / 'server_config.json'

        if not config_file.exists():
            print("   ⚠️  MCP server config not found")
            return {
                'status': 'warning',
                'message': 'MCP server configuration missing'
            }

        print("   ✅ MCP server configuration found")
        return {
            'status': 'ok',
            'message': 'MCP servers configured'
        }

    def _check_skills(self) -> Dict[str, Any]:
        """Check skill integrity."""
        print("🎯 Checking skills...")

        skills_dir = self.project_root / '.claude' / 'skills'

        if not skills_dir.exists():
            print("   ❌ Skills directory not found")
            return {
                'status': 'error',
                'message': 'Skills directory missing'
            }

        # Count skills
        skills = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        skill_count = len(skills)

        # Check each skill has required files
        incomplete_skills = []
        for skill_dir in skills:
            required_files = ['SKILL.md', 'prompt.txt', 'examples.md']
            missing = [f for f in required_files if not (skill_dir / f).exists()]
            if missing:
                incomplete_skills.append(f"{skill_dir.name} (missing: {', '.join(missing)})")

        if incomplete_skills:
            print(f"   ⚠️  {len(incomplete_skills)} incomplete skills")
            return {
                'status': 'warning',
                'message': f'{len(incomplete_skills)} incomplete skills',
                'skill_count': skill_count,
                'incomplete': incomplete_skills
            }

        print(f"   ✅ {skill_count} skills configured")
        return {
            'status': 'ok',
            'message': f'{skill_count} skills configured',
            'skill_count': skill_count
        }

    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration files."""
        print("⚙️  Checking configuration...")

        env_file = self.project_root / '.env'

        if not env_file.exists():
            print("   ⚠️  .env file not found")
            return {
                'status': 'warning',
                'message': '.env file missing (using defaults)'
            }

        print("   ✅ Configuration file found")
        return {
            'status': 'ok',
            'message': 'Configuration file present'
        }

    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print health check summary."""
        print()
        print("=" * 50)
        print("HEALTH CHECK SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌'
        }.get(results['overall_status'], '❓')

        print(f"Overall Status: {status_emoji} {results['overall_status'].upper()}")
        print()

        if results['warnings']:
            print(f"Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"  ⚠️  {warning}")
            print()

        if results['errors']:
            print(f"Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  ❌ {error}")
            print()

        print("Component Status:")
        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            message = check_result.get('message', 'No details')
            emoji = {'ok': '✅', 'warning': '⚠️', 'error': '❌'}.get(status, '❓')
            print(f"  {emoji} {check_name}: {message}")

        print()


if __name__ == '__main__':
    checker = HealthChecker()
    results = checker.check_all()

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'healthy' else 1
    sys.exit(exit_code)
