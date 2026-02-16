"""Configuration management for Bronze Tier Constitutional FTE.

Loads configuration from .env file and provides access to settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for orchestrator.

    Loads settings from .env file and provides typed access.
    All settings have sensible defaults.
    """

    def __init__(self, env_file: Optional[Path] = None):
        """Initialize configuration.

        Args:
            env_file: Path to .env file (default: .env in project root)
        """
        if env_file is None:
            env_file = Path(".env")

        # Load .env file if it exists
        if env_file.exists():
            load_dotenv(env_file)

        # Load configuration with defaults
        self.dry_run = self._get_bool("DRY_RUN", default=False)
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.poll_interval = self._get_int("POLL_INTERVAL", default=5)
        self.max_retries = self._get_int("MAX_RETRIES", default=3)

        # Paths (convert to absolute paths for reliability)
        self.vault_path = Path("AI_Employee_Vault").resolve()
        self.skills_path = Path(".claude/skills").resolve()
        self.logs_path = self.vault_path / "Logs"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"
        self.briefings_path = self.vault_path / "Briefings"
        self.dashboard_path = self.vault_path / "Dashboard.md"

        # Validate configuration
        self._validate()

    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def _get_int(self, key: str, default: int) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default

    def _validate(self) -> None:
        """Validate configuration values."""
        if self.poll_interval < 1:
            raise ValueError("POLL_INTERVAL must be at least 1 second")

        if self.max_retries < 0 or self.max_retries > 10:
            raise ValueError("MAX_RETRIES must be between 0 and 10")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}")

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.vault_path,
            self.logs_path,
            self.needs_action_path,
            self.pending_approval_path,
            self.done_path,
            self.briefings_path,
            self.skills_path,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"Config(dry_run={self.dry_run}, "
            f"log_level={self.log_level}, "
            f"poll_interval={self.poll_interval}, "
            f"max_retries={self.max_retries})"
        )
