# LinkedIn Post Generator Skill

**Version**: 1.0.0
**Status**: Active
**Category**: Content Generation & Social Media
**Priority**: High

## Purpose

The LinkedIn Post Generator skill autonomously creates and publishes LinkedIn posts aligned with business goals, demonstrating proactive revenue-generating behavior while maintaining HITL safety through approval workflows.

## Constitutional Alignment
- **Proactivity**: Autonomously generates business content without explicit prompts
- **Revenue Orientation**: Creates sales-focused content aligned with business goals
- **HITL Safety**: All posts require approval before publishing
- **Transparency**: All post generation and publishing logged
- **Local-First**: Drafts stored locally before approval

## Capabilities

- **Business Goal Analysis**: Read and understand Business_Goals.md
- **Content Generation**: Create engaging LinkedIn posts aligned with goals
- **Hashtag Selection**: Choose relevant hashtags for reach
- **Content Validation**: Check post length, tone, and compliance
- **Approval Integration**: Request approval for all public posts
- **Publishing via MCP**: Execute post creation through LinkedIn MCP server
- **Performance Tracking**: Monitor post engagement metrics

## When to Use

This skill is invoked when:

1. **Scheduled Posting**: Weekly/daily scheduled LinkedIn posts
2. **Business Milestones**: Announce achievements or updates
3. **Thought Leadership**: Share industry insights
4. **Product Announcements**: Promote services or features
5. **Engagement Campaigns**: Drive audience interaction

## Input Format

```json
{
  "trigger": "scheduled|manual|milestone",
  "topic": "Optional specific topic",
  "tone": "professional|casual|inspirational",
  "include_cta": true,
  "max_hashtags": 5
}
```

## Output Format

```json
{
  "status": "draft_created|published|failed",
  "draft_file": "AI_Employee_Vault/Pending_Approval/linkedin_post_20260217.md",
  "content": "Post content preview",
  "hashtags": ["AI", "Automation", "Business"],
  "requires_approval": true,
  "approval_id": "linkedin_post_20260217_001",
  "post_id": "linkedin_post_123" (after publishing)
}
```

## Execution Flow

### Phase 1: Content Planning
1. **Read Business Goals**: Load Business_Goals.md to understand priorities
2. **Select Topic**: Choose topic aligned with current business focus
3. **Determine Tone**: Select appropriate tone (professional, inspirational, etc.)
4. **Plan Structure**: Outline post structure (hook, body, CTA)

### Phase 2: Content Generation
1. **Write Hook**: Create attention-grabbing opening
2. **Develop Body**: Expand on topic with value proposition
3. **Add CTA**: Include clear call-to-action
4. **Select Hashtags**: Choose 3-5 relevant hashtags
5. **Validate Content**: Check length, tone, compliance

### Phase 3: Approval
1. **Create Draft File**: Save draft in Pending_Approval/
2. **Request Approval**: Create approval request with preview
3. **Wait for Decision**: Poll for human approval
4. **Handle Rejection**: If rejected, log and archive

### Phase 4: Publishing
1. **Validate Content**: Final validation before publishing
2. **Call MCP Server**: Execute create_post via LinkedIn MCP
3. **Verify Publication**: Confirm post was published
4. **Log Outcome**: Record post ID and timestamp
5. **Move to Done**: Archive draft file

## Content Generation Guidelines

### Post Structure
1. **Hook** (1-2 sentences): Grab attention with question, stat, or bold statement
2. **Body** (3-5 sentences): Provide value, insight, or story
3. **CTA** (1 sentence): Clear call-to-action (comment, share, connect, visit)

### Tone Guidelines
- **Professional**: Industry insights, data-driven, authoritative
- **Inspirational**: Motivational, story-driven, aspirational
- **Casual**: Conversational, relatable, friendly

### Content Rules
- Maximum 3000 characters (LinkedIn limit)
- Optimal length: 150-300 characters for engagement
- Use line breaks for readability
- Include 3-5 relevant hashtags
- Always include call-to-action
- Avoid spam indicators (excessive emojis, ALL CAPS, multiple exclamation marks)

## Business Goal Integration

Read Business_Goals.md to extract:
- **Primary Goals**: Revenue targets, customer acquisition, brand awareness
- **Target Audience**: Who we're trying to reach
- **Value Propositions**: What we offer and why it matters
- **Current Focus**: Active campaigns or initiatives

Generate posts that:
- Align with primary goals
- Speak to target audience
- Highlight value propositions
- Support current focus areas

## Risk Classification

### High Risk (ALWAYS require approval)
- All LinkedIn posts (public visibility)
- Posts mentioning competitors
- Posts with pricing information
- Posts making claims or guarantees

### Approval Process
Every LinkedIn post requires approval because:
- Public visibility impacts brand reputation
- Content represents company voice
- Mistakes are difficult to undo
- Compliance and legal considerations

## Integration Points

- **Business Goals Reader**: Uses `scripts/business_goals_reader.py` to load goals
- **Post Generator**: Uses `scripts/post_generator.py` for content creation
- **Content Validator**: Uses LinkedIn MCP `validate_content` method
- **Approval Workflow**: Uses `scripts/approval_workflow.py` for HITL approval
- **LinkedIn MCP**: Uses `mcp_servers/linkedin_server.py` for publishing
- **Logger**: Logs all operations via `scripts/logger.py`

## Error Handling

### Content Generation Failures
- Unable to read Business_Goals.md → Use default topics
- Content validation fails → Regenerate with corrections
- No suitable topic found → Use general thought leadership

### Publishing Failures
- LinkedIn login fails → Log error, create escalation task
- Post creation fails → Retry up to 3 times
- Rate limit exceeded → Queue for later
- Network timeout → Retry with exponential backoff

### Approval Timeout
- No decision within 24 hours → Auto-reject
- Create task in Needs_Action/ for review
- Log timeout event

## Logging Requirements

Must log all post generation operations:
- **Content Generated**: Topic, length, hashtags
- **Validation**: Validation result, warnings
- **Approval Request**: Approval ID, draft file path
- **Publishing**: Post ID, timestamp, outcome
- **Engagement**: Views, likes, comments (when available)

Log format:
```json
{
  "timestamp": "2026-02-17T10:30:00Z",
  "component": "content",
  "action": "post_generated|post_published",
  "actor": "linkedin_post_generator",
  "target": "linkedin",
  "status": "success",
  "details": {
    "post_id": "linkedin_post_123",
    "topic": "AI automation benefits",
    "hashtags": ["AI", "Automation"],
    "requires_approval": true
  }
}
```

## Examples

See `examples.md` for detailed scenarios covering:
- Weekly scheduled post generation
- Milestone announcement post
- Thought leadership post
- Product feature announcement
- Engagement campaign post
- Approval rejection handling
- Publishing failure recovery

## Testing

Run tests with:
```bash
python -m pytest tests/test_linkedin_post_generator.py -v
```

Test coverage includes:
- Business goal parsing
- Content generation quality
- Hashtag selection relevance
- Content validation accuracy
- Approval workflow integration
- MCP publishing integration
- Error handling and retry logic

## Configuration

Environment variables:
- `LINKEDIN_POST_SCHEDULE`: Cron expression for scheduled posts (default: weekly Monday 9am)
- `LINKEDIN_MAX_HASHTAGS`: Maximum hashtags per post (default: 5)
- `DRY_RUN`: If "true", simulate post creation without publishing

## Dependencies

- `scripts/business_goals_reader.py`: Business goal parsing
- `scripts/post_generator.py`: Content generation
- `scripts/approval_workflow.py`: HITL approval
- `scripts/mcp_client.py`: MCP client for LinkedIn server
- `mcp_servers/linkedin_server.py`: LinkedIn MCP server
- `scripts/logger.py`: Audit logging

## Maintenance

- Review post engagement metrics weekly
- Update content templates based on performance
- Adjust hashtag strategy based on reach
- Monitor approval rejection reasons
- Refine business goal alignment

## Version History

- **1.0.0** (2026-02-17): Initial implementation for Silver Tier
  - Autonomous post generation from business goals
  - Content validation and optimization
  - Approval workflow integration
  - Publishing via LinkedIn MCP server
  - Complete audit logging

## Completion Condition

Post generation completes when:
- Business goals analyzed
- Content generated and validated
- Approval obtained
- Post published via MCP (or simulated in DRY_RUN)
- Post ID recorded
- All operations logged

**Verification**:
- Draft file created in Pending_Approval/
- Approval file moved to Approved/
- Post ID returned from LinkedIn
- Complete audit trail in logs
