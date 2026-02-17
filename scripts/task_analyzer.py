"""
TaskAnalyzer class - Analyzes events and classifies them for appropriate handling.
Determines task complexity, required actions, and execution strategy.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from scripts.logger import get_logger


class TaskAnalyzer:
    """
    Analyzes events to determine task complexity and execution strategy.

    Classification categories:
    - Simple: Single-step tasks (reply to email, acknowledge message)
    - Complex: Multi-step tasks requiring planning (sales opportunity, project request)
    - Routine: Automated tasks with predefined workflows (weekly report, scheduled post)
    - Critical: High-priority tasks requiring immediate attention (urgent request, complaint)
    """

    def __init__(self):
        """Initialize task analyzer."""
        self.logger = get_logger()

        # Keywords for task classification
        self.urgent_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'important', 'priority', 'deadline', 'time-sensitive'
        ]

        self.sales_keywords = [
            'pricing', 'quote', 'proposal', 'interested', 'purchase',
            'buy', 'cost', 'demo', 'trial', 'consultation', 'meeting'
        ]

        self.support_keywords = [
            'help', 'issue', 'problem', 'error', 'bug', 'not working',
            'broken', 'question', 'how to', 'support', 'assistance'
        ]

        self.complaint_keywords = [
            'complaint', 'unhappy', 'disappointed', 'frustrated', 'angry',
            'unacceptable', 'poor', 'terrible', 'worst', 'refund'
        ]

        self.routine_keywords = [
            'weekly', 'daily', 'monthly', 'scheduled', 'regular',
            'recurring', 'automated', 'routine', 'periodic'
        ]

    def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an event and determine its classification and handling strategy.

        Args:
            event: Event dictionary with source, type, content, metadata

        Returns:
            Analysis result with:
            - complexity: simple, complex, routine, critical
            - category: sales, support, complaint, general, routine
            - priority: low, medium, high, urgent
            - requires_plan: boolean
            - suggested_actions: list of action descriptions
            - estimated_steps: number of steps needed
        """
        source = event.get('source', 'unknown')
        event_type = event.get('type', 'unknown')
        content = event.get('content', '').lower()
        metadata = event.get('metadata', {})

        # Determine category
        category = self._classify_category(content, metadata)

        # Determine priority
        priority = self._classify_priority(content, metadata, category)

        # Determine complexity
        complexity = self._classify_complexity(content, metadata, category, priority)

        # Determine if plan is needed
        requires_plan = complexity in ['complex', 'critical']

        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(
            source, event_type, category, complexity, metadata
        )

        # Estimate steps
        estimated_steps = self._estimate_steps(complexity, category, len(suggested_actions))

        analysis = {
            'complexity': complexity,
            'category': category,
            'priority': priority,
            'requires_plan': requires_plan,
            'suggested_actions': suggested_actions,
            'estimated_steps': estimated_steps,
            'source': source,
            'event_type': event_type
        }

        # Log analysis
        self.logger.info(
            component="reasoning",
            action="event_analyzed",
            actor="task_analyzer",
            target=event.get('id', 'unknown'),
            details={
                'complexity': complexity,
                'category': category,
                'priority': priority,
                'requires_plan': requires_plan
            }
        )

        return analysis

    def _classify_category(self, content: str, metadata: Dict[str, Any]) -> str:
        """Classify event into a category based on content and metadata."""
        # Check for routine/scheduled tasks
        if any(keyword in content for keyword in self.routine_keywords):
            return 'routine'

        # Check for complaints
        if any(keyword in content for keyword in self.complaint_keywords):
            return 'complaint'

        # Check for sales opportunities
        if any(keyword in content for keyword in self.sales_keywords):
            return 'sales'

        # Check for support requests
        if any(keyword in content for keyword in self.support_keywords):
            return 'support'

        # Default to general
        return 'general'

    def _classify_priority(
        self,
        content: str,
        metadata: Dict[str, Any],
        category: str
    ) -> str:
        """Classify event priority based on content, metadata, and category."""
        # Check for urgent keywords
        if any(keyword in content for keyword in self.urgent_keywords):
            return 'urgent'

        # Complaints are high priority
        if category == 'complaint':
            return 'high'

        # Sales opportunities are medium-high priority
        if category == 'sales':
            return 'high'

        # Support requests are medium priority
        if category == 'support':
            return 'medium'

        # Routine tasks are low priority
        if category == 'routine':
            return 'low'

        # Check metadata for priority hints
        if metadata.get('priority') == 'high':
            return 'high'

        # Default to medium
        return 'medium'

    def _classify_complexity(
        self,
        content: str,
        metadata: Dict[str, Any],
        category: str,
        priority: str
    ) -> str:
        """Classify task complexity based on all factors."""
        # Urgent tasks are critical
        if priority == 'urgent':
            return 'critical'

        # Complaints are complex (require careful handling)
        if category == 'complaint':
            return 'complex'

        # Sales opportunities are complex (multi-step)
        if category == 'sales':
            return 'complex'

        # Routine tasks are simple (predefined workflow)
        if category == 'routine':
            return 'routine'

        # Support requests can be simple or complex
        if category == 'support':
            # Check content length as complexity indicator
            if len(content) > 500:
                return 'complex'
            return 'simple'

        # General tasks - check content length
        if len(content) > 300:
            return 'complex'

        return 'simple'

    def _generate_suggested_actions(
        self,
        source: str,
        event_type: str,
        category: str,
        complexity: str,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Generate suggested actions based on event characteristics."""
        actions = []

        if category == 'sales':
            actions.extend([
                'Analyze lead quality and intent',
                'Draft personalized response with value proposition',
                'Offer consultation or demo',
                'Schedule follow-up',
                'Log opportunity in CRM'
            ])
        elif category == 'complaint':
            actions.extend([
                'Acknowledge complaint and apologize',
                'Investigate issue details',
                'Propose resolution or compensation',
                'Escalate to human if needed',
                'Follow up to ensure satisfaction'
            ])
        elif category == 'support':
            actions.extend([
                'Understand the issue',
                'Search knowledge base for solution',
                'Provide step-by-step guidance',
                'Offer additional resources',
                'Follow up to confirm resolution'
            ])
        elif category == 'routine':
            actions.extend([
                'Execute predefined workflow',
                'Generate required content',
                'Submit for approval if needed',
                'Publish or send',
                'Log completion'
            ])
        else:  # general
            actions.extend([
                'Analyze request intent',
                'Determine appropriate response',
                'Draft response',
                'Review and send'
            ])

        # Add source-specific actions
        if source == 'gmail' and event_type == 'new_message':
            actions.insert(0, 'Read and parse email content')
        elif source == 'linkedin' and event_type == 'connection_request':
            actions.insert(0, 'Review LinkedIn profile')
        elif source == 'linkedin' and event_type == 'new_message':
            actions.insert(0, 'Review conversation history')

        return actions

    def _estimate_steps(
        self,
        complexity: str,
        category: str,
        num_actions: int
    ) -> int:
        """Estimate number of execution steps needed."""
        base_steps = {
            'simple': 2,
            'routine': 3,
            'complex': 5,
            'critical': 7
        }.get(complexity, 3)

        # Adjust based on category
        if category in ['sales', 'complaint']:
            base_steps += 2

        # Use number of suggested actions as guide
        return max(base_steps, num_actions)

    def should_create_plan(self, event: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if an event requires a structured plan.

        Args:
            event: Event dictionary

        Returns:
            Tuple of (should_create_plan, reason)
        """
        analysis = self.analyze_event(event)

        if analysis['complexity'] == 'critical':
            return True, "Critical priority requires structured planning"

        if analysis['complexity'] == 'complex':
            return True, "Complex task requires multi-step planning"

        if analysis['category'] in ['sales', 'complaint']:
            return True, f"{analysis['category'].title()} requires careful planning"

        if analysis['estimated_steps'] > 4:
            return True, "Multi-step task requires planning"

        return False, "Simple task can be handled without formal plan"


# Global instance
_task_analyzer = None


def get_task_analyzer() -> TaskAnalyzer:
    """Get or create the global task analyzer instance."""
    global _task_analyzer
    if _task_analyzer is None:
        _task_analyzer = TaskAnalyzer()
    return _task_analyzer
