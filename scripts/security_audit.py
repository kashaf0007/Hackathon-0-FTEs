"""
Security Audit Script - Validates security best practices.
Checks for credentials in code, proper secret management, and security configurations.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import re

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


class SecurityAuditor:
    """
    Performs security audit on AI Employee system.

    Checks:
    - No credentials in code
    - All secrets in .env
    - Proper .gitignore configuration
    - File permissions
    - OAuth2 token security
    - MCP server authentication
    """

    def __init__(self):
        """Initialize security auditor."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': None,
            'checks': {},
            'vulnerabilities': [],
            'warnings': [],
            'overall_status': 'secure'
        }

    def audit(self) -> Dict[str, Any]:
        """
        Run security audit.

        Returns:
            Audit results
        """
        print("🔒 Security Audit - AI Employee")
        print("=" * 50)
        print()

        self.results['timestamp'] = self._get_timestamp()

        # Run security checks
        checks = [
            ('credentials_in_code', self._check_credentials_in_code),
            ('secrets_management', self._check_secrets_management),
            ('gitignore_config', self._check_gitignore),
            ('file_permissions', self._check_file_permissions),
            ('oauth_security', self._check_oauth_security),
            ('env_file_security', self._check_env_security)
        ]

        for check_name, check_func in checks:
            try:
                result = check_func()
                self.results['checks'][check_name] = result

                if result['status'] == 'vulnerable':
                    self.results['vulnerabilities'].append(f"{check_name}: {result['message']}")
                elif result['status'] == 'warning':
                    self.results['warnings'].append(f"{check_name}: {result['message']}")

            except Exception as e:
                self.results['checks'][check_name] = {
                    'status': 'error',
                    'message': f'Check failed: {str(e)}'
                }
                self.results['warnings'].append(f"{check_name}: Check error - {str(e)}")

        # Determine overall status
        if self.results['vulnerabilities']:
            self.results['overall_status'] = 'vulnerable'
        elif self.results['warnings']:
            self.results['overall_status'] = 'warnings'

        # Print summary
        self._print_summary()

        return self.results

    def _check_credentials_in_code(self) -> Dict[str, Any]:
        """Check for hardcoded credentials in code."""
        print("🔍 Checking for credentials in code...")

        # Patterns that indicate potential credentials
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'api_key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'token'),
            (r'["\'][A-Za-z0-9]{32,}["\']', 'long_string')  # Potential API keys
        ]

        violations = []

        # Check Python files
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '.git' in str(py_file) or 'test' in str(py_file):
                continue

            try:
                content = py_file.read_text()

                for pattern, cred_type in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's in a comment or example
                        line = content[max(0, match.start()-50):match.end()+50]
                        if '#' in line or 'example' in line.lower() or 'test' in line.lower():
                            continue

                        # Skip if it's reading from env
                        if 'os.getenv' in line or 'os.environ' in line or '.env' in line:
                            continue

                        violations.append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'type': cred_type,
                            'line': match.group(0)[:50]
                        })
            except:
                pass

        if violations:
            print(f"   ❌ Found {len(violations)} potential credentials in code")
            return {
                'status': 'vulnerable',
                'message': f'Found {len(violations)} potential hardcoded credentials',
                'violations': violations[:5]  # First 5
            }

        print("   ✅ No hardcoded credentials found")
        return {
            'status': 'secure',
            'message': 'No hardcoded credentials detected'
        }

    def _check_secrets_management(self) -> Dict[str, Any]:
        """Check secrets are properly managed in .env."""
        print("🔐 Checking secrets management...")

        checks = []

        # Check .env.example exists
        env_example = self.project_root / '.env.example'
        if not env_example.exists():
            print("   ⚠️  .env.example missing")
            checks.append({'file': '.env.example', 'status': 'warning'})
        else:
            print("   ✅ .env.example exists")
            checks.append({'file': '.env.example', 'status': 'pass'})

        # Check .env is in .gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            content = gitignore.read_text()
            if '.env' in content and '.env.example' not in content:
                print("   ✅ .env in .gitignore")
                checks.append({'check': 'env_ignored', 'status': 'pass'})
            else:
                print("   ❌ .env not properly ignored")
                return {
                    'status': 'vulnerable',
                    'message': '.env not in .gitignore',
                    'checks': checks
                }
        else:
            print("   ⚠️  .gitignore missing")
            checks.append({'file': '.gitignore', 'status': 'warning'})

        # Check .env doesn't contain actual secrets (if it exists)
        env_file = self.project_root / '.env'
        if env_file.exists():
            content = env_file.read_text()
            # Check for placeholder values
            if 'your-' in content.lower() or 'example' in content.lower():
                print("   ⚠️  .env contains placeholder values")
                checks.append({'check': 'env_configured', 'status': 'warning'})
            else:
                print("   ✅ .env appears configured")
                checks.append({'check': 'env_configured', 'status': 'pass'})

        print("   ✅ Secrets management: SECURE")
        return {
            'status': 'secure',
            'message': 'Secrets properly managed',
            'checks': checks
        }

    def _check_gitignore(self) -> Dict[str, Any]:
        """Check .gitignore is properly configured."""
        print("📝 Checking .gitignore configuration...")

        gitignore = self.project_root / '.gitignore'
        if not gitignore.exists():
            print("   ❌ .gitignore missing")
            return {
                'status': 'vulnerable',
                'message': '.gitignore file not found'
            }

        content = gitignore.read_text()

        # Required patterns
        required_patterns = [
            '.env',
            '*.log',
            '__pycache__',
            'venv',
            '*_token.json',
            '*_credentials.json'
        ]

        missing = []
        for pattern in required_patterns:
            if pattern not in content:
                missing.append(pattern)

        if missing:
            print(f"   ⚠️  Missing patterns: {', '.join(missing)}")
            return {
                'status': 'warning',
                'message': f'Missing .gitignore patterns: {", ".join(missing)}',
                'missing': missing
            }

        print("   ✅ .gitignore properly configured")
        return {
            'status': 'secure',
            'message': '.gitignore properly configured'
        }

    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions on sensitive files."""
        print("🔒 Checking file permissions...")

        # On Windows, file permissions work differently
        if os.name == 'nt':
            print("   ⏭️  Skipping (Windows)")
            return {
                'status': 'skipped',
                'message': 'File permission check skipped on Windows'
            }

        sensitive_files = [
            '.env',
            'AI_Employee_Vault/Watchers/gmail_token.json',
            'AI_Employee_Vault/Watchers/gmail_credentials.json'
        ]

        issues = []
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # Check if file is world-readable
                stat_info = full_path.stat()
                mode = stat_info.st_mode

                # Check if others have read permission (octal 004)
                if mode & 0o004:
                    issues.append(f"{file_path}: world-readable")

        if issues:
            print(f"   ⚠️  {len(issues)} permission issues")
            return {
                'status': 'warning',
                'message': f'{len(issues)} files have overly permissive permissions',
                'issues': issues
            }

        print("   ✅ File permissions secure")
        return {
            'status': 'secure',
            'message': 'File permissions properly configured'
        }

    def _check_oauth_security(self) -> Dict[str, Any]:
        """Check OAuth2 token security."""
        print("🔑 Checking OAuth2 security...")

        checks = []

        # Check token files are in .gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            content = gitignore.read_text()
            if '*_token.json' in content or 'gmail_token.json' in content:
                print("   ✅ Token files ignored")
                checks.append({'check': 'tokens_ignored', 'status': 'pass'})
            else:
                print("   ⚠️  Token files not in .gitignore")
                checks.append({'check': 'tokens_ignored', 'status': 'warning'})
                return {
                    'status': 'warning',
                    'message': 'OAuth tokens not in .gitignore',
                    'checks': checks
                }

        # Check credentials files are in .gitignore
        if gitignore.exists():
            content = gitignore.read_text()
            if '*_credentials.json' in content or 'gmail_credentials.json' in content:
                print("   ✅ Credentials files ignored")
                checks.append({'check': 'credentials_ignored', 'status': 'pass'})
            else:
                print("   ⚠️  Credentials files not in .gitignore")
                checks.append({'check': 'credentials_ignored', 'status': 'warning'})

        print("   ✅ OAuth2 security: SECURE")
        return {
            'status': 'secure',
            'message': 'OAuth2 tokens properly secured',
            'checks': checks
        }

    def _check_env_security(self) -> Dict[str, Any]:
        """Check .env file security."""
        print("⚙️  Checking .env security...")

        env_file = self.project_root / '.env'

        if not env_file.exists():
            print("   ⏭️  .env not found (using defaults)")
            return {
                'status': 'skipped',
                'message': '.env file not found'
            }

        # Check file is not committed
        try:
            result = os.popen('git ls-files .env').read()
            if result.strip():
                print("   ❌ .env is committed to git")
                return {
                    'status': 'vulnerable',
                    'message': '.env file is committed to version control'
                }
        except:
            pass

        print("   ✅ .env security: SECURE")
        return {
            'status': 'secure',
            'message': '.env file properly secured'
        }

    def _print_summary(self) -> None:
        """Print audit summary."""
        print()
        print("=" * 50)
        print("SECURITY AUDIT SUMMARY")
        print("=" * 50)
        print()

        status_emoji = {
            'secure': '✅',
            'warnings': '⚠️',
            'vulnerable': '❌'
        }.get(self.results['overall_status'], '❓')

        print(f"Overall Status: {status_emoji} {self.results['overall_status'].upper()}")
        print()

        if self.results['vulnerabilities']:
            print(f"❌ Vulnerabilities ({len(self.results['vulnerabilities'])}):")
            for vuln in self.results['vulnerabilities']:
                print(f"   • {vuln}")
            print()

        if self.results['warnings']:
            print(f"⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
            print()

        print("Security Checks:")
        for check_name, check_result in self.results['checks'].items():
            status = check_result.get('status', 'unknown')
            message = check_result.get('message', 'No details')
            emoji = {
                'secure': '✅',
                'warning': '⚠️',
                'vulnerable': '❌',
                'skipped': '⏭️',
                'error': '❌'
            }.get(status, '❓')
            print(f"  {emoji} {check_name.replace('_', ' ').title()}: {message}")

        print()

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() + 'Z'


if __name__ == '__main__':
    auditor = SecurityAuditor()
    results = auditor.audit()

    # Exit with appropriate code
    exit_code = 0 if results['overall_status'] == 'secure' else 1
    sys.exit(exit_code)
