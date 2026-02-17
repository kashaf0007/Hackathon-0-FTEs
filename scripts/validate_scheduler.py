"""
Scheduler Validation Script - Validates scheduler configuration and health.
Checks if scheduled tasks are configured correctly and running as expected.
"""

import os
import sys
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from scripts.logger import get_logger


class SchedulerValidator:
    """
    Validates scheduler configuration and health.

    Checks:
    - Scheduler type (cron, Task Scheduler, launchd)
    - Task configuration
    - Recent execution logs
    - Python environment
    - File permissions
    """

    def __init__(self):
        """Initialize scheduler validator."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.platform = platform.system()

    def validate(self) -> Dict[str, Any]:
        """
        Run full validation.

        Returns:
            Validation results
        """
        print("🔍 AI Employee Scheduler Validation")
        print("====================================")
        print()

        results = {
            'platform': self.platform,
            'checks': {},
            'warnings': [],
            'errors': [],
            'timestamp': datetime.now().isoformat() + 'Z'
        }

        # Run platform-specific checks
        if self.platform == 'Linux':
            results['checks']['scheduler'] = self._check_cron()
        elif self.platform == 'Darwin':
            results['checks']['scheduler'] = self._check_launchd()
        elif self.platform == 'Windows':
            results['checks']['scheduler'] = self._check_task_scheduler()
        else:
            results['errors'].append(f"Unsupported platform: {self.platform}")

        # Run common checks
        results['checks']['python'] = self._check_python()
        results['checks']['environment'] = self._check_environment()
        results['checks']['logs'] = self._check_logs()
        results['checks']['permissions'] = self._check_permissions()

        # Determine overall status
        has_errors = len(results['errors']) > 0 or any(
            check.get('status') == 'error' for check in results['checks'].values()
        )
        has_warnings = len(results['warnings']) > 0 or any(
            check.get('status') == 'warning' for check in results['checks'].values()
        )

        if has_errors:
            results['status'] = 'failed'
        elif has_warnings:
            results['status'] = 'warning'
        else:
            results['status'] = 'passed'

        # Print results
        self._print_results(results)

        return results

    def _check_cron(self) -> Dict[str, Any]:
        """Check cron configuration (Linux)."""
        print("📋 Checking cron configuration...")

        try:
            # Check if crontab exists
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("   ❌ No crontab found")
                return {
                    'status': 'error',
                    'message': 'No crontab configured'
                }

            # Check for AI Employee jobs
            crontab_content = result.stdout
            ai_jobs = [line for line in crontab_content.split('\n') if 'AI Employee' in line]

            if not ai_jobs:
                print("   ⚠️  No AI Employee jobs found in crontab")
                return {
                    'status': 'warning',
                    'message': 'No AI Employee jobs configured',
                    'suggestion': 'Run: bash scripts/scheduler_setup.sh'
                }

            print(f"   ✅ Found {len(ai_jobs)} AI Employee cron jobs")
            return {
                'status': 'ok',
                'message': f'{len(ai_jobs)} cron jobs configured',
                'jobs': ai_jobs
            }

        except FileNotFoundError:
            print("   ❌ crontab command not found")
            return {
                'status': 'error',
                'message': 'cron not installed'
            }

    def _check_launchd(self) -> Dict[str, Any]:
        """Check launchd configuration (macOS)."""
        print("📋 Checking launchd configuration...")

        launch_agents_dir = Path.home() / 'Library' / 'LaunchAgents'

        if not launch_agents_dir.exists():
            print("   ⚠️  LaunchAgents directory not found")
            return {
                'status': 'warning',
                'message': 'LaunchAgents directory missing'
            }

        # Check for AI Employee plists
        ai_plists = list(launch_agents_dir.glob('com.aiemployee.*.plist'))

        if not ai_plists:
            print("   ⚠️  No AI Employee agents found")
            return {
                'status': 'warning',
                'message': 'No AI Employee agents configured',
                'suggestion': 'Run: bash scripts/setup_macos_scheduler.sh'
            }

        # Check if agents are loaded
        try:
            result = subprocess.run(
                ['launchctl', 'list'],
                capture_output=True,
                text=True
            )

            loaded_agents = [
                line for line in result.stdout.split('\n')
                if 'com.aiemployee' in line
            ]

            print(f"   ✅ Found {len(ai_plists)} agents ({len(loaded_agents)} loaded)")
            return {
                'status': 'ok',
                'message': f'{len(ai_plists)} agents configured, {len(loaded_agents)} loaded',
                'agents': [p.name for p in ai_plists]
            }

        except FileNotFoundError:
            print("   ❌ launchctl command not found")
            return {
                'status': 'error',
                'message': 'launchctl not available'
            }

    def _check_task_scheduler(self) -> Dict[str, Any]:
        """Check Windows Task Scheduler configuration."""
        print("📋 Checking Task Scheduler configuration...")

        try:
            # Use PowerShell to check for AI Employee tasks
            result = subprocess.run(
                ['powershell', '-Command',
                 "Get-ScheduledTask | Where-Object {$_.TaskName -like 'AI_Employee*'} | Select-Object TaskName, State"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("   ❌ Failed to query Task Scheduler")
                return {
                    'status': 'error',
                    'message': 'Failed to query Task Scheduler'
                }

            output = result.stdout.strip()

            if not output or 'AI_Employee' not in output:
                print("   ⚠️  No AI Employee tasks found")
                return {
                    'status': 'warning',
                    'message': 'No AI Employee tasks configured',
                    'suggestion': 'Run as Admin: .\\scripts\\setup_windows_scheduler.ps1'
                }

            # Count tasks
            task_count = output.count('AI_Employee')
            print(f"   ✅ Found {task_count} AI Employee tasks")

            return {
                'status': 'ok',
                'message': f'{task_count} tasks configured',
                'tasks': output
            }

        except FileNotFoundError:
            print("   ❌ PowerShell not found")
            return {
                'status': 'error',
                'message': 'PowerShell not available'
            }

    def _check_python(self) -> Dict[str, Any]:
        """Check Python installation."""
        print("🐍 Checking Python environment...")

        python_version = sys.version.split()[0]
        major, minor = map(int, python_version.split('.')[:2])

        if major < 3 or (major == 3 and minor < 11):
            print(f"   ⚠️  Python {python_version} (3.11+ recommended)")
            return {
                'status': 'warning',
                'message': f'Python {python_version} (upgrade to 3.11+ recommended)',
                'version': python_version
            }

        print(f"   ✅ Python {python_version}")
        return {
            'status': 'ok',
            'message': f'Python {python_version}',
            'version': python_version
        }

    def _check_environment(self) -> Dict[str, Any]:
        """Check environment configuration."""
        print("⚙️  Checking environment...")

        env_file = self.project_root / '.env'

        if not env_file.exists():
            print("   ⚠️  .env file not found")
            return {
                'status': 'warning',
                'message': '.env file missing',
                'suggestion': 'Copy .env.example to .env'
            }

        # Check DRY_RUN setting
        dry_run = os.getenv('DRY_RUN', 'true')
        print(f"   ℹ️  DRY_RUN={dry_run}")

        print("   ✅ Environment configured")
        return {
            'status': 'ok',
            'message': 'Environment configured',
            'dry_run': dry_run
        }

    def _check_logs(self) -> Dict[str, Any]:
        """Check log directory and recent logs."""
        print("📝 Checking logs...")

        log_dir = self.project_root / 'logs'

        if not log_dir.exists():
            print("   ⚠️  Logs directory not found")
            return {
                'status': 'warning',
                'message': 'Logs directory missing',
                'suggestion': 'Create: mkdir logs'
            }

        # Check for recent logs
        log_files = list(log_dir.glob('*.log'))

        if not log_files:
            print("   ⚠️  No log files found")
            return {
                'status': 'warning',
                'message': 'No logs found (scheduler may not have run yet)'
            }

        # Check most recent log
        recent_log = max(log_files, key=lambda f: f.stat().st_mtime)
        age_seconds = datetime.now().timestamp() - recent_log.stat().st_mtime
        age_minutes = int(age_seconds / 60)

        print(f"   ✅ Found {len(log_files)} log files")
        print(f"   ℹ️  Most recent: {recent_log.name} ({age_minutes} minutes ago)")

        return {
            'status': 'ok',
            'message': f'{len(log_files)} log files found',
            'recent_log': recent_log.name,
            'age_minutes': age_minutes
        }

    def _check_permissions(self) -> Dict[str, Any]:
        """Check file permissions."""
        print("🔒 Checking permissions...")

        # Check if scripts are executable (Unix-like systems)
        if self.platform in ['Linux', 'Darwin']:
            script_files = [
                'scripts/scheduler_setup.sh',
                'scripts/setup_macos_scheduler.sh'
            ]

            non_executable = []
            for script in script_files:
                script_path = self.project_root / script
                if script_path.exists() and not os.access(script_path, os.X_OK):
                    non_executable.append(script)

            if non_executable:
                print(f"   ⚠️  {len(non_executable)} scripts not executable")
                return {
                    'status': 'warning',
                    'message': f'{len(non_executable)} scripts need chmod +x',
                    'files': non_executable
                }

        print("   ✅ Permissions OK")
        return {
            'status': 'ok',
            'message': 'Permissions configured correctly'
        }

    def _print_results(self, results: Dict[str, Any]) -> None:
        """Print validation results summary."""
        print()
        print("=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'passed': '✅',
            'warning': '⚠️',
            'failed': '❌'
        }.get(results['status'], '❓')

        print(f"Overall Status: {status_emoji} {results['status'].upper()}")
        print(f"Platform: {results['platform']}")
        print()

        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  ❌ {error}")
            print()

        if results['warnings']:
            print("Warnings:")
            for warning in results['warnings']:
                print(f"  ⚠️  {warning}")
            print()

        print("Checks:")
        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            message = check_result.get('message', 'No details')
            emoji = {'ok': '✅', 'warning': '⚠️', 'error': '❌'}.get(status, '❓')
            print(f"  {emoji} {check_name}: {message}")

            if check_result.get('suggestion'):
                print(f"     💡 {check_result['suggestion']}")

        print()


if __name__ == '__main__':
    validator = SchedulerValidator()
    results = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if results['status'] == 'passed' else 1)
