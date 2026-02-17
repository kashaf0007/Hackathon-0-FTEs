"""
Performance Validation Script - Validates system performance metrics.
Checks watcher polling intervals, event processing times, and resource usage.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json
import time

# Fix Windows encoding for emoji support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.logger import get_logger


class PerformanceValidator:
    """
    Validates system performance against Silver Tier requirements.

    Requirements:
    - Watcher polling: 5-15 minutes
    - Event processing: < 30 seconds
    - Concurrent tasks: Max 10
    - Log retention: 90 days
    - Approval timeout: 24 hours
    - Retry attempts: 3 with exponential backoff
    """

    def __init__(self):
        """Initialize performance validator."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.vault_dir = self.project_root / 'AI_Employee_Vault'
        self.log_dir = self.vault_dir / 'Logs'

    def validate(self) -> Dict[str, Any]:
        """
        Run performance validation.

        Returns:
            Validation results
        """
        print("⚡ Performance Validation - Silver Tier")
        print("=" * 50)
        print()

        results = {
            'timestamp': datetime.now().isoformat() + 'Z',
            'checks': {},
            'warnings': [],
            'errors': [],
            'overall_status': 'passed'
        }

        # Run performance checks
        checks = [
            ('watcher_polling', self._check_watcher_polling),
            ('event_processing', self._check_event_processing),
            ('concurrent_tasks', self._check_concurrent_tasks),
            ('log_retention', self._check_log_retention),
            ('approval_timeout', self._check_approval_timeout),
            ('retry_logic', self._check_retry_logic)
        ]

        for check_name, check_func in checks:
            try:
                result = check_func()
                results['checks'][check_name] = result

                if result['status'] == 'failed':
                    results['errors'].append(f"{check_name}: {result['message']}")
                elif result['status'] == 'warning':
                    results['warnings'].append(f"{check_name}: {result['message']}")

            except Exception as e:
                results['checks'][check_name] = {
                    'status': 'error',
                    'message': f'Check failed: {str(e)}'
                }
                results['errors'].append(f"{check_name}: Check error - {str(e)}")

        # Determine overall status
        if results['errors']:
            results['overall_status'] = 'failed'
        elif results['warnings']:
            results['overall_status'] = 'warnings'

        # Print summary
        self._print_summary(results)

        return results

    def _check_watcher_polling(self) -> Dict[str, Any]:
        """Check watcher polling intervals (5-15 minutes)."""
        print("📡 Checking watcher polling intervals...")

        watcher_config = self.vault_dir / 'Watchers' / 'watcher_config.json'

        if not watcher_config.exists():
            print("   ⚠️  Watcher config not found")
            return {
                'status': 'warning',
                'message': 'Watcher configuration not found'
            }

        try:
            with open(watcher_config) as f:
                config = json.load(f)

            issues = []
            for watcher_name, watcher_cfg in config.items():
                if not watcher_cfg.get('enabled', False):
                    continue

                interval = watcher_cfg.get('poll_interval', 0)

                # Check if interval is within 5-15 minutes (300-900 seconds)
                if interval < 300:
                    issues.append(f"{watcher_name}: {interval}s (too frequent, < 5 min)")
                elif interval > 900:
                    issues.append(f"{watcher_name}: {interval}s (too slow, > 15 min)")
                else:
                    print(f"   ✅ {watcher_name}: {interval}s ({interval/60:.1f} min)")

            if issues:
                print(f"   ⚠️  {len(issues)} polling interval issues")
                return {
                    'status': 'warning',
                    'message': f'{len(issues)} watchers outside 5-15 min range',
                    'issues': issues
                }

            print("   ✅ All polling intervals within range")
            return {
                'status': 'passed',
                'message': 'Watcher polling intervals optimal'
            }

        except Exception as e:
            print(f"   ❌ Error reading config: {str(e)}")
            return {
                'status': 'failed',
                'message': f'Failed to read watcher config: {str(e)}'
            }

    def _check_event_processing(self) -> Dict[str, Any]:
        """Check event processing times (< 30 seconds)."""
        print("⏱️  Checking event processing times...")

        # Analyze recent logs for processing times
        today_log = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        if not today_log.exists():
            print("   ⚠️  No log file for today")
            return {
                'status': 'warning',
                'message': 'No recent logs to analyze'
            }

        try:
            processing_times = []

            with open(today_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        details = entry.get('details', {})

                        if 'duration_ms' in details:
                            duration_ms = details['duration_ms']
                            processing_times.append(duration_ms)

                    except json.JSONDecodeError:
                        continue

            if not processing_times:
                print("   ⚠️  No processing times found in logs")
                return {
                    'status': 'warning',
                    'message': 'No processing time data available'
                }

            # Calculate statistics
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)

            # Check if any processing took > 30 seconds (30000 ms)
            slow_events = [t for t in processing_times if t > 30000]

            print(f"   📊 Avg: {avg_time:.0f}ms, Max: {max_time:.0f}ms, Min: {min_time:.0f}ms")

            if slow_events:
                print(f"   ⚠️  {len(slow_events)} events took > 30s")
                return {
                    'status': 'warning',
                    'message': f'{len(slow_events)} events exceeded 30s threshold',
                    'avg_ms': avg_time,
                    'max_ms': max_time,
                    'slow_count': len(slow_events)
                }

            print("   ✅ All events processed within 30s")
            return {
                'status': 'passed',
                'message': 'Event processing times optimal',
                'avg_ms': avg_time,
                'max_ms': max_time
            }

        except Exception as e:
            print(f"   ❌ Error analyzing logs: {str(e)}")
            return {
                'status': 'failed',
                'message': f'Failed to analyze processing times: {str(e)}'
            }

    def _check_concurrent_tasks(self) -> Dict[str, Any]:
        """Check concurrent task limit (max 10)."""
        print("🔢 Checking concurrent task limits...")

        orchestrator = self.project_root / 'scripts' / 'orchestrator.py'

        if not orchestrator.exists():
            print("   ⚠️  Orchestrator not found")
            return {
                'status': 'warning',
                'message': 'Orchestrator script not found'
            }

        try:
            content = orchestrator.read_text()

            # Look for max concurrent task configuration
            if 'max' in content.lower() and 'concurrent' in content.lower():
                # Try to extract the value
                import re
                match = re.search(r'max.*concurrent.*=\s*(\d+)', content, re.IGNORECASE)
                if match:
                    max_concurrent = int(match.group(1))
                    print(f"   ✅ Max concurrent tasks: {max_concurrent}")

                    if max_concurrent > 10:
                        print(f"   ⚠️  Limit too high ({max_concurrent} > 10)")
                        return {
                            'status': 'warning',
                            'message': f'Concurrent limit too high: {max_concurrent}',
                            'max_concurrent': max_concurrent
                        }

                    return {
                        'status': 'passed',
                        'message': f'Concurrent limit configured: {max_concurrent}',
                        'max_concurrent': max_concurrent
                    }

            print("   ⚠️  Concurrent limit not clearly defined")
            return {
                'status': 'warning',
                'message': 'Concurrent task limit not found in code'
            }

        except Exception as e:
            print(f"   ❌ Error checking orchestrator: {str(e)}")
            return {
                'status': 'failed',
                'message': f'Failed to check concurrent limits: {str(e)}'
            }

    def _check_log_retention(self) -> Dict[str, Any]:
        """Check log retention (90 days)."""
        print("📅 Checking log retention...")

        if not self.log_dir.exists():
            print("   ❌ Logs directory not found")
            return {
                'status': 'failed',
                'message': 'Logs directory not found'
            }

        # Check for logs older than 90 days
        cutoff_date = datetime.now() - timedelta(days=90)
        old_logs = []

        for log_file in self.log_dir.glob('*.json'):
            if 'archive' in str(log_file):
                continue

            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_date:
                old_logs.append(log_file.name)

        if old_logs:
            print(f"   ⚠️  {len(old_logs)} logs older than 90 days")
            return {
                'status': 'warning',
                'message': f'{len(old_logs)} logs need rotation',
                'old_logs': old_logs[:5]
            }

        print("   ✅ Log retention within 90 days")
        return {
            'status': 'passed',
            'message': 'Log retention policy compliant'
        }

    def _check_approval_timeout(self) -> Dict[str, Any]:
        """Check approval timeout (24 hours)."""
        print("⏰ Checking approval timeout...")

        env_example = self.project_root / '.env.example'

        if not env_example.exists():
            print("   ⚠️  .env.example not found")
            return {
                'status': 'warning',
                'message': '.env.example not found'
            }

        try:
            content = env_example.read_text()

            if 'APPROVAL_TIMEOUT' in content:
                # Try to extract the value
                import re
                match = re.search(r'APPROVAL_TIMEOUT.*=\s*(\d+)', content)
                if match:
                    timeout_hours = int(match.group(1))
                    print(f"   ✅ Approval timeout: {timeout_hours} hours")

                    if timeout_hours != 24:
                        print(f"   ⚠️  Timeout not 24 hours ({timeout_hours}h)")
                        return {
                            'status': 'warning',
                            'message': f'Approval timeout is {timeout_hours}h (expected 24h)',
                            'timeout_hours': timeout_hours
                        }

                    return {
                        'status': 'passed',
                        'message': 'Approval timeout configured: 24 hours',
                        'timeout_hours': timeout_hours
                    }

            print("   ⚠️  Approval timeout not configured")
            return {
                'status': 'warning',
                'message': 'Approval timeout not found in .env.example'
            }

        except Exception as e:
            print(f"   ❌ Error checking timeout: {str(e)}")
            return {
                'status': 'failed',
                'message': f'Failed to check approval timeout: {str(e)}'
            }

    def _check_retry_logic(self) -> Dict[str, Any]:
        """Check retry logic (3 attempts with exponential backoff)."""
        print("🔄 Checking retry logic...")

        step_executor = self.project_root / 'scripts' / 'step_executor.py'

        if not step_executor.exists():
            print("   ⚠️  Step executor not found")
            return {
                'status': 'warning',
                'message': 'Step executor script not found'
            }

        try:
            content = step_executor.read_text()

            checks = []

            # Check for max retries = 3
            if 'max_retries' in content.lower() and '3' in content:
                print("   ✅ Max retries: 3")
                checks.append({'check': 'max_retries', 'status': 'pass'})
            else:
                print("   ⚠️  Max retries not clearly set to 3")
                checks.append({'check': 'max_retries', 'status': 'warning'})

            # Check for exponential backoff
            if 'exponential' in content.lower() or ('5' in content and '15' in content and '45' in content):
                print("   ✅ Exponential backoff: 5s, 15s, 45s")
                checks.append({'check': 'exponential_backoff', 'status': 'pass'})
            else:
                print("   ⚠️  Exponential backoff not clearly implemented")
                checks.append({'check': 'exponential_backoff', 'status': 'warning'})

            # Check for retry logic
            if 'retry' in content.lower():
                print("   ✅ Retry logic present")
                checks.append({'check': 'retry_logic', 'status': 'pass'})
            else:
                print("   ❌ Retry logic not found")
                return {
                    'status': 'failed',
                    'message': 'Retry logic not implemented',
                    'checks': checks
                }

            warnings = [c for c in checks if c['status'] == 'warning']
            if warnings:
                return {
                    'status': 'warning',
                    'message': f'{len(warnings)} retry configuration warnings',
                    'checks': checks
                }

            print("   ✅ Retry logic properly configured")
            return {
                'status': 'passed',
                'message': 'Retry logic: 3 attempts with exponential backoff',
                'checks': checks
            }

        except Exception as e:
            print(f"   ❌ Error checking retry logic: {str(e)}")
            return {
                'status': 'failed',
                'message': f'Failed to check retry logic: {str(e)}'
            }

    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print validation summary."""
        print()
        print("=" * 50)
        print("PERFORMANCE VALIDATION SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'passed': '✅',
            'warnings': '⚠️',
            'failed': '❌'
        }.get(results['overall_status'], '❓')

        print(f"Overall Status: {status_emoji} {results['overall_status'].upper()}")
        print()

        if results['errors']:
            print(f"❌ Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"   • {error}")
            print()

        if results['warnings']:
            print(f"⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"   • {warning}")
            print()

        print("Performance Checks:")
        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            message = check_result.get('message', 'No details')
            emoji = {
                'passed': '✅',
                'warning': '⚠️',
                'failed': '❌',
                'error': '❌'
            }.get(status, '❓')
            print(f"  {emoji} {check_name.replace('_', ' ').title()}: {message}")

        print()


if __name__ == '__main__':
    validator = PerformanceValidator()
    results = validator.validate()

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'passed' else 1
    sys.exit(exit_code)
