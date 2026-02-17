# Sample Approval Request 1: LinkedIn Post

**Action ID**: linkedin_post_20260217_001
**Risk Level**: medium
**Created**: 2026-02-17T15:00:00Z
**Expires**: 2026-02-18T15:00:00Z
**Related Plan**: plan_20260217_001

## Description

Post to LinkedIn about new AI automation consulting services offering.

## Risk Assessment

- **Risk Level**: medium
- **Risk Factors**:
  - Public post visible to all connections
  - Represents company brand
  - Contains business claims
- **Potential Impact**: Brand reputation if content is inappropriate or contains errors

## Action Details

- **Type**: linkedin_post
- **Target**: LinkedIn profile
- **Content**:

```
Excited to announce our new AI automation consulting services! 🚀

We help businesses:
- Automate routine tasks
- Reduce operational costs by 40%
- Free up time for strategic work

Interested in learning more? Let's connect and discuss how automation can transform your business.

#AI #Automation #Consulting #BusinessTransformation
```

## Instructions

To approve this action:
1. Review the description and risk assessment above
2. Move this file to: `AI_Employee_Vault/Approved/`
3. The system will execute the action automatically

To reject this action:
1. Move this file to: `AI_Employee_Vault/Rejected/`
2. The system will cancel the action

**Timeout**: This request will expire in 24 hours if not approved.

## Metadata

```json
{
  "action_id": "linkedin_post_20260217_001",
  "action_type": "linkedin_post",
  "risk_level": "medium",
  "created_at": "2026-02-17T15:00:00Z",
  "expires_at": "2026-02-18T15:00:00Z",
  "plan_id": "plan_20260217_001",
  "action_data": {
    "content": "Excited to announce our new AI automation consulting services...",
    "hashtags": ["AI", "Automation", "Consulting", "BusinessTransformation"],
    "visibility": "public"
  }
}
```

---

# Sample Approval Request 2: Email Send

**Action ID**: email_send_20260217_002
**Risk Level**: medium
**Created**: 2026-02-17T16:30:00Z
**Expires**: 2026-02-18T16:30:00Z
**Related Plan**: plan_20260217_002

## Description

Send email reply to new contact inquiring about consulting services.

## Risk Assessment

- **Risk Level**: medium
- **Risk Factors**:
  - New contact (first interaction)
  - Business communication
  - Represents company professionally
- **Potential Impact**: First impression with potential client

## Action Details

- **Type**: email_send
- **Target**: potential.client@example.com
- **Subject**: Re: Question about your services
- **Content**:

```
Hi [Name],

Thank you for your interest in our AI consulting services!

I'd be happy to schedule a call to discuss how we can help your business. We specialize in:
- Process automation
- AI integration
- Workflow optimization

Are you available for a 30-minute call this week? Please let me know what times work best for you.

Best regards,
[Your Name]
```

## Instructions

To approve this action:
1. Review the email content above
2. Move this file to: `AI_Employee_Vault/Approved/`
3. The system will send the email automatically

To reject this action:
1. Move this file to: `AI_Employee_Vault/Rejected/`
2. The system will cancel the email

**Timeout**: This request will expire in 24 hours if not approved.

## Metadata

```json
{
  "action_id": "email_send_20260217_002",
  "action_type": "email_send",
  "risk_level": "medium",
  "created_at": "2026-02-17T16:30:00Z",
  "expires_at": "2026-02-18T16:30:00Z",
  "plan_id": "plan_20260217_002",
  "action_data": {
    "to": "potential.client@example.com",
    "subject": "Re: Question about your services",
    "body_type": "plain",
    "contact_history": "new"
  }
}
```

---

# Sample Approval Request 3: Payment (High Risk)

**Action ID**: payment_20260217_003
**Risk Level**: high
**Created**: 2026-02-17T18:00:00Z
**Expires**: 2026-02-18T18:00:00Z
**Related Plan**: plan_20260217_003

## Description

Process payment of $750 to new vendor for software licenses.

## Risk Assessment

- **Risk Level**: high
- **Risk Factors**:
  - Payment amount exceeds $500 threshold
  - New payee (first transaction)
  - Financial transaction is irreversible
- **Potential Impact**: Financial loss if payment is fraudulent or incorrect

## Action Details

- **Type**: payment
- **Target**: New Vendor LLC
- **Amount**: $750.00 USD
- **Purpose**: Software license renewal
- **Payment Method**: Bank transfer

## Instructions

To approve this action:
1. **VERIFY** the vendor details and invoice
2. **CONFIRM** the amount is correct
3. Move this file to: `AI_Employee_Vault/Approved/`
4. The system will process the payment

To reject this action:
1. Move this file to: `AI_Employee_Vault/Rejected/`
2. The system will cancel the payment

**⚠️ WARNING**: This is a high-risk financial transaction. Please review carefully before approving.

**Timeout**: This request will expire in 24 hours if not approved.

## Metadata

```json
{
  "action_id": "payment_20260217_003",
  "action_type": "payment",
  "risk_level": "high",
  "created_at": "2026-02-17T18:00:00Z",
  "expires_at": "2026-02-18T18:00:00Z",
  "plan_id": "plan_20260217_003",
  "action_data": {
    "payee": "New Vendor LLC",
    "amount": 750.00,
    "currency": "USD",
    "new_payee": true,
    "purpose": "Software license renewal"
  }
}
```
