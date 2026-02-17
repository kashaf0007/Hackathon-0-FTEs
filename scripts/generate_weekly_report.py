"""
Weekly Report Generator - Creates comprehensive weekly activity reports.
Analyzes logs and generates summary of system activity.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json
from collections import defaultdict

from scripts.logger import get_logger


class WeeklyReportGenerator:
    """
    Generates weekly activity reports from system logs.

    Reports include:
    - Event statistics
    - Approval metrics
    - Skill usage
    - Error summary
    - Performance metrics
    - Top actions
    """

    def __init__(self):
        """Initialize report generator."""
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.vault_dir = self.project_root / 'AI_Employee_Vault'
        self.log_dir = self.vault_dir / 'Logs'
        self.briefings_dir = self.vault_dir / 'Briefings'

    def generate_report(self, weeks_back: int = 1) -> Dict[str, Any]:
        """
        Generate weekly report.

        Args:
            weeks_back: Number of weeks back to report (default: 1 = last week)

        Returns:
            Report data
        """
        # Calculate date range
        end_date = datetime.now() - timedelta(days=(weeks_back - 1) * 7)
        start_date = end_date - timedelta(days=7)

        print(f"📊 Generating Weekly Report")
        print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print()

        # Collect log data
        log_data = self._collect_logs(start_date, end_date)

        if not log_data:
            print("⚠️  No log data found for this period")
            return {
                'status': 'no_data',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }

        # Analyze data
        report = self._analyze_logs(log_data, start_date, end_date)

        # Generate report file
        report_file = self._write_report(report)

        print(f"✅ Report generated: {report_file}")
        print()

        return report

    def _collect_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Collect log entries for date range.

        Args:
            start_date: Start of period
            end_date: End of period

        Returns:
            List of log entries
        """
        log_entries = []

        # Iterate through dates in range
        current_date = start_date
        while current_date <= end_date:
            log_file = self.log_dir / f"{current_date.strftime('%Y-%m-%d')}.json"

            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                log_entries.append(entry)
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    print(f"⚠️  Error reading {log_file.name}: {str(e)}")

            current_date += timedelta(days=1)

        return log_entries

    def _analyze_logs(self, log_data: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Analyze log data and generate report.

        Args:
            log_data: List of log entries
            start_date: Start of period
            end_date: End of period

        Returns:
            Report data
        """
        report = {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'days': (end_date - start_date).days + 1
            },
            'summary': {
                'total_events': len(log_data),
                'events_per_day': len(log_data) / ((end_date - start_date).days + 1)
            },
            'components': defaultdict(int),
            'actions': defaultdict(int),
            'actors': defaultdict(int),
            'status': defaultdict(int),
            'errors': [],
            'approvals': {
                'requested': 0,
                'granted': 0,
                'rejected': 0,
                'timeout': 0
            },
            'skills': defaultdict(int),
            'performance': {
                'total_duration_ms': 0,
                'avg_duration_ms': 0,
                'max_duration_ms': 0,
                'min_duration_ms': float('inf')
            },
            'top_events': []
        }

        # Analyze each log entry
        for entry in log_data:
            # Component stats
            component = entry.get('component', 'unknown')
            report['components'][component] += 1

            # Action stats
            action = entry.get('action', 'unknown')
            report['actions'][action] += 1

            # Actor stats
            actor = entry.get('actor', 'unknown')
            report['actors'][actor] += 1

            # Status stats
            status = entry.get('status', 'unknown')
            report['status'][status] += 1

            # Error tracking
            if status == 'error':
                report['errors'].append({
                    'timestamp': entry.get('timestamp'),
                    'component': component,
                    'action': action,
                    'target': entry.get('target'),
                    'details': entry.get('details', {})
                })

            # Approval tracking
            if 'approval' in action:
                if 'requested' in action:
                    report['approvals']['requested'] += 1
                elif 'granted' in action or 'approved' in action:
                    report['approvals']['granted'] += 1
                elif 'rejected' in action:
                    report['approvals']['rejected'] += 1
                elif 'timeout' in action:
                    report['approvals']['timeout'] += 1

            # Skill usage (from actor field)
            if actor and actor not in ['orchestrator', 'system', 'human']:
                report['skills'][actor] += 1

            # Performance metrics
            details = entry.get('details', {})
            if 'duration_ms' in details:
                duration = details['duration_ms']
                report['performance']['total_duration_ms'] += duration
                report['performance']['max_duration_ms'] = max(
                    report['performance']['max_duration_ms'], duration
                )
                report['performance']['min_duration_ms'] = min(
                    report['performance']['min_duration_ms'], duration
                )

        # Calculate averages
        if log_data:
            report['performance']['avg_duration_ms'] = (
                report['performance']['total_duration_ms'] / len(log_data)
            )

        # Convert defaultdicts to regular dicts and sort
        report['components'] = dict(sorted(report['components'].items(), key=lambda x: x[1], reverse=True))
        report['actions'] = dict(sorted(report['actions'].items(), key=lambda x: x[1], reverse=True))
        report['actors'] = dict(sorted(report['actors'].items(), key=lambda x: x[1], reverse=True))
        report['status'] = dict(report['status'])
        report['skills'] = dict(sorted(report['skills'].items(), key=lambda x: x[1], reverse=True))

        # Top 10 actions
        report['top_events'] = list(report['actions'].items())[:10]

        # Success rate
        total_with_status = sum(report['status'].values())
        if total_with_status > 0:
            success_count = report['status'].get('success', 0)
            report['summary']['success_rate'] = (success_count / total_with_status) * 100
        else:
            report['summary']['success_rate'] = 0

        return report

    def _write_report(self, report: Dict[str, Any]) -> Path:
        """
        Write report to markdown file.

        Args:
            report: Report data

        Returns:
            Path to report file
        """
        # Ensure briefings directory exists
        self.briefings_dir.mkdir(exist_ok=True)

        # Generate filename
        end_date = datetime.strptime(report['period']['end'], '%Y-%m-%d')
        filename = f"weekly_report_{end_date.strftime('%Y-%m-%d')}.md"
        report_file = self.briefings_dir / filename

        # Generate markdown content
        content = self._format_report_markdown(report)

        # Write file
        with open(report_file, 'w') as f:
            f.write(content)

        return report_file

    def _format_report_markdown(self, report: Dict[str, Any]) -> str:
        """
        Format report as markdown.

        Args:
            report: Report data

        Returns:
            Markdown content
        """
        lines = []

        # Header
        lines.append(f"# AI Employee Weekly Report")
        lines.append(f"")
        lines.append(f"**Period**: {report['period']['start']} to {report['period']['end']} ({report['period']['days']} days)")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        # Executive Summary
        lines.append(f"## Executive Summary")
        lines.append(f"")
        lines.append(f"- **Total Events**: {report['summary']['total_events']:,}")
        lines.append(f"- **Events Per Day**: {report['summary']['events_per_day']:.1f}")
        lines.append(f"- **Success Rate**: {report['summary'].get('success_rate', 0):.1f}%")
        lines.append(f"- **Errors**: {len(report['errors'])}")
        lines.append(f"")

        # Component Activity
        lines.append(f"## Component Activity")
        lines.append(f"")
        lines.append(f"| Component | Events | Percentage |")
        lines.append(f"|-----------|--------|------------|")
        total_events = report['summary']['total_events']
        for component, count in list(report['components'].items())[:10]:
            percentage = (count / total_events) * 100 if total_events > 0 else 0
            lines.append(f"| {component} | {count:,} | {percentage:.1f}% |")
        lines.append(f"")

        # Top Actions
        lines.append(f"## Top Actions")
        lines.append(f"")
        lines.append(f"| Action | Count |")
        lines.append(f"|--------|-------|")
        for action, count in report['top_events']:
            lines.append(f"| {action} | {count:,} |")
        lines.append(f"")

        # Skill Usage
        if report['skills']:
            lines.append(f"## Skill Usage")
            lines.append(f"")
            lines.append(f"| Skill | Invocations |")
            lines.append(f"|-------|-------------|")
            for skill, count in list(report['skills'].items())[:10]:
                lines.append(f"| {skill} | {count:,} |")
            lines.append(f"")

        # Approval Metrics
        lines.append(f"## Approval Metrics")
        lines.append(f"")
        lines.append(f"- **Requested**: {report['approvals']['requested']}")
        lines.append(f"- **Granted**: {report['approvals']['granted']}")
        lines.append(f"- **Rejected**: {report['approvals']['rejected']}")
        lines.append(f"- **Timeout**: {report['approvals']['timeout']}")
        lines.append(f"")
        if report['approvals']['requested'] > 0:
            approval_rate = (report['approvals']['granted'] / report['approvals']['requested']) * 100
            lines.append(f"**Approval Rate**: {approval_rate:.1f}%")
            lines.append(f"")

        # Performance Metrics
        lines.append(f"## Performance Metrics")
        lines.append(f"")
        lines.append(f"- **Average Duration**: {report['performance']['avg_duration_ms']:.0f} ms")
        lines.append(f"- **Max Duration**: {report['performance']['max_duration_ms']:.0f} ms")
        if report['performance']['min_duration_ms'] != float('inf'):
            lines.append(f"- **Min Duration**: {report['performance']['min_duration_ms']:.0f} ms")
        lines.append(f"")

        # Status Distribution
        lines.append(f"## Status Distribution")
        lines.append(f"")
        lines.append(f"| Status | Count | Percentage |")
        lines.append(f"|--------|-------|------------|")
        for status, count in report['status'].items():
            percentage = (count / total_events) * 100 if total_events > 0 else 0
            lines.append(f"| {status} | {count:,} | {percentage:.1f}% |")
        lines.append(f"")

        # Errors
        if report['errors']:
            lines.append(f"## Errors ({len(report['errors'])})")
            lines.append(f"")
            for i, error in enumerate(report['errors'][:10], 1):
                lines.append(f"### Error {i}")
                lines.append(f"")
                lines.append(f"- **Time**: {error.get('timestamp', 'unknown')}")
                lines.append(f"- **Component**: {error.get('component', 'unknown')}")
                lines.append(f"- **Action**: {error.get('action', 'unknown')}")
                lines.append(f"- **Target**: {error.get('target', 'unknown')}")
                if error.get('details'):
                    lines.append(f"- **Details**: {error['details']}")
                lines.append(f"")
            if len(report['errors']) > 10:
                lines.append(f"*... and {len(report['errors']) - 10} more errors*")
                lines.append(f"")

        # Footer
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"*Generated by AI Employee Weekly Report Generator*")
        lines.append(f"")

        return '\n'.join(lines)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Weekly Report Generator')
    parser.add_argument('--weeks-back', type=int, default=1,
                        help='Number of weeks back to report (default: 1 = last week)')

    args = parser.parse_args()

    generator = WeeklyReportGenerator()
    report = generator.generate_report(weeks_back=args.weeks_back)

    if report.get('status') == 'no_data':
        print("No data available for the specified period")
        sys.exit(1)
    else:
        sys.exit(0)
