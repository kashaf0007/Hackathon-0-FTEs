# Sample Task: Delete Temporary Files

**Type**: delete_file
**Priority**: LOW
**Created**: 2026-02-17T10:10:00
**Status**: PENDING

## Context
Delete temporary files older than 30 days from the project directory to free up disk space. This includes:
- *.tmp files
- *.log files older than 30 days
- Cache directories

This is a high-risk action because it involves permanent file deletion.

## Expected Output
List of files deleted with their sizes. Total disk space freed. Confirmation that only files older than 30 days were removed.
