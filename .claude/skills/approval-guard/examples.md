# Approval Guard Skill - Examples

## Example 1: Email to New Contact (Medium Risk)

**Input**:
```json
{
  "action_id": "email_20260217_001",
  "action_type": "email_send",
  "content": "Hi, thank you for your interest in our services. I'd be happy to schedule a call.",
  "metadata": {
    "to": "potential.client@example.com",
    "subject": "Re: Question about your services",
    "contact_history": "new"
  }
}
```

**Expected Output**:
```json
{
  "risk_level": "medium",
  "requires_approval": true,
  "reason": "Email to new contact requires approval",
  "approval_request_file": "AI_Employee_Vault/Pending_Approval/email_20260217_001.md",
  "action": "wait_for_approval"
}
```

**Approval Request Created**: Yes, in Pending_Approval/

---

## Example 2: LinkedIn Post (Medium Risk)

**Input**:
```json
{
  "action_id": "linkedin_20260217_002",
  "action_type": "linkedin_post",
  "content": "Excited to announce our new AI automation services! Contact us to learn more.",
  "metadata": {
    "visibility": "public",
    "hashtags": ["AI", "Automation"]
  }
}
```

**Expected Output**:
```json
{
  "risk_level": "medium",
  "requires_approval": true,
  "reason": "Social media post requires approval",
  "approval_request_file": "AI_Employee_Vault/Pending_Approval/linkedin_20260217_002.md",
  "action": "wait_for_approval"
}
```

**Approval Request Created**: Yes, in Pending_Approval/

---

## Example 3: Payment to New Vendor (High Risk)

**Input**:
```json
{
  "action_id": "payment_20260217_003",
  "action_type": "payment",
  "content": "Process payment for software licenses",
  "metadata": {
    "amount": 750.00,
    "payee": "New Vendor LLC",
    "new_payee": true
  }
}
```

**Expected Output**:
```json
{
  "risk_level": "high",
  "requires_approval": true,
  "reason": "Payment amount $750.00 exceeds high threshold ($500.00) AND new payee requires approval",
  "approval_request_file": "AI_Employee_Vault/Pending_Approval/payment_20260217_003.md",
  "action": "wait_for_approval"
}
```

**Approval Request Created**: Yes, with HIGH RISK warning

---

## Example 4: Email to Frequent Contact (Low Risk)

**Input**:
```json
{
  "action_id": "email_20260217_004",
  "action_type": "email_send",
  "content": "Thanks for the update. I'll review and get back to you tomorrow.",
  "metadata": {
    "to": "regular.client@example.com",
    "subject": "Re: Project Update",
    "contact_history": "frequent"
  }
}
```

**Expected Output**:
```json
{
  "risk_level": "low",
  "requires_approval": false,
  "reason": "No risk indicators detected - frequent contact",
  "approval_request_file": null,
  "action": "proceed"
}
```

**Approval Request Created**: No, can proceed immediately

---

## Example 5: File Deletion (High Risk)

**Input**:
```json
{
  "action_id": "file_20260217_005",
  "action_type": "file_delete",
  "content": "Delete old project files",
  "metadata": {
    "file_path": "/important/project/data.json"
  }
}
```

**Expected Output**:
```json
{
  "risk_level": "high",
  "requires_approval": true,
  "reason": "File deletion is irreversible and requires approval",
  "approval_request_file": "AI_Employee_Vault/Pending_Approval/file_20260217_005.md",
  "action": "wait_for_approval"
}
```

**Approval Request Created**: Yes, with HIGH RISK warning

---

## Example 6: Approval Timeout

**Scenario**: Approval request created but not approved within 24 hours

**Initial Status**: `pending`

**After 24 Hours**:
- File automatically moved from Pending_Approval/ to Rejected/
- Status becomes: `timeout`
- Action is cancelled
- Timeout event logged

---

## Example 7: Approval Granted

**Scenario**: Human moves approval file to Approved/

**Status Check Result**:
```json
{
  "status": "approved",
  "file_path": "AI_Employee_Vault/Approved/email_20260217_001.md"
}
```

**Action**: Proceed with execution, log approval decision

---

## Example 8: Approval Rejected

**Scenario**: Human moves approval file to Rejected/

**Status Check Result**:
```json
{
  "status": "rejected",
  "file_path": "AI_Employee_Vault/Rejected/email_20260217_001.md"
}
```

**Action**: Cancel execution, log rejection decision

---

## Example 9: Missing Metadata (Default to High Risk)

**Input**:
```json
{
  "action_id": "unknown_20260217_006",
  "action_type": "email_send",
  "content": "Some email content",
  "metadata": {}
}
```

**Expected Output**:
```json
{
  "risk_level": "high",
  "requires_approval": true,
  "reason": "Insufficient metadata - defaulting to high risk for safety",
  "approval_request_file": "AI_Employee_Vault/Pending_Approval/unknown_20260217_006.md",
  "action": "wait_for_approval"
}
```

**Rationale**: When uncertain, always require approval

---

## Example 10: DRY_RUN Mode

**Environment**: `DRY_RUN=true`

**Input**: Any action requiring approval

**Behavior**:
- Approval request file is created
- Status checks are simulated
- No actual execution occurs
- All actions logged with "simulated" status

**Purpose**: Safe testing without real consequences

---

## Testing Checklist

- [ ] High-risk actions always require approval
- [ ] Medium-risk actions always require approval
- [ ] Low-risk actions proceed without approval
- [ ] Approval files are created with correct format
- [ ] Timeout mechanism works (auto-reject after 24h)
- [ ] Approval granted allows execution
- [ ] Approval rejected cancels execution
- [ ] All decisions are logged
- [ ] DRY_RUN mode works correctly
- [ ] Missing metadata defaults to high risk
