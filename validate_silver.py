"""
Simple validation script - Checks basic Silver Tier structure.
Run this from PowerShell: python validate_silver.py
"""

import sys
from pathlib import Path

def check_structure():
    """Check basic Silver Tier structure."""
    print("=" * 60)
    print("Silver Tier Structure Validation")
    print("=" * 60)
    print()

    project_root = Path(__file__).parent
    checks_passed = 0
    checks_failed = 0

    # Check directories
    print("Checking directories...")
    required_dirs = [
        'AI_Employee_Vault',
        'AI_Employee_Vault/Logs',
        'AI_Employee_Vault/Needs_Action',
        'AI_Employee_Vault/Done',
        'AI_Employee_Vault/Pending_Approval',
        'AI_Employee_Vault/Approved',
        'AI_Employee_Vault/Rejected',
        'AI_Employee_Vault/Watchers',
        '.claude/skills',
        'mcp_servers',
        'scripts'
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  [OK] {dir_path}")
            checks_passed += 1
        else:
            print(f"  [FAIL] {dir_path} - MISSING")
            checks_failed += 1

    print()

    # Check skills
    print("Checking skills...")
    required_skills = [
        'task-orchestrator',
        'approval-guard',
        'logging-audit',
        'reasoning-loop',
        'email-mcp-sender',
        'linkedin-post-generator'
    ]

    skills_dir = project_root / '.claude' / 'skills'
    for skill in required_skills:
        skill_path = skills_dir / skill
        if skill_path.exists():
            print(f"  [OK] {skill}")
            checks_passed += 1
        else:
            print(f"  [FAIL] {skill} - MISSING")
            checks_failed += 1

    print()

    # Check key scripts
    print("Checking key scripts...")
    required_scripts = [
        'scripts/orchestrator.py',
        'scripts/logger.py',
        'scripts/event_queue.py',
        'scripts/approval_workflow.py',
        'scripts/plan_generator.py',
        'scripts/step_executor.py',
        'mcp_servers/mcp_base.py',
        'mcp_servers/email_server.py',
        'mcp_servers/linkedin_server.py'
    ]

    for script in required_scripts:
        script_path = project_root / script
        if script_path.exists():
            print(f"  [OK] {script}")
            checks_passed += 1
        else:
            print(f"  [FAIL] {script} - MISSING")
            checks_failed += 1

    print()
    print("=" * 60)
    print(f"Results: {checks_passed} passed, {checks_failed} failed")
    print("=" * 60)

    if checks_failed == 0:
        print("\nStatus: COMPLETE - All Silver Tier components present")
        return 0
    else:
        print(f"\nStatus: INCOMPLETE - {checks_failed} components missing")
        return 1

if __name__ == '__main__':
    sys.exit(check_structure())
