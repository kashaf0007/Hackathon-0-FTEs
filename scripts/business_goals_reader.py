"""
Business Goals Reader - Reads and parses Business_Goals.md for content generation.
Extracts goals, target audience, value propositions, and current focus areas.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from scripts.logger import get_logger


class BusinessGoalsReader:
    """
    Reads and parses Business_Goals.md to extract business context.

    Extracts:
    - Primary goals (revenue, customer acquisition, etc.)
    - Target audience
    - Value propositions
    - Current focus areas
    - Key messaging themes
    """

    def __init__(self, goals_file: Optional[Path] = None):
        """
        Initialize business goals reader.

        Args:
            goals_file: Path to Business_Goals.md (default: AI_Employee_Vault/Business_Goals.md)
        """
        self.goals_file = goals_file or Path('AI_Employee_Vault/Business_Goals.md')
        self.logger = get_logger()

    def read_goals(self) -> Dict[str, Any]:
        """
        Read and parse Business_Goals.md.

        Returns:
            Dictionary with parsed business goals and context
        """
        if not self.goals_file.exists():
            self.logger.warning(
                component="content",
                action="goals_file_missing",
                actor="business_goals_reader",
                target=str(self.goals_file),
                details={"using_defaults": True}
            )
            return self._get_default_goals()

        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                content = f.read()

            goals = self._parse_goals(content)

            self.logger.info(
                component="content",
                action="goals_loaded",
                actor="business_goals_reader",
                target=str(self.goals_file),
                details={
                    "primary_goals_count": len(goals.get('primary_goals', [])),
                    "target_audiences_count": len(goals.get('target_audience', [])),
                    "current_focus": goals.get('current_focus', 'none')
                }
            )

            return goals

        except Exception as e:
            self.logger.error(
                component="content",
                action="goals_read_failed",
                actor="business_goals_reader",
                target=str(self.goals_file),
                details={"error": str(e)}
            )
            return self._get_default_goals()

    def _parse_goals(self, content: str) -> Dict[str, Any]:
        """
        Parse Business_Goals.md content.

        Args:
            content: File content

        Returns:
            Parsed goals dictionary
        """
        goals = {
            'primary_goals': [],
            'target_audience': [],
            'value_propositions': [],
            'current_focus': '',
            'key_themes': [],
            'metrics': {}
        }

        # Extract primary goals
        goals_section = self._extract_section(content, 'Primary Goals', 'Target Audience')
        if goals_section:
            goals['primary_goals'] = self._extract_bullet_points(goals_section)

        # Extract target audience
        audience_section = self._extract_section(content, 'Target Audience', 'Value Proposition')
        if audience_section:
            goals['target_audience'] = self._extract_bullet_points(audience_section)

        # Extract value propositions
        value_section = self._extract_section(content, 'Value Proposition', 'Current Focus')
        if value_section:
            goals['value_propositions'] = self._extract_bullet_points(value_section)

        # Extract current focus
        focus_section = self._extract_section(content, 'Current Focus', 'Key Themes')
        if focus_section:
            goals['current_focus'] = focus_section.strip()

        # Extract key themes
        themes_section = self._extract_section(content, 'Key Themes', 'Metrics')
        if themes_section:
            goals['key_themes'] = self._extract_bullet_points(themes_section)

        # Extract metrics
        metrics_section = self._extract_section(content, 'Metrics', None)
        if metrics_section:
            goals['metrics'] = self._extract_metrics(metrics_section)

        return goals

    def _extract_section(self, content: str, start_header: str, end_header: Optional[str]) -> str:
        """
        Extract content between two headers.

        Args:
            content: Full content
            start_header: Starting header
            end_header: Ending header (None for end of file)

        Returns:
            Section content
        """
        # Find start
        start_pattern = rf'#+\s*{re.escape(start_header)}'
        start_match = re.search(start_pattern, content, re.IGNORECASE)
        if not start_match:
            return ''

        start_pos = start_match.end()

        # Find end
        if end_header:
            end_pattern = rf'#+\s*{re.escape(end_header)}'
            end_match = re.search(end_pattern, content[start_pos:], re.IGNORECASE)
            if end_match:
                end_pos = start_pos + end_match.start()
            else:
                end_pos = len(content)
        else:
            end_pos = len(content)

        return content[start_pos:end_pos].strip()

    def _extract_bullet_points(self, text: str) -> List[str]:
        """
        Extract bullet points from text.

        Args:
            text: Text containing bullet points

        Returns:
            List of bullet point contents
        """
        bullets = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            # Match various bullet formats: -, *, •, →
            if re.match(r'^[-*•→]\s+', line):
                bullet_text = re.sub(r'^[-*•→]\s+', '', line).strip()
                if bullet_text:
                    bullets.append(bullet_text)

        return bullets

    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """
        Extract metrics from text.

        Args:
            text: Text containing metrics

        Returns:
            Dictionary of metrics
        """
        metrics = {}
        lines = text.split('\n')

        for line in lines:
            # Match patterns like "Revenue: $X" or "Clients: X per month"
            match = re.match(r'^[-*•]?\s*([^:]+):\s*(.+)$', line.strip())
            if match:
                key = match.group(1).strip().lower().replace(' ', '_')
                value = match.group(2).strip()
                metrics[key] = value

        return metrics

    def _get_default_goals(self) -> Dict[str, Any]:
        """
        Get default goals when file is missing or unreadable.

        Returns:
            Default goals dictionary
        """
        return {
            'primary_goals': [
                'Acquire new clients',
                'Increase revenue',
                'Build brand awareness'
            ],
            'target_audience': [
                'Small business owners',
                'CTOs and technical leaders',
                'Operations managers'
            ],
            'value_propositions': [
                'AI automation saves time and reduces costs',
                'Easy to implement and use',
                '24/7 automated operations'
            ],
            'current_focus': 'Customer support automation',
            'key_themes': [
                'Efficiency',
                'Cost savings',
                'Scalability',
                'Innovation'
            ],
            'metrics': {
                'target_clients': '10 per month',
                'revenue_goal': 'Growth',
                'engagement_rate': 'Increase'
            }
        }

    def get_content_topics(self) -> List[str]:
        """
        Get suggested content topics based on business goals.

        Returns:
            List of content topic suggestions
        """
        goals = self.read_goals()

        topics = []

        # Topics from current focus
        if goals.get('current_focus'):
            topics.append(goals['current_focus'])

        # Topics from value propositions
        for vp in goals.get('value_propositions', []):
            topics.append(vp)

        # Topics from key themes
        for theme in goals.get('key_themes', []):
            topics.append(f"{theme} in business")

        # Generic topics if nothing specific
        if not topics:
            topics = [
                'AI automation benefits',
                'Business efficiency tips',
                'Digital transformation',
                'Customer success stories'
            ]

        return topics


# Global instance
_business_goals_reader = None


def get_business_goals_reader() -> BusinessGoalsReader:
    """Get or create the global business goals reader instance."""
    global _business_goals_reader
    if _business_goals_reader is None:
        _business_goals_reader = BusinessGoalsReader()
    return _business_goals_reader
