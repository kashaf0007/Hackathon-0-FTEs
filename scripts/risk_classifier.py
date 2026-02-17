"""
RiskClassifier for assessing action risk levels.
Uses keyword-based classification with configurable rules.
"""

from typing import Dict, Any, Tuple, List


class RiskClassifier:
    """
    Classifies actions into risk levels (low, medium, high) based on keywords and rules.
    """

    # High-risk keywords
    HIGH_RISK_KEYWORDS = [
        'payment', 'transfer', 'invoice', 'legal', 'contract',
        'medical', 'health', 'condolence', 'lawsuit', 'terminate',
        'delete', 'remove', 'destroy', 'cancel', 'refund'
    ]

    # Medium-risk keywords
    MEDIUM_RISK_KEYWORDS = [
        'email', 'send', 'post', 'publish', 'share', 'reply',
        'new contact', 'unknown', 'first time', 'external',
        'public', 'broadcast', 'announce'
    ]

    # Sensitive contexts
    SENSITIVE_CONTEXTS = [
        'emotional', 'conflict', 'negotiation', 'complaint',
        'dispute', 'disagreement', 'criticism', 'feedback'
    ]

    # Payment thresholds
    PAYMENT_THRESHOLD_HIGH = 500  # USD
    PAYMENT_THRESHOLD_MEDIUM = 50  # USD

    def __init__(self):
        """Initialize risk classifier with default rules."""
        pass

    def classify(
        self,
        action_type: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Classify action risk level.

        Args:
            action_type: Type of action (e.g., 'email_send', 'linkedin_post', 'payment')
            content: Action content or description
            metadata: Additional metadata (e.g., amount, recipient, contact_history)

        Returns:
            Tuple of (risk_level, reason)
            risk_level: 'low', 'medium', or 'high'
            reason: Explanation for the classification
        """
        content_lower = content.lower()

        # Check for high-risk keywords
        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in content_lower:
                return 'high', f'Contains high-risk keyword: {keyword}'

        # Check payment-specific rules
        if action_type == 'payment':
            amount = metadata.get('amount', 0)
            new_payee = metadata.get('new_payee', False)

            if amount > self.PAYMENT_THRESHOLD_HIGH:
                return 'high', f'Payment amount ${amount} exceeds high threshold (${self.PAYMENT_THRESHOLD_HIGH})'

            if new_payee:
                return 'high', 'New payee requires approval'

            if amount > self.PAYMENT_THRESHOLD_MEDIUM:
                return 'medium', f'Payment amount ${amount} exceeds medium threshold (${self.PAYMENT_THRESHOLD_MEDIUM})'

        # Check for medium-risk keywords
        for keyword in self.MEDIUM_RISK_KEYWORDS:
            if keyword in content_lower:
                return 'medium', f'Contains medium-risk keyword: {keyword}'

        # Check for sensitive contexts
        for context in self.SENSITIVE_CONTEXTS:
            if context in content_lower:
                return 'medium', f'Sensitive context detected: {context}'

        # Social media always requires approval
        if action_type in ['linkedin_post', 'twitter_post', 'facebook_post']:
            return 'medium', 'Social media post requires approval'

        # Email to new contacts
        if action_type == 'email_send':
            contact_history = metadata.get('contact_history', 'unknown')
            if contact_history == 'new':
                return 'medium', 'Email to new contact requires approval'

        # File deletion
        if action_type == 'file_delete':
            return 'high', 'File deletion is irreversible and requires approval'

        # Default: low risk
        return 'low', 'No risk indicators detected'

    def requires_approval(self, risk_level: str) -> bool:
        """
        Determine if risk level requires human approval.

        Args:
            risk_level: Risk level ('low', 'medium', 'high')

        Returns:
            True if approval required, False otherwise
        """
        return risk_level in ['medium', 'high']

    def get_risk_factors(self, content: str) -> List[str]:
        """
        Get all risk factors found in content.

        Args:
            content: Content to analyze

        Returns:
            List of risk factors found
        """
        content_lower = content.lower()
        factors = []

        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in content_lower:
                factors.append(f'High-risk keyword: {keyword}')

        for keyword in self.MEDIUM_RISK_KEYWORDS:
            if keyword in content_lower:
                factors.append(f'Medium-risk keyword: {keyword}')

        for context in self.SENSITIVE_CONTEXTS:
            if context in content_lower:
                factors.append(f'Sensitive context: {context}')

        return factors


# Global classifier instance
_classifier = None


def get_classifier() -> RiskClassifier:
    """Get or create the global risk classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = RiskClassifier()
    return _classifier


# Alias for compatibility
def get_risk_classifier() -> RiskClassifier:
    """Get or create the global risk classifier instance (alias)."""
    return get_classifier()


def classify_action(
    action_type: str,
    content: str,
    metadata: Dict[str, Any] = None
) -> Tuple[str, str]:
    """
    Convenience function to classify an action.

    Args:
        action_type: Type of action
        content: Action content
        metadata: Additional metadata

    Returns:
        Tuple of (risk_level, reason)
    """
    return get_classifier().classify(action_type, content, metadata or {})
