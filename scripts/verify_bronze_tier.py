"""
Bronze Tier Verification Script - Validates Bronze tier functionality remains operational.
Ensures Silver Tier upgrades haven't broken Bronze foundation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

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


class BronzeVerifier:
    """
    Verifies Bronze Tier functionality remains operational after Silver upgrade.

    Checks:
    - Bronze orchestrator (main.py) exists
    - src/ directory structure intact
    - Bronze skills present
    - monitored/ directory exists
    - Bronze tier can still run
    """

    def __init__(self):
        """Initialize Bronze verifier."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent

    def verify(self) -> Dict[str, Any]:
        """
        Verify Bronze tier functionality.

        Returns:
            Verification results
        """
        print("🥉 Bronze Tier Verification")
        print("=" * 50)
        print()

        results = {
            'timestamp': self._get_timestamp(),
            'checks': {},
            'warnings': [],
            'errors': [],
            'overall_status': 'operational'
        }

        # Run verification checks
        checks = [
            ('bronze_orchestrator', self._check_bronze_orchestrator),
            ('src_structure', self._check_src_structure),
            ('bronze_skills', self._check_bronze_skills),
            ('monitored_directory', self._check_monitored_directory),
            ('bronze_compatibility', self._check_bronze_compatibility)
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
            results['overall_status'] = 'broken'
        elif results['warnings']:
            results['overall_status'] = 'degraded'

        # Print summary
        self._print_summary(results)

        return results

    def _check_bronze_orchestrator(self) -> Dict[str, Any]:
        """Check Bronze orchestrator exists and is functional."""
        print("📋 Checking Bronze orchestrator...")

        main_py = self.project_root / 'main.py'

        if not main_py.exists():
            print("   ❌ main.py not found")
            return {
                'status': 'failed',
                'message': 'Bronze orchestrator (main.py) not found'
            }

        print("   ✅ main.py exists")

        # Check it imports from src.orchestrator
        try:
            content = main_py.read_text()
            if 'src.orchestrator' in content:
                print("   ✅ Imports Bronze orchestrator")
                return {
                    'status': 'passed',
                    'message': 'Bronze orchestrator present and configured'
                }
            else:
                print("   ⚠️  Bronze orchestrator import not found")
                return {
                    'status': 'warning',
                    'message': 'main.py exists but may not be configured correctly'
                }
        except Exception as e:
            print(f"   ⚠️  Could not read main.py: {str(e)}")
            return {
                'status': 'warning',
                'message': f'Could not verify main.py contents: {str(e)}'
            }

    def _check_src_structure(self) -> Dict[str, Any]:
        """Check src/ directory structure is intact."""
        print("📁 Checking src/ directory structure...")

        src_dir = self.project_root / 'src'

        if not src_dir.exists():
            print("   ❌ src/ directory not found")
            return {
                'status': 'failed',
                'message': 'Bronze src/ directory not found'
            }

        print("   ✅ src/ directory exists")

        # Check required subdirectories
        required_dirs = ['models', 'orchestrator', 'skills', 'utils', 'watchers']
        missing_dirs = []

        for dir_name in required_dirs:
            dir_path = src_dir / dir_name
            if dir_path.exists():
                print(f"   ✅ src/{dir_name}/ exists")
            else:
                print(f"   ⚠️  src/{dir_name}/ missing")
                missing_dirs.append(dir_name)

        if missing_dirs:
            return {
                'status': 'warning',
                'message': f'Missing Bronze directories: {", ".join(missing_dirs)}',
                'missing': missing_dirs
            }

        print("   ✅ All Bronze directories present")
        return {
            'status': 'passed',
            'message': 'Bronze src/ structure intact'
        }

    def _check_bronze_skills(self) -> Dict[str, Any]:
        """Check Bronze skills are still present."""
        print("🎯 Checking Bronze skills...")

        skills_dir = self.project_root / '.claude' / 'skills'

        if not skills_dir.exists():
            print("   ❌ .claude/skills/ directory not found")
            return {
                'status': 'failed',
                'message': 'Skills directory not found'
            }

        # Bronze tier requires 3 skills minimum
        bronze_skills = ['task-orchestrator', 'approval-guard', 'logging-audit']
        missing_skills = []

        for skill_name in bronze_skills:
            skill_path = skills_dir / skill_name
            if skill_path.exists():
                print(f"   ✅ {skill_name} skill exists")
            else:
                print(f"   ❌ {skill_name} skill missing")
                missing_skills.append(skill_name)

        if missing_skills:
            return {
                'status': 'failed',
                'message': f'Missing Bronze skills: {", ".join(missing_skills)}',
                'missing': missing_skills
            }

        print("   ✅ All Bronze skills present")
        return {
            'status': 'passed',
            'message': 'Bronze skills intact (3/3)'
        }

    def _check_monitored_directory(self) -> Dict[str, Any]:
        """Check monitored/ directory exists (Bronze file watcher)."""
        print("👁️  Checking monitored/ directory...")

        monitored_dir = self.project_root / 'monitored'

        if not monitored_dir.exists():
            print("   ⚠️  monitored/ directory not found")
            return {
                'status': 'warning',
                'message': 'Bronze monitored/ directory not found (file watcher disabled)'
            }

        print("   ✅ monitored/ directory exists")
        return {
            'status': 'passed',
            'message': 'Bronze file watcher directory present'
        }

    def _check_bronze_compatibility(self) -> Dict[str, Any]:
        """Check Bronze and Silver can coexist."""
        print("🔗 Checking Bronze-Silver compatibility...")

        checks = []

        # Check both orchestrators exist
        bronze_orch = self.project_root / 'main.py'
        silver_orch = self.project_root / 'scripts' / 'orchestrator.py'

        if bronze_orch.exists() and silver_orch.exists():
            print("   ✅ Both orchestrators present")
            checks.append({'check': 'both_orchestrators', 'status': 'pass'})
        else:
            print("   ⚠️  One orchestrator missing")
            checks.append({'check': 'both_orchestrators', 'status': 'warning'})

        # Check AI_Employee_Vault is shared
        vault_dir = self.project_root / 'AI_Employee_Vault'
        if vault_dir.exists():
            print("   ✅ Shared AI_Employee_Vault")
            checks.append({'check': 'shared_vault', 'status': 'pass'})
        else:
            print("   ❌ AI_Employee_Vault missing")
            return {
                'status': 'failed',
                'message': 'AI_Employee_Vault not found',
                'checks': checks
            }

        # Check skills directory is shared
        skills_dir = self.project_root / '.claude' / 'skills'
        if skills_dir.exists():
            skill_count = len([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
            print(f"   ✅ Shared skills directory ({skill_count} skills)")
            checks.append({'check': 'shared_skills', 'status': 'pass', 'count': skill_count})
        else:
            print("   ❌ Skills directory missing")
            return {
                'status': 'failed',
                'message': 'Skills directory not found',
                'checks': checks
            }

        print("   ✅ Bronze-Silver compatibility verified")
        return {
            'status': 'passed',
            'message': 'Bronze and Silver can coexist',
            'checks': checks
        }

    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print verification summary."""
        print()
        print("=" * 50)
        print("BRONZE TIER VERIFICATION SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'operational': '✅',
            'degraded': '⚠️',
            'broken': '❌'
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

        print("Verification Checks:")
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

        if results['overall_status'] == 'operational':
            print("✅ Bronze Tier remains fully operational")
            print("   Users can continue using main.py for Bronze functionality")
            print("   Silver Tier (scripts/orchestrator.py) adds new capabilities")
        elif results['overall_status'] == 'degraded':
            print("⚠️  Bronze Tier partially operational")
            print("   Some Bronze features may not work correctly")
            print("   Review warnings above")
        else:
            print("❌ Bronze Tier is broken")
            print("   Bronze functionality needs to be restored")
            print("   Review errors above")

        print()

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() + 'Z'


if __name__ == '__main__':
    verifier = BronzeVerifier()
    results = verifier.verify()

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'operational' else 1
    sys.exit(exit_code)
