"""
Log Rotation Script - Archives logs older than 90 days.
Maintains log directory health and prevents disk space issues.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import shutil
import json

from scripts.logger import get_logger


class LogRotator:
    """
    Manages log file rotation and archival.

    Responsibilities:
    - Archive logs older than retention period
    - Compress archived logs
    - Maintain archive directory structure
    - Report rotation statistics
    """

    def __init__(self, retention_days: int = 90):
        """
        Initialize log rotator.

        Args:
            retention_days: Number of days to retain logs (default: 90)
        """
        self.retention_days = retention_days
        self.logger = get_logger()
        self.project_root = Path(__file__).parent.parent
        self.log_dir = self.project_root / 'AI_Employee_Vault' / 'Logs'
        self.archive_dir = self.log_dir / 'archive'

    def rotate(self) -> Dict[str, Any]:
        """
        Rotate logs older than retention period.

        Returns:
            Rotation statistics
        """
        print(f"🔄 Log Rotation Started")
        print(f"   Retention: {self.retention_days} days")
        print(f"   Log Directory: {self.log_dir}")
        print()

        # Ensure archive directory exists
        self.archive_dir.mkdir(exist_ok=True)

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        print(f"📅 Cutoff Date: {cutoff_date.strftime('%Y-%m-%d')}")
        print(f"   (Files older than this will be archived)")
        print()

        # Find old log files
        old_logs = self._find_old_logs(cutoff_date)

        if not old_logs:
            print("✅ No logs to rotate")
            return {
                'status': 'success',
                'files_archived': 0,
                'bytes_archived': 0,
                'cutoff_date': cutoff_date.isoformat()
            }

        print(f"📦 Found {len(old_logs)} log files to archive")
        print()

        # Archive logs
        stats = self._archive_logs(old_logs)

        # Log rotation event
        self.logger.info(
            component="maintenance",
            action="logs_rotated",
            actor="log_rotator",
            target="log_directory",
            details=stats
        )

        # Print summary
        self._print_summary(stats)

        return stats

    def _find_old_logs(self, cutoff_date: datetime) -> List[Path]:
        """
        Find log files older than cutoff date.

        Args:
            cutoff_date: Files older than this will be returned

        Returns:
            List of log file paths
        """
        old_logs = []

        for log_file in self.log_dir.glob('*.json'):
            # Skip if already in archive
            if 'archive' in str(log_file):
                continue

            # Check file modification time
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

            if mtime < cutoff_date:
                old_logs.append(log_file)

        return sorted(old_logs)

    def _archive_logs(self, log_files: List[Path]) -> Dict[str, Any]:
        """
        Archive log files to archive directory.

        Args:
            log_files: List of log files to archive

        Returns:
            Archive statistics
        """
        stats = {
            'status': 'success',
            'files_archived': 0,
            'bytes_archived': 0,
            'files_failed': 0,
            'errors': [],
            'cutoff_date': (datetime.now() - timedelta(days=self.retention_days)).isoformat()
        }

        for log_file in log_files:
            try:
                # Get file size
                file_size = log_file.stat().st_size

                # Determine archive path (organize by year/month)
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                year_month = mtime.strftime('%Y-%m')
                archive_subdir = self.archive_dir / year_month
                archive_subdir.mkdir(exist_ok=True)

                # Move file to archive
                archive_path = archive_subdir / log_file.name
                shutil.move(str(log_file), str(archive_path))

                stats['files_archived'] += 1
                stats['bytes_archived'] += file_size

                print(f"   ✅ Archived: {log_file.name} → archive/{year_month}/")

            except Exception as e:
                stats['files_failed'] += 1
                stats['errors'].append({
                    'file': log_file.name,
                    'error': str(e)
                })
                print(f"   ❌ Failed: {log_file.name} - {str(e)}")

                self.logger.error(
                    component="maintenance",
                    action="log_archive_failed",
                    actor="log_rotator",
                    target=log_file.name,
                    details={'error': str(e)}
                )

        return stats

    def _print_summary(self, stats: Dict[str, Any]) -> None:
        """
        Print rotation summary.

        Args:
            stats: Rotation statistics
        """
        print()
        print("=" * 50)
        print("ROTATION SUMMARY")
        print("=" * 50)
        print()

        status_emoji = '✅' if stats['status'] == 'success' else '❌'
        print(f"Status: {status_emoji} {stats['status'].upper()}")
        print(f"Files Archived: {stats['files_archived']}")
        print(f"Bytes Archived: {stats['bytes_archived']:,} ({self._format_bytes(stats['bytes_archived'])})")

        if stats['files_failed'] > 0:
            print(f"Files Failed: {stats['files_failed']}")
            print()
            print("Errors:")
            for error in stats['errors']:
                print(f"  ❌ {error['file']}: {error['error']}")

        print()
        print(f"Archive Location: {self.archive_dir}")
        print()

    def _format_bytes(self, bytes: int) -> str:
        """
        Format bytes as human-readable string.

        Args:
            bytes: Number of bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    def get_archive_stats(self) -> Dict[str, Any]:
        """
        Get statistics about archived logs.

        Returns:
            Archive statistics
        """
        if not self.archive_dir.exists():
            return {
                'total_files': 0,
                'total_bytes': 0,
                'oldest_log': None,
                'newest_log': None
            }

        archive_files = list(self.archive_dir.rglob('*.json'))

        if not archive_files:
            return {
                'total_files': 0,
                'total_bytes': 0,
                'oldest_log': None,
                'newest_log': None
            }

        total_bytes = sum(f.stat().st_size for f in archive_files)
        oldest = min(archive_files, key=lambda f: f.stat().st_mtime)
        newest = max(archive_files, key=lambda f: f.stat().st_mtime)

        return {
            'total_files': len(archive_files),
            'total_bytes': total_bytes,
            'total_bytes_formatted': self._format_bytes(total_bytes),
            'oldest_log': oldest.name,
            'oldest_date': datetime.fromtimestamp(oldest.stat().st_mtime).isoformat(),
            'newest_log': newest.name,
            'newest_date': datetime.fromtimestamp(newest.stat().st_mtime).isoformat()
        }


# Global instance
_log_rotator = None


def get_log_rotator(retention_days: int = 90) -> LogRotator:
    """Get or create the global log rotator instance."""
    global _log_rotator
    if _log_rotator is None:
        _log_rotator = LogRotator(retention_days=retention_days)
    return _log_rotator


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Log Rotation')
    parser.add_argument('--retention-days', type=int, default=90,
                        help='Number of days to retain logs (default: 90)')
    parser.add_argument('--stats', action='store_true',
                        help='Show archive statistics only')

    args = parser.parse_args()

    rotator = LogRotator(retention_days=args.retention_days)

    if args.stats:
        # Show archive statistics
        print("📊 Archive Statistics")
        print("=" * 50)
        print()

        stats = rotator.get_archive_stats()

        if stats['total_files'] == 0:
            print("No archived logs found")
        else:
            print(f"Total Files: {stats['total_files']}")
            print(f"Total Size: {stats['total_bytes_formatted']}")
            print(f"Oldest Log: {stats['oldest_log']} ({stats['oldest_date']})")
            print(f"Newest Log: {stats['newest_log']} ({stats['newest_date']})")

        print()
    else:
        # Perform rotation
        results = rotator.rotate()
        sys.exit(0 if results['status'] == 'success' else 1)
