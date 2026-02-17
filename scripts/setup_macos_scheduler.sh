#!/bin/bash
# macOS launchd Setup Script for AI Employee
# Sets up launchd agents for automatic execution

set -e

echo "🔧 AI Employee Scheduler Setup (macOS launchd)"
echo "=============================================="
echo

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is for macOS only"
    echo "   Use scheduler_setup.sh for Linux"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "   Please install Python 3.11+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_PATH=$(which python3)
echo "✅ Found Python $PYTHON_VERSION at $PYTHON_PATH"
echo

# Create LaunchAgents directory if it doesn't exist
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"
echo "✅ LaunchAgents directory ready"
echo

# Create log directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
echo "✅ Created logs directory"
echo

# Function to create launchd plist
create_plist() {
    local name=$1
    local script=$2
    local interval=$3
    local start_calendar_interval=$4

    local plist_file="$LAUNCH_AGENTS_DIR/com.aiemployee.$name.plist"
    local log_file="$LOG_DIR/$name.log"
    local error_log_file="$LOG_DIR/$name.error.log"

    cat > "$plist_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiemployee.$name</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$PROJECT_ROOT/scripts/$script</string>
EOF

    # Add arguments if script is orchestrator
    if [[ "$script" == "orchestrator.py" ]]; then
        cat >> "$plist_file" << EOF
        <string>--once</string>
EOF
    fi

    cat >> "$plist_file" << EOF
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>

    <key>StandardOutPath</key>
    <string>$log_file</string>

    <key>StandardErrorPath</key>
    <string>$error_log_file</string>

    <key>RunAtLoad</key>
    <true/>

EOF

    # Add interval or calendar-based scheduling
    if [[ -n "$interval" ]]; then
        cat >> "$plist_file" << EOF
    <key>StartInterval</key>
    <integer>$interval</integer>

EOF
    elif [[ -n "$start_calendar_interval" ]]; then
        cat >> "$plist_file" << EOF
    <key>StartCalendarInterval</key>
    <dict>
        $start_calendar_interval
    </dict>

EOF
    fi

    cat >> "$plist_file" << EOF
    <key>KeepAlive</key>
    <false/>

    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
EOF

    echo "   ✅ Created: $plist_file"
}

# Remove existing plists if they exist
echo "🗑️  Removing existing AI Employee agents..."
for plist in "$LAUNCH_AGENTS_DIR"/com.aiemployee.*.plist; do
    if [[ -f "$plist" ]]; then
        label=$(basename "$plist" .plist)
        launchctl unload "$plist" 2>/dev/null || true
        rm "$plist"
        echo "   Removed: $label"
    fi
done
echo

# Create launchd plists
echo "📝 Creating launchd agents..."

# Orchestrator - every 5 minutes (300 seconds)
create_plist "orchestrator" "orchestrator.py" "300" ""

# Watchers - every 10 minutes (600 seconds)
create_plist "watchers" "run_watchers.py" "600" ""

# Dashboard - daily at 8:00 AM
create_plist "dashboard" "update_dashboard.py" "" "<key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer>"

# Watchdog - daily at 9:00 AM
create_plist "watchdog" "watchdog.py" "" "<key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer>"

# LinkedIn - weekly Monday at 9:00 AM
create_plist "linkedin" "linkedin_scheduler.py" "" "<key>Weekday</key><integer>1</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer>"

echo "✅ All agents created"
echo

# Load launchd agents
echo "🚀 Loading launchd agents..."
for plist in "$LAUNCH_AGENTS_DIR"/com.aiemployee.*.plist; do
    if [[ -f "$plist" ]]; then
        label=$(basename "$plist" .plist)
        launchctl load "$plist"
        echo "   ✅ Loaded: $label"
    fi
done
echo

# Display loaded agents
echo "📋 Loaded agents:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
launchctl list | grep com.aiemployee || echo "No agents found"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

echo "✅ Setup complete!"
echo
echo "📝 Next steps:"
echo "   1. Verify agents: launchctl list | grep com.aiemployee"
echo "   2. Check logs in: $LOG_DIR/"
echo "   3. Monitor execution: tail -f $LOG_DIR/orchestrator.log"
echo
echo "⚠️  Note: Make sure DRY_RUN is set appropriately in .env"
echo
echo "To unload agents:"
echo "   launchctl unload ~/Library/LaunchAgents/com.aiemployee.*.plist"
echo
echo "To reload agents:"
echo "   launchctl load ~/Library/LaunchAgents/com.aiemployee.*.plist"
echo
