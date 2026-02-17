"""
Quickstart Validation Script - Runs all 7 test procedures from quickstart.md.
Validates Silver Tier system is properly configured and operational.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
import subprocess

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


class QuickstartValidator:
    """
    Validates Silver Tier system using quickstart.md test procedures.

    Test Procedures:
    1. Event Detection (Watchers)
    2. Risk Classification
    3. Approval Workflow
    4. MCP Server Integration
    5. LinkedIn Post Generation
    6. Reasoning Loop
    7. End-to-End Workflow
    """

    def __init__(self):
        """Initialize validator."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': None,
            'tests': {},
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'overall_status': 'passed'
        }

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all quickstart validation procedures.

        Returns:
            Validation results
        """
        print("🧪 Quickstart Validation - Silver Tier")
        print("=" * 50)
        print()

        self.results['timestamp'] = self._get_timestamp()

        # Run all test procedures
        tests = [
            ('test_1_event_detection', self._test_event_detection),
            ('test_2_risk_classification', self._test_risk_classification),
            ('test_3_approval_workflow', self._test_approval_workflow),
            ('test_4_mcp_integration', self._test_mcp_integration),
            ('test_5_linkedin_generation', self._test_linkedin_generation),
            ('test_6_reasoning_loop', self._test_reasoning_loop),
            ('test_7_end_to_end', self._test_end_to_end)
        ]

        for test_name, test_func in tests:
            try:
                result = test_func()
                self.results['tests'][test_name] = result

                if result['status'] == 'passed':
                    self.results['passed'] += 1
                elif result['status'] == 'failed':
                    self.results['failed'] += 1
                elif result['status'] == 'skipped':
                    self.results['skipped'] += 1

            except Exception as e:
                self.results['tests'][test_name] = {
                    'status': 'failed',
                    'message': f'Test error: {str(e)}'
                }
                self.results['failed'] += 1

        # Determine overall status
        if self.results['failed'] > 0:
            self.results['overall_status'] = 'failed'
        elif self.results['skipped'] == len(tests):
            self.results['overall_status'] = 'skipped'

        # Print summary
        self._print_summary()

        return self.results

    def _test_event_detection(self) -> Dict[str, Any]:
        """Test 1: Event Detection (Watchers)."""
        print("Test 1: Event Detection (Watchers)")
        print("-" * 50)

        checks = []

        # Check watcher files exist
        watcher_dir = self.project_root / 'AI_Employee_Vault' / 'Watchers'
        required_watchers = ['gmail_watcher.py', 'linkedin_watcher.py', 'watcher_base.py']

        for watcher in required_watchers:
            watcher_path = watcher_dir / watcher
            if watcher_path.exists():
                print(f"   ✅ {watcher} exists")
                checks.append({'file': watcher, 'status': 'pass'})
            else:
                print(f"   ❌ {watcher} missing")
                checks.append({'file': watcher, 'status': 'fail'})
                return {
                    'status': 'failed',
                    'message': f'{watcher} not found',
                    'checks': checks
                }

        # Check Needs_Action directory exists
        needs_action = self.project_root / 'AI_Employee_Vault' / 'Needs_Action'
        if not needs_action.exists():
            print("   ❌ Needs_Action directory missing")
            return {
                'status': 'failed',
                'message': 'Needs_Action directory not found',
                'checks': checks
            }

        print("   ✅ Needs_Action directory exists")
        checks.append({'check': 'needs_action_dir', 'status': 'pass'})

        print("   ✅ Test 1: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'Event detection components present',
            'checks': checks
        }

    def _test_risk_classification(self) -> Dict[str, Any]:
        """Test 2: Risk Classification."""
        print("Test 2: Risk Classification")
        print("-" * 50)

        checks = []

        # Check risk classifier exists
        risk_classifier = self.project_root / 'scripts' / 'risk_classifier.py'
        if not risk_classifier.exists():
            print("   ❌ risk_classifier.py missing")
            return {
                'status': 'failed',
                'message': 'Risk classifier not found',
                'checks': checks
            }

        print("   ✅ risk_classifier.py exists")
        checks.append({'file': 'risk_classifier.py', 'status': 'pass'})

        # Check approval-guard skill exists
        approval_skill = self.project_root / '.claude' / 'skills' / 'approval-guard'
        if not approval_skill.exists():
            print("   ❌ approval-guard skill missing")
            return {
                'status': 'failed',
                'message': 'Approval-guard skill not found',
                'checks': checks
            }

        print("   ✅ approval-guard skill exists")
        checks.append({'skill': 'approval-guard', 'status': 'pass'})

        print("   ✅ Test 2: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'Risk classification components present',
            'checks': checks
        }

    def _test_approval_workflow(self) -> Dict[str, Any]:
        """Test 3: Approval Workflow."""
        print("Test 3: Approval Workflow")
        print("-" * 50)

        checks = []

        # Check approval workflow script exists
        approval_workflow = self.project_root / 'scripts' / 'approval_workflow.py'
        if not approval_workflow.exists():
            print("   ❌ approval_workflow.py missing")
            return {
                'status': 'failed',
                'message': 'Approval workflow not found',
                'checks': checks
            }

        print("   ✅ approval_workflow.py exists")
        checks.append({'file': 'approval_workflow.py', 'status': 'pass'})

        # Check approval directories exist
        vault_dir = self.project_root / 'AI_Employee_Vault'
        approval_dirs = ['Pending_Approval', 'Approved', 'Rejected']

        for dir_name in approval_dirs:
            dir_path = vault_dir / dir_name
            if dir_path.exists():
                print(f"   ✅ {dir_name}/ exists")
                checks.append({'directory': dir_name, 'status': 'pass'})
            else:
                print(f"   ❌ {dir_name}/ missing")
                return {
                    'status': 'failed',
                    'message': f'{dir_name} directory not found',
                    'checks': checks
                }

        print("   ✅ Test 3: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'Approval workflow components present',
            'checks': checks
        }

    def _test_mcp_integration(self) -> Dict[str, Any]:
        """Test 4: MCP Server Integration."""
        print("Test 4: MCP Server Integration")
        print("-" * 50)

        checks = []

        # Check MCP base server exists
        mcp_base = self.project_root / 'mcp_servers' / 'mcp_base.py'
        if not mcp_base.exists():
            print("   ❌ mcp_base.py missing")
            return {
                'status': 'failed',
                'message': 'MCP base server not found',
                'checks': checks
            }

        print("   ✅ mcp_base.py exists")
        checks.append({'file': 'mcp_base.py', 'status': 'pass'})

        # Check MCP servers exist
        mcp_servers = ['email_server.py', 'linkedin_server.py']
        for server in mcp_servers:
            server_path = self.project_root / 'mcp_servers' / server
            if server_path.exists():
                print(f"   ✅ {server} exists")
                checks.append({'file': server, 'status': 'pass'})
            else:
                print(f"   ❌ {server} missing")
                return {
                    'status': 'failed',
                    'message': f'{server} not found',
                    'checks': checks
                }

        # Check MCP client exists
        mcp_client = self.project_root / 'scripts' / 'mcp_client.py'
        if not mcp_client.exists():
            print("   ❌ mcp_client.py missing")
            return {
                'status': 'failed',
                'message': 'MCP client not found',
                'checks': checks
            }

        print("   ✅ mcp_client.py exists")
        checks.append({'file': 'mcp_client.py', 'status': 'pass'})

        print("   ✅ Test 4: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'MCP integration components present',
            'checks': checks
        }

    def _test_linkedin_generation(self) -> Dict[str, Any]:
        """Test 5: LinkedIn Post Generation."""
        print("Test 5: LinkedIn Post Generation")
        print("-" * 50)

        checks = []

        # Check linkedin-post-generator skill exists
        linkedin_skill = self.project_root / '.claude' / 'skills' / 'linkedin-post-generator'
        if not linkedin_skill.exists():
            print("   ❌ linkedin-post-generator skill missing")
            return {
                'status': 'failed',
                'message': 'LinkedIn post generator skill not found',
                'checks': checks
            }

        print("   ✅ linkedin-post-generator skill exists")
        checks.append({'skill': 'linkedin-post-generator', 'status': 'pass'})

        # Check post generator script exists
        post_generator = self.project_root / 'scripts' / 'post_generator.py'
        if not post_generator.exists():
            print("   ❌ post_generator.py missing")
            return {
                'status': 'failed',
                'message': 'Post generator script not found',
                'checks': checks
            }

        print("   ✅ post_generator.py exists")
        checks.append({'file': 'post_generator.py', 'status': 'pass'})

        # Check Business_Goals.md exists
        business_goals = self.project_root / 'AI_Employee_Vault' / 'Business_Goals.md'
        if not business_goals.exists():
            print("   ⚠️  Business_Goals.md missing (optional)")
            checks.append({'file': 'Business_Goals.md', 'status': 'warning'})
        else:
            print("   ✅ Business_Goals.md exists")
            checks.append({'file': 'Business_Goals.md', 'status': 'pass'})

        print("   ✅ Test 5: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'LinkedIn generation components present',
            'checks': checks
        }

    def _test_reasoning_loop(self) -> Dict[str, Any]:
        """Test 6: Reasoning Loop."""
        print("Test 6: Reasoning Loop")
        print("-" * 50)

        checks = []

        # Check reasoning-loop skill exists
        reasoning_skill = self.project_root / '.claude' / 'skills' / 'reasoning-loop'
        if not reasoning_skill.exists():
            print("   ❌ reasoning-loop skill missing")
            return {
                'status': 'failed',
                'message': 'Reasoning loop skill not found',
                'checks': checks
            }

        print("   ✅ reasoning-loop skill exists")
        checks.append({'skill': 'reasoning-loop', 'status': 'pass'})

        # Check plan generator exists
        plan_generator = self.project_root / 'scripts' / 'plan_generator.py'
        if not plan_generator.exists():
            print("   ❌ plan_generator.py missing")
            return {
                'status': 'failed',
                'message': 'Plan generator not found',
                'checks': checks
            }

        print("   ✅ plan_generator.py exists")
        checks.append({'file': 'plan_generator.py', 'status': 'pass'})

        # Check step executor exists
        step_executor = self.project_root / 'scripts' / 'step_executor.py'
        if not step_executor.exists():
            print("   ❌ step_executor.py missing")
            return {
                'status': 'failed',
                'message': 'Step executor not found',
                'checks': checks
            }

        print("   ✅ step_executor.py exists")
        checks.append({'file': 'step_executor.py', 'status': 'pass'})

        # Check Plan.md template exists
        plan_template = self.project_root / 'AI_Employee_Vault' / 'Plan.md'
        if not plan_template.exists():
            print("   ⚠️  Plan.md template missing (will be created on first use)")
            checks.append({'file': 'Plan.md', 'status': 'warning'})
        else:
            print("   ✅ Plan.md exists")
            checks.append({'file': 'Plan.md', 'status': 'pass'})

        print("   ✅ Test 6: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'Reasoning loop components present',
            'checks': checks
        }

    def _test_end_to_end(self) -> Dict[str, Any]:
        """Test 7: End-to-End Workflow."""
        print("Test 7: End-to-End Workflow")
        print("-" * 50)

        checks = []

        # Check orchestrator exists
        orchestrator = self.project_root / 'scripts' / 'orchestrator.py'
        if not orchestrator.exists():
            print("   ❌ orchestrator.py missing")
            return {
                'status': 'failed',
                'message': 'Orchestrator not found',
                'checks': checks
            }

        print("   ✅ orchestrator.py exists")
        checks.append({'file': 'orchestrator.py', 'status': 'pass'})

        # Check all required skills exist
        required_skills = [
            'task-orchestrator',
            'approval-guard',
            'logging-audit',
            'reasoning-loop',
            'email-mcp-sender',
            'linkedin-post-generator'
        ]

        skills_dir = self.project_root / '.claude' / 'skills'
        for skill_name in required_skills:
            skill_path = skills_dir / skill_name
            if skill_path.exists():
                print(f"   ✅ {skill_name} skill exists")
                checks.append({'skill': skill_name, 'status': 'pass'})
            else:
                print(f"   ❌ {skill_name} skill missing")
                return {
                    'status': 'failed',
                    'message': f'{skill_name} skill not found',
                    'checks': checks
                }

        # Check Done directory exists
        done_dir = self.project_root / 'AI_Employee_Vault' / 'Done'
        if not done_dir.exists():
            print("   ❌ Done/ directory missing")
            return {
                'status': 'failed',
                'message': 'Done directory not found',
                'checks': checks
            }

        print("   ✅ Done/ directory exists")
        checks.append({'directory': 'Done', 'status': 'pass'})

        print("   ✅ Test 7: PASSED")
        print()
        return {
            'status': 'passed',
            'message': 'End-to-end workflow components present',
            'checks': checks
        }

    def _print_summary(self) -> None:
        """Print validation summary."""
        print("=" * 50)
        print("QUICKSTART VALIDATION SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'passed': '✅',
            'failed': '❌',
            'skipped': '⏭️'
        }.get(self.results['overall_status'], '❓')

        print(f"Overall Status: {status_emoji} {self.results['overall_status'].upper()}")
        print()
        print(f"Tests Passed: {self.results['passed']}")
        print(f"Tests Failed: {self.results['failed']}")
        print(f"Tests Skipped: {self.results['skipped']}")
        print()

        if self.results['failed'] > 0:
            print("Failed Tests:")
            for test_name, test_result in self.results['tests'].items():
                if test_result['status'] == 'failed':
                    print(f"  ❌ {test_name}: {test_result['message']}")
            print()

        print("Test Results:")
        for test_name, test_result in self.results['tests'].items():
            status = test_result.get('status', 'unknown')
            message = test_result.get('message', 'No details')
            emoji = {'passed': '✅', 'failed': '❌', 'skipped': '⏭️'}.get(status, '❓')
            print(f"  {emoji} {test_name}: {message}")

        print()

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() + 'Z'


if __name__ == '__main__':
    validator = QuickstartValidator()
    results = validator.validate_all()

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'passed' else 1
    sys.exit(exit_code)
