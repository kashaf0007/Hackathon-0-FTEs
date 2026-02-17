"""
Post Generator - Generates LinkedIn post content aligned with business goals.
Handles content creation, validation, approval, and publishing.
"""

import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from scripts.logger import get_logger
from scripts.business_goals_reader import get_business_goals_reader
from scripts.approval_workflow import get_approval_workflow
from scripts.mcp_client import get_mcp_client


class PostGenerator:
    """
    Generates LinkedIn posts aligned with business goals.

    Features:
    - Content generation from business goals
    - Hashtag selection
    - Content validation
    - Draft creation
    - Approval workflow integration
    - Publishing via MCP
    """

    def __init__(self):
        """Initialize post generator."""
        self.logger = get_logger()
        self.goals_reader = get_business_goals_reader()
        self.approval_workflow = get_approval_workflow()
        self.mcp_client = get_mcp_client()

    def generate_post(
        self,
        topic: Optional[str] = None,
        tone: str = 'professional'
    ) -> Dict[str, Any]:
        """
        Generate a LinkedIn post.

        Args:
            topic: Specific topic (optional, will select from goals if not provided)
            tone: Post tone (professional, inspirational, casual)

        Returns:
            Generated post dictionary with content, hashtags, validation
        """
        # Load business goals
        goals = self.goals_reader.read_goals()

        # Select topic if not provided
        if not topic:
            topic = self._select_topic(goals)

        # Generate content
        content = self._generate_content(topic, tone, goals)

        # Select hashtags
        hashtags = self._select_hashtags(topic, goals)

        # Validate content
        validation = self._validate_content(content, hashtags)

        post = {
            'topic': topic,
            'tone': tone,
            'content': content,
            'hashtags': hashtags,
            'validation': validation,
            'character_count': len(content),
            'generated_at': datetime.now().isoformat() + 'Z'
        }

        self.logger.info(
            component="content",
            action="post_generated",
            actor="post_generator",
            target="linkedin",
            details={
                'topic': topic,
                'tone': tone,
                'character_count': len(content),
                'hashtag_count': len(hashtags),
                'valid': validation['valid']
            }
        )

        return post

    def _select_topic(self, goals: Dict[str, Any]) -> str:
        """Select a topic based on business goals."""
        topics = []

        # Priority 1: Current focus
        if goals.get('current_focus'):
            topics.append(goals['current_focus'])

        # Priority 2: Value propositions
        topics.extend(goals.get('value_propositions', []))

        # Priority 3: Key themes
        for theme in goals.get('key_themes', []):
            topics.append(f"{theme} in business")

        # Fallback topics
        if not topics:
            topics = [
                'AI automation benefits for small businesses',
                'Digital transformation strategies',
                'Business efficiency and productivity',
                'Customer success and satisfaction'
            ]

        return random.choice(topics)

    def _generate_content(
        self,
        topic: str,
        tone: str,
        goals: Dict[str, Any]
    ) -> str:
        """
        Generate post content.

        Args:
            topic: Post topic
            tone: Post tone
            goals: Business goals context

        Returns:
            Generated content
        """
        # Extract context
        target_audience = goals.get('target_audience', ['business owners'])
        value_props = goals.get('value_propositions', [])

        # Generate hook
        hook = self._generate_hook(topic, tone)

        # Generate body
        body = self._generate_body(topic, tone, value_props)

        # Generate CTA
        cta = self._generate_cta(tone)

        # Combine with line breaks
        content = f"{hook}\n\n{body}\n\n{cta}"

        return content

    def _generate_hook(self, topic: str, tone: str) -> str:
        """Generate attention-grabbing hook."""
        hooks = {
            'professional': [
                f"Did you know that {topic.lower()} can transform your business operations?",
                f"The data is clear: {topic.lower()} drives measurable results.",
                f"Here's what most businesses miss about {topic.lower()}:"
            ],
            'inspirational': [
                f"The future of business is here, and it's powered by {topic.lower()}.",
                f"Imagine a world where {topic.lower()} handles the heavy lifting.",
                f"Success isn't about working harder—it's about {topic.lower()}."
            ],
            'casual': [
                f"Let's talk about {topic.lower()}.",
                f"Quick question: Are you using {topic.lower()} yet?",
                f"Here's something interesting about {topic.lower()}:"
            ]
        }

        return random.choice(hooks.get(tone, hooks['professional']))

    def _generate_body(
        self,
        topic: str,
        tone: str,
        value_props: List[str]
    ) -> str:
        """Generate post body content."""
        # Use value propositions if available
        if value_props:
            points = value_props[:3]  # Use top 3
            body_lines = [f"• {prop}" for prop in points]
            body = '\n'.join(body_lines)
        else:
            # Generic body based on topic
            body = f"Businesses using {topic.lower()} are seeing:\n"
            body += "• Increased efficiency and productivity\n"
            body += "• Reduced operational costs\n"
            body += "• Better customer satisfaction"

        return body

    def _generate_cta(self, tone: str) -> str:
        """Generate call-to-action."""
        ctas = {
            'professional': [
                "What's your experience with this? Share your thoughts below.",
                "How is your business approaching this challenge?",
                "What strategies have worked for you?"
            ],
            'inspirational': [
                "What's one step you can take today?",
                "Are you ready to make the change?",
                "What's holding you back?"
            ],
            'casual': [
                "What do you think? Drop a comment 👇",
                "Let me know your thoughts!",
                "Agree or disagree? Comment below."
            ]
        }

        return random.choice(ctas.get(tone, ctas['professional']))

    def _select_hashtags(self, topic: str, goals: Dict[str, Any]) -> List[str]:
        """Select relevant hashtags."""
        hashtags = []

        # Extract keywords from topic
        topic_words = topic.lower().split()

        # Common business hashtags
        common = ['Business', 'Entrepreneurship', 'Leadership', 'Growth', 'Innovation']

        # Topic-specific hashtags
        if 'ai' in topic_words or 'automation' in topic_words:
            hashtags.extend(['AI', 'Automation', 'Technology'])
        if 'small' in topic_words or 'business' in topic_words:
            hashtags.extend(['SmallBusiness', 'BusinessOwner'])
        if 'customer' in topic_words:
            hashtags.extend(['CustomerSuccess', 'CustomerExperience'])
        if 'digital' in topic_words:
            hashtags.extend(['DigitalTransformation', 'Innovation'])

        # Add from key themes
        for theme in goals.get('key_themes', []):
            if theme and len(hashtags) < 5:
                hashtags.append(theme.replace(' ', ''))

        # Fill with common hashtags if needed
        for tag in common:
            if len(hashtags) >= 5:
                break
            if tag not in hashtags:
                hashtags.append(tag)

        return hashtags[:5]  # Limit to 5

    def _validate_content(
        self,
        content: str,
        hashtags: List[str]
    ) -> Dict[str, Any]:
        """Validate post content."""
        warnings = []
        recommendations = []
        is_valid = True

        # Check length
        if len(content) > 3000:
            warnings.append(f"Content exceeds LinkedIn limit ({len(content)}/3000 characters)")
            is_valid = False
        elif len(content) < 50:
            recommendations.append("Content is very short - consider adding more detail")

        # Check hashtags
        if len(hashtags) > 10:
            warnings.append(f"Too many hashtags ({len(hashtags)}/10 max)")
        elif len(hashtags) == 0:
            recommendations.append("Consider adding hashtags for better reach")

        # Check for spam indicators
        spam_indicators = ['!!!', 'CLICK HERE', 'BUY NOW', 'LIMITED TIME']
        spam_found = [ind for ind in spam_indicators if ind in content.upper()]
        if spam_found:
            warnings.append(f"Potential spam indicators: {', '.join(spam_found)}")

        return {
            'valid': is_valid,
            'warnings': warnings,
            'recommendations': recommendations,
            'character_count': len(content),
            'hashtag_count': len(hashtags)
        }

    def create_draft(self, post: Dict[str, Any]) -> Path:
        """
        Create draft file in Pending_Approval/.

        Args:
            post: Post dictionary

        Returns:
            Path to draft file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_file = Path(f'AI_Employee_Vault/Pending_Approval/linkedin_post_{timestamp}.md')

        content = f"""# LinkedIn Post Draft

**Topic**: {post['topic']}
**Tone**: {post['tone']}
**Generated**: {post['generated_at']}
**Character Count**: {post['character_count']}

## Content

{post['content']}

## Hashtags

{' '.join(f'#{tag}' for tag in post['hashtags'])}

## Validation

- **Valid**: {post['validation']['valid']}
- **Warnings**: {len(post['validation']['warnings'])}
- **Recommendations**: {len(post['validation']['recommendations'])}

{self._format_validation_details(post['validation'])}

## Instructions

To approve this post:
1. Review the content above
2. Move this file to: `AI_Employee_Vault/Approved/`
3. The system will publish automatically

To reject this post:
1. Move this file to: `AI_Employee_Vault/Rejected/`
2. The system will cancel publication

**Timeout**: This request will expire in 24 hours if not approved.
"""

        draft_file.parent.mkdir(parents=True, exist_ok=True)
        draft_file.write_text(content, encoding='utf-8')

        self.logger.info(
            component="content",
            action="draft_created",
            actor="post_generator",
            target=str(draft_file),
            details={'topic': post['topic'], 'character_count': post['character_count']}
        )

        return draft_file

    def _format_validation_details(self, validation: Dict[str, Any]) -> str:
        """Format validation details for display."""
        lines = []

        if validation['warnings']:
            lines.append("### Warnings")
            for warning in validation['warnings']:
                lines.append(f"- ⚠️ {warning}")

        if validation['recommendations']:
            lines.append("\n### Recommendations")
            for rec in validation['recommendations']:
                lines.append(f"- 💡 {rec}")

        return '\n'.join(lines) if lines else "*No issues found*"

    def publish_post(
        self,
        post: Dict[str, Any],
        wait_for_approval: bool = True
    ) -> Dict[str, Any]:
        """
        Publish post to LinkedIn via MCP.

        Args:
            post: Post dictionary
            wait_for_approval: Whether to wait for approval (default: True)

        Returns:
            Publication result
        """
        action_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Request approval
        if wait_for_approval:
            approval_file = self.approval_workflow.request_approval(
                action_id=action_id,
                action_type="linkedin_post",
                description=f"Publish LinkedIn post about: {post['topic']}",
                risk_level="medium",
                action_data={
                    'content': post['content'][:200] + '...',
                    'hashtags': post['hashtags'],
                    'character_count': post['character_count']
                }
            )

            # Wait for approval
            status, _ = self.approval_workflow.wait_for_approval(
                action_id=action_id,
                poll_interval=60,
                max_wait_seconds=3600  # 1 hour max wait
            )

            if status != 'approved':
                self.logger.warning(
                    component="content",
                    action="post_not_approved",
                    actor="post_generator",
                    target=action_id,
                    details={'status': status}
                )
                return {
                    'status': 'rejected',
                    'reason': f'Approval {status}',
                    'action_id': action_id
                }

        # Publish via MCP
        try:
            result = self.mcp_client.create_linkedin_post(
                content=post['content'],
                hashtags=post['hashtags'],
                visibility='public'
            )

            self.logger.info(
                component="content",
                action="post_published",
                actor="post_generator",
                target="linkedin",
                details={
                    'post_id': result.get('post_id'),
                    'topic': post['topic'],
                    'character_count': post['character_count']
                }
            )

            return {
                'status': 'published',
                'post_id': result.get('post_id'),
                'action_id': action_id,
                'published_at': result.get('created_at')
            }

        except Exception as e:
            self.logger.error(
                component="content",
                action="post_publish_failed",
                actor="post_generator",
                target="linkedin",
                details={'error': str(e), 'action_id': action_id}
            )
            return {
                'status': 'failed',
                'error': str(e),
                'action_id': action_id
            }


# Global instance
_post_generator = None


def get_post_generator() -> PostGenerator:
    """Get or create the global post generator instance."""
    global _post_generator
    if _post_generator is None:
        _post_generator = PostGenerator()
    return _post_generator
