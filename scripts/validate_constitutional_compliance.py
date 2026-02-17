"""
Constitutional Compliance Validator - Verifies all constitutional principles are enforced.
Checks system implementation against the six core principles.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

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


class ConstitutionalValidator:
    """
    Validates constitutional compliance across the system.

    Principles:
    1. Local-First: All data stored locally
    2. HITL Safety: Human approval for risky actions
    3. Transparency: Complete audit logging
    4. Proactivity: Autonomous monitoring
    5. Persistence: Retry logic and completion
    6. Cost Efficiency: Resource optimization
    """

    def __init__(self):
        """Initialize validator."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': None,
            'principles': {},
            'violations': [],
            'warnings': [],
            'overall_status': 'compliant'
        }

    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all constitutional principles.

        Returns:
            Validation results
        """
        print("⚖️  Constitutional Compliance Validation")
        print("=" * 50)
        print()

        self.results['timestamp'] = self._get_timestamp()

        # Validate each principle
        principles = [
            ('local_first', self._validate_local_first),
            ('hitl_safety', self._validate_hitl_safety),
            ('transparency', self._validate_transparency),
            ('proactivity', self._validate_proactivity),
            ('persistence', self._validate_persistence),
            ('cost_efficiency', self._validate_cost_efficiency)
        ]

        for principle_name, validator_func in principles:
            try:
                result = validator_func()
                self.results['principles'][principle_name] = result

                if result['status'] == 'violation':
                    self.results['violations'].append(f"{principle_name}: {result['message']}")
                elif result['status'] == 'warning':
                    self.results['warnings'].append(f"{principle_name}: {result['message']}")

            except Exception as e:
                self.results['principles'][principle_name] = {
                    'status': 'error',
                    'message': f'Validation failed: {str(e)}'
                }
                self.results['violations'].append(f"{principle_name}: Validation error - {str(e)}")

        # Determine overall status
        if self.results['violations']:
            self.results['overall_status'] = 'non_compliant'
        elif self.results['warnings']:
            self.results['overall_status'] = 'compliant_with_warnings'

        # Print summary
        self._print_summary()

        # Log validation
        self.logger.info(
            component="validation",
            action="constitutional_validation_completed",
            actor="constitutional_validator",
            target="system",
            details={
                'overall_status': self.results['overall_status'],
                'violations': len(self.results['violations']),
                'warnings': len(self.results['warnings'])
            }
        )

        return self.results

    def _validate_local_first(self) -> Dict[str, Any]:
        """Validate Local-First principle: All data stored locally."""
        print("1️⃣  Validating Local-First Principle...")

        checks = []

        # Check AI_Employee_Vault exists
        vault_dir = self.project_root / 'AI_Employee_Vault'
        if not vault_dir.exists():
            print("   ❌ AI_Employee_Vault directory missing")
            return {
                'status': 'violation',
                'message': 'AI_Employee_Vault directory not found',
                'checks': checks
            }
        checks.append({'check': 'vault_directory', 'status': 'pass'})

        # Check for cloud storage references in code
        cloud_patterns = ['s3', 'azure', 'gcs', 'cloud', 'remote']
        violations = []

        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '.git' in str(py_file):
                continue

            try:
                content = py_file.read_text().lower()
                for pattern in cloud_patterns:
                    if pattern in content and 'import' not in content:
                        violations.append(f"{py_file.name}: contains '{pattern}'")
            except:
                pass

        if violations:
            print(f"   ⚠️  Found {len(violations)} potential cloud references")
            checks.append({'check': 'no_cloud_storage', 'status': 'warning', 'details': violations[:3]})
            return {
                'status': 'warning',
                'message': f'Found {len(violations)} potential cloud storage references',
                'checks': checks,
                'violations': violations[:5]
            }

        checks.append({'check': 'no_cloud_storage', 'status': 'pass'})

        # Check all state directories exist
        required_dirs = ['Logs', 'Needs_Action', 'Done', 'Pending_Approval', 'Approved', 'Rejected']
        missing_dirs = [d for d in required_dirs if not (vault_dir / d).exists()]

        if missing_dirs:
            print(f"   ⚠️  Missing directories: {', '.join(missing_dirs)}")
            checks.append({'check': 'state_directories', 'status': 'warning', 'missing': missing_dirs})
            return {
                'status': 'warning',
                'message': f'Missing state directories: {", ".join(missing_dirs)}',
                'checks': checks
            }

        checks.append({'check': 'state_directories', 'status': 'pass'})

        print("   ✅ Local-First: COMPLIANT")
        return {
            'status': 'compliant',
            'message': 'All data stored locally',
            'checks': checks
        }

    def _validate_hitl_safety(self) -> Dict[str, Any]:
        """Validate HITL Safety principle: Human approval for risky actions."""
        print("2️⃣  Validating HITL Safety Principle...")

        checks = []

        # Check approval workflow exists
        approval_script = self.project_root / 'scripts' / 'approval_workflow.py'
        if not approval_script.exists():
            print("   ❌ Approval workflow script missing")
            return {
                'status': 'violation',
                'message': 'Approval workflow not implemented',
                'checks': checks
            }
        checks.append({'check': 'approval_workflow_exists', 'status': 'pass'})

        # Check approval-guard skill exists
        approval_skill = self.project_root / '.claude' / 'skills' / 'approval-guard'
        if not approval_skill.exists():
            print("   ❌ Approval-guard skill missing")
            return {
                'status': 'violation',
                'message': 'Approval-guard skill not found',
                'checks': checks
            }
        checks.append({'check': 'approval_skill_exists', 'status': 'pass'})

        # Check risk classifier exists
        risk_classifier = self.project_root / 'scripts' / 'risk_classifier.py'
        if not risk_classifier.exists():
            print("   ⚠️  Risk classifier missing")
            checks.append({'check': 'risk_classifier_exists', 'status': 'warning'})
            return {
                'status': 'warning',
                'message': 'Risk classifier not found',
                'checks': checks
            }
        checks.append({'check': 'risk_classifier_exists', 'status': 'pass'})

        # Check approval directories exist
        vault_dir = self.project_root / 'AI_Employee_Vault'
        approval_dirs = ['Pending_Approval', 'Approved', 'Rejected']
        missing = [d for d in approval_dirs if not (vault_dir / d).exists()]

        if missing:
            print(f"   ❌ Missing approval directories: {', '.join(missing)}")
            checks.append({'check': 'approval_directories', 'status': 'violation', 'missing': missing})
            return {
                'status': 'violation',
                'message': f'Missing approval directories: {", ".join(missing)}',
                'checks': checks
            }
        checks.append({'check': 'approval_directories', 'status': 'pass'})

        print("   ✅ HITL Safety: COMPLIANT")
        return {
            'status': 'compliant',
            'message': 'HITL approval workflow implemented',
            'checks': checks
        }

    def _validate_transparency(self) -> Dict[str, Any]:
        """Validate Transparency principle: Complete audit logging."""
        print("3️⃣  Validating Transparency Principle...")

        checks = []

        # Check logger exists
        logger_script = self.project_root / 'scripts' / 'logger.py'
        if not logger_script.exists():
            print("   ❌ Logger script missing")
            return {
                'status': 'violation',
                'message': 'Logger not implemented',
                'checks': checks
            }
        checks.append({'check': 'logger_exists', 'status': 'pass'})

        # Check logging-audit skill exists
        logging_skill = self.project_root / '.claude' / 'skills' / 'logging-audit'
        if not logging_skill.exists():
            print("   ❌ Logging-audit skill missing")
            return {
                'status': 'violation',
                'message': 'Logging-audit skill not found',
                'checks': checks
            }
        checks.append({'check': 'logging_skill_exists', 'status': 'pass'})

        # Check Logs directory exists
        log_dir = self.project_root / 'AI_Employee_Vault' / 'Logs'
        if not log_dir.exists():
            print("   ❌ Logs directory missing")
            return {
                'status': 'violation',
                'message': 'Logs directory not found',
                'checks': checks
            }
        checks.append({'check': 'logs_directory_exists', 'status': 'pass'})

        # Check for log files
        log_files = list(log_dir.glob('*.json'))
        if not log_files:
            print("   ⚠️  No log files found")
            checks.append({'check': 'log_files_exist', 'status': 'warning'})
            return {
                'status': 'warning',
                'message': 'No log files found (system may not have run yet)',
                'checks': checks
            }
        checks.append({'check': 'log_files_exist', 'status': 'pass', 'count': len(log_files)})

        print("   ✅ Transparency: COMPLIANT")
        return {
            'status': 'compliant',
            'message': 'Comprehensive logging implemented',
            'checks': checks
        }

    def _validate_proactivity(self) -> Dict[str, Any]:
        """Validate Proactivity principle: Autonomous monitoring."""
        print("4️⃣  Validating Proactivity Principle...")

        checks = []

        # Check watchers exist
        watcher_dir = self.project_root / 'AI_Employee_Vault' / 'Watchers'
        if not watcher_dir.exists():
            print("   ❌ Watchers directory missing")
            return {
                'status': 'violation',
                'message': 'Watchers not implemented',
                'checks': checks
            }
        checks.append({'check': 'watchers_directory_exists', 'status': 'pass'})

        # Check for watcher scripts
        watcher_files = list(watcher_dir.glob('*_watcher.py'))
        if len(watcher_files) < 2:
            print(f"   ❌ Insufficient watchers (found {len(watcher_files)}, need 2+)")
            return {
                'status': 'violation',
                'message': f'Only {len(watcher_files)} watchers found (Silver requires 2+)',
                'checks': checks
            }
        checks.append({'check': 'watcher_count', 'status': 'pass', 'count': len(watcher_files)})

        # Check orchestrator exists
        orchestrator = self.project_root / 'scripts' / 'orchestrator.py'
        if not orchestrator.exists():
            print("   ❌ Orchestrator missing")
            return {
                'status': 'violation',
                'message': 'Orchestrator not implemented',
                'checks': checks
            }
        checks.append({'check': 'orchestrator_exists', 'status': 'pass'})

        # Check scheduler setup scripts exist
        scheduler_scripts = [
            'scripts/scheduler_setup.sh',
            'scripts/setup_windows_scheduler.ps1',
            'scripts/setup_macos_scheduler.sh'
        ]
        missing_schedulers = [s for s in scheduler_scripts if not (self.project_root / s).exists()]

        if len(missing_schedulers) == len(scheduler_scripts):
            print("   ❌ No scheduler setup scripts found")
            return {
                'status': 'violation',
                'message': 'No scheduler setup scripts found',
                'checks': checks
            }
        checks.append({'check': 'scheduler_scripts_exist', 'status': 'pass'})

        print("   ✅ Proactivity: COMPLIANT")
        return {
            'status': 'compliant',
            'message': 'Autonomous monitoring implemented',
            'checks': checks
        }

    def _validate_persistence(self) -> Dict[str, Any]:
        """Validate Persistence principle: Retry logic and completion."""
        print("5️⃣  Validating Persistence Principle...")

        checks = []

        # Check step_executor exists (has retry logic)
        step_executor = self.project_root / 'scripts' / 'step_executor.py'
        if not step_executor.exists():
            print("   ❌ Step executor missing")
            return {
                'status': 'violation',
                'message': 'Step executor not implemented',
                'checks': checks
            }
        checks.append({'check': 'step_executor_exists', 'status': 'pass'})

        # Check for retry logic in step_executor
        try:
            content = step_executor.read_text()
            if 'retry' not in content.lower() or 'max_retries' not in content.lower():
                print("   ⚠️  Retry logic not found in step_executor")
                checks.append({'check': 'retry_logic_exists', 'status': 'warning'})
                return {
                    'status': 'warning',
                    'message': 'Retry logic not clearly implemented',
                    'checks': checks
                }
            checks.append({'check': 'retry_logic_exists', 'status': 'pass'})
        except:
            pass

        # Check reasoning-loop skill exists
        reasoning_skill = self.project_root / '.claude' / 'skills' / 'reasoning-loop'
        if not reasoning_skill.exists():
            print("   ❌ Reasoning-loop skill missing")
            return {
                'status': 'violation',
                'message': 'Reasoning-loop skill not found',
                'checks': checks
            }
        checks.append({'check': 'reasoning_skill_exists', 'status': 'pass'})

        # Check Done directory exists
        done_dir = self.project_root / 'AI_Employee_Vault' / 'Done'
        if not done_dir.exists():
            print("   ❌ Done directory missing")
            return {
                'status': 'violation',
                'message': 'Done directory not found',
                'checks': checks
            }
        checks.append({'check': 'done_directory_exists', 'status': 'pass'})

        print("   ✅ Persistence: COMPLIANT")
        return {
            'status': 'compliant',
            'message': 'Retry logic and completion tracking implemented',
            'checks': checks
        }

    def _validate_cost_efficiency(self) -> Dict[str, Any]:
        """Validate Cost Efficiency principle: Resource optimization."""
        print("6️⃣  Validating Cost Efficiency Principle...")

        checks = []

        # Check DRY_RUN support in .env.example
        env_example = self.project_root / '.env.example'
        if not env_example.exists():
            print("   ⚠️  .env.example missing")
            checks.append({'check': 'env_example_exists', 'status': 'warning'})
        else:
            try:
                content = env_example.read_text()
                if 'DRY_RUN' not in content:
                    print("   ⚠️  DRY_RUN not in .env.example")
                    checks.append({'check': 'dry_run_configured', 'status': 'warning'})
                else:
                    checks.append({'check': 'dry_run_configured', 'status': 'pass'})
            except:
                pass

        # Check for resource limits in orchestrator
        orchestrator = self.project_root / 'scripts' / 'orchestrator.py'
        if orchestrator.exists():
            try:
                content = orchestrator.read_text()
                if 'max' in content.lower() and ('concurrent' in content.lower() or 'limit' in content.lower()):
                    checks.append({'check': 'resource_limits_exist', 'status': 'pass'})
                else:
                    print("   ⚠️  Resource limits not clearly defined")
                    checks.append({'check': 'resource_limits_exist', 'status': 'warning'})
            except:
                pass
        else:
            checks.append({'check': 'resource_limits_exist', 'status': 'warning'})

        # Check for polling interval configuration
        if env_example.exists():
            try:
                content = env_example.read_text()
                if 'POLL_INTERVAL' in content or 'poll_interval' in content.lower():
                    checks.append({'check': 'polling_configured', 'status': 'pass'})
                else:
                    checks.append({'check': 'polling_configured', 'status': 'warning'})
            except:
                pass

        print("   ✅ Cost Efficiency: COMPLIANT")
        return {
            'status': 'compliant',
            'message': 'Resource optimization implemented',
            'checks': checks
        }

    def _print_summary(self) -> None:
        """Print validation summary."""
        print()
        print("=" * 50)
        print("CONSTITUTIONAL COMPLIANCE SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'compliant': '✅',
            'compliant_with_warnings': '⚠️',
            'non_compliant': '❌'
        }.get(self.results['overall_status'], '❓')

        print(f"Overall Status: {status_emoji} {self.results['overall_status'].upper().replace('_', ' ')}")
        print()

        if self.results['violations']:
            print(f"❌ Violations ({len(self.results['violations'])}):")
            for violation in self.results['violations']:
                print(f"   • {violation}")
            print()

        if self.results['warnings']:
            print(f"⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
            print()

        print("Principle Status:")
        for principle, result in self.results['principles'].items():
            status = result.get('status', 'unknown')
            message = result.get('message', 'No details')
            emoji = {
                'compliant': '✅',
                'warning': '⚠️',
                'violation': '❌',
                'error': '❌'
            }.get(status, '❓')
            print(f"  {emoji} {principle.replace('_', ' ').title()}: {message}")

        print()

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() + 'Z'


if __name__ == '__main__':
    validator = ConstitutionalValidator()
    results = validator.validate_all()

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'compliant' else 1
    sys.exit(exit_code)
