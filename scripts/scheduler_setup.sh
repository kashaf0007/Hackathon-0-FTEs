#!/bin/bash
# Scheduler Setup Script for Linux/macOS
# Sets up cron jobs for AI Employee system

set -e

echo "🔧 AI Employee Scheduler Setup (Linux/macOS)"
echo "============================================"
echo

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "⚠️  Detected macOS - Consider using setup_macos_scheduler.sh for launchd instead"
    echo "   This script will set up cron, but launchd is recommended on macOS"
    echo
fi

# Check if cron is available
if ! command -v crontab &> /dev/null; then
    echo "❌ Error: crontab command not found"
    echo "   Please install cron and try again"
    exit 1
fi

echo "✅ Found crontab"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "   Please install Python 3.11+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo

# Load existing crontab
echo "📋 Loading existing crontab..."
TEMP_CRON=$(mktemp)
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Check if AI Employee jobs already exist
if grep -q "AI Employee" "$TEMP_CRON"; then
    echo "⚠️  AI Employee cron jobs already exist"
    echo "   Remove existing jobs? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        sed -i.bak '/# AI Employee/d' "$TEMP_CRON"
        echo "   Removed existing jobs"
    fi
fi

# Add AI Employee cron jobs
echo
echo "📝 Adding AI Employee cron jobs..."
cat >> "$TEMP_CRON" << EOF

# AI Employee - Orchestrator (every 5 minutes)
*/5 * * * * cd "$PROJECT_ROOT" && python3 scripts/orchestrator.py --once >> logs/orchestrator.log 2>&1

# AI Employee - Watchers (every 10 minutes)
*/10 * * * * cd "$PROJECT_ROOT" && python3 scripts/run_watchers.py >> logs/watchers.log 2>&1

# AI Employee - Dashboard Update (daily at 8am)
0 8 * * * cd "$PROJECT_ROOT" && python3 scripts/update_dashboard.py >> logs/dashboard.log 2>&1

# AI Employee - Health Check (daily at 9am)
0 9 * * * cd "$PROJECT_ROOT" && python3 scripts/watchdog.py >> logs/watchdog.log 2>&1

# AI Employee - LinkedIn Post (weekly Monday at 9am)
0 9 * * 1 cd "$PROJECT_ROOT" && python3 scripts/linkedin_scheduler.py >> logs/linkedin.log 2>&1

EOF

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Cron jobs installed successfully"
echo

# Create log directory
mkdir -p "$PROJECT_ROOT/logs"
echo "✅ Created logs directory"
echo

# Display installed jobs
echo "📋 Installed cron jobs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
crontab -l | grep "AI Employee" || echo "No AI Employee jobs found"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

echo "✅ Setup complete!"
echo
echo "📝 Next steps:"
echo "   1. Verify cron jobs: crontab -l"
echo "   2. Check logs in: $PROJECT_ROOT/logs/"
echo "   3. Monitor system: tail -f logs/orchestrator.log"
echo
echo "⚠️  Note: Make sure DRY_RUN is set appropriately in .env"
echo
