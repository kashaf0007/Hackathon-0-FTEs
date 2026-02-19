# WhatsApp Watcher Setup Guide

This guide explains how to set up and use the WhatsApp watcher for the Silver Tier AI Employee system.

## Architecture Overview

The WhatsApp integration uses a two-component architecture:

1. **Node.js Bridge Server** (`whatsapp_bridge.js`): Handles WhatsApp Web session management using `whatsapp-web.js`
2. **Python Watcher** (`AI_Employee_Vault/Watchers/whatsapp_watcher.py`): Polls the bridge for new messages and creates events

This architecture separates concerns: Node.js handles the complex WhatsApp Web automation, while Python integrates with the existing AI Employee system.

## Prerequisites

- **Node.js**: Version 16.0.0 or higher
- **Python**: Version 3.11 or higher
- **Chrome/Chromium**: Required by Puppeteer (installed automatically with whatsapp-web.js)
- **WhatsApp Account**: Active WhatsApp account on your phone

## Installation

### Step 1: Install Node.js Dependencies

```bash
# Install Node.js packages
npm install
```

This installs:
- `express`: HTTP server for the bridge API
- `whatsapp-web.js`: WhatsApp Web automation library
- `qrcode`: QR code generation for authentication
- `qrcode-terminal`: Display QR codes in terminal

### Step 2: Configure Environment Variables

Copy `.env.example` to `.env` and update WhatsApp settings:

```bash
# WhatsApp Configuration
WHATSAPP_ENABLED=true
WHATSAPP_SESSION_PATH=.wwebjs_auth
WHATSAPP_BRIDGE_PORT=5002
WHATSAPP_BRIDGE_URL=http://localhost:5002
```

### Step 3: Update Watcher Configuration

Edit `AI_Employee_Vault/Watchers/watcher_config.json`:

```json
{
  "watchers": {
    "whatsapp": {
      "enabled": true,
      "poll_interval_seconds": 300,
      "bridge_url": "http://localhost:5002",
      "features": {
        "personal_messages": true,
        "group_messages": false
      }
    }
  }
}
```

**Configuration Options**:
- `enabled`: Set to `true` to activate WhatsApp watcher
- `poll_interval_seconds`: How often to check for new messages (default: 300 = 5 minutes)
- `bridge_url`: URL of the Node.js bridge server
- `personal_messages`: Monitor personal chats (recommended: `true`)
- `group_messages`: Monitor group chats (recommended: `false` to reduce noise)

## Usage

### Starting the WhatsApp Bridge

The bridge server must be running before the Python watcher can function.

```bash
# Start the bridge server
node whatsapp_bridge.js
```

**First-time authentication**:
1. The bridge will display a QR code in the terminal
2. Open WhatsApp on your phone
3. Go to Settings → Linked Devices → Link a Device
4. Scan the QR code displayed in the terminal
5. Once authenticated, the session is saved to `.wwebjs_auth/` directory

**Subsequent runs**:
- The bridge will automatically use the saved session
- No QR code scanning needed unless session expires

### Running the WhatsApp Watcher

Once the bridge is running and authenticated:

```bash
# Test the watcher (single poll)
python scripts/run_watchers.py --watcher whatsapp --test

# Run the watcher once (for scheduled execution)
python scripts/run_watchers.py --watcher whatsapp

# Check bridge connectivity
python AI_Employee_Vault/Watchers/whatsapp_watcher.py --check-bridge
```

### Running All Watchers Together

```bash
# Run all enabled watchers (Gmail, LinkedIn, WhatsApp)
python scripts/run_watchers.py
```

## How It Works

### Message Flow

1. **WhatsApp receives message** → WhatsApp Web session detects new message
2. **Bridge captures message** → Node.js bridge stores message in unprocessed queue
3. **Python watcher polls** → Watcher requests new messages via HTTP API
4. **Event creation** → Watcher normalizes message and creates event file in `Needs_Action/`
5. **Reasoning loop processes** → Claude reasoning loop analyzes event and generates Plan.md
6. **Action execution** → System executes planned actions (with approval if needed)
7. **Mark processed** → Watcher marks message as processed in bridge

### Bridge API Endpoints

The Node.js bridge exposes these HTTP endpoints:

- `GET /health` - Check bridge status and session readiness
- `GET /qr` - Get QR code for authentication (if not authenticated)
- `GET /messages` - Fetch unprocessed messages
- `POST /mark-processed` - Mark message as processed
- `POST /send` - Send WhatsApp message (for future reply functionality)
- `POST /logout` - Logout and clear session

### Event Format

WhatsApp messages are normalized to this standard event format:

```json
{
  "event_id": "20260220_143022_whatsapp_a3f8d1",
  "source": "whatsapp",
  "type": "whatsapp_message",
  "timestamp": "2026-02-20T14:30:22Z",
  "priority": "medium",
  "content": {
    "subject": "WhatsApp from John Doe",
    "body": "Hey, can we schedule a call?",
    "from": "John Doe",
    "to": "me",
    "attachments": []
  },
  "metadata": {
    "message_id": "true_1234567890@c.us_ABCDEF123456",
    "from_number": "1234567890@c.us",
    "is_group": false,
    "group_name": "",
    "contact_history": "known",
    "has_media": false,
    "labels": ["whatsapp", "personal"],
    "is_reply": false,
    "raw_data": {
      "chat_id": "1234567890@c.us",
      "quoted_msg": null
    }
  },
  "created_at": "2026-02-20T14:30:22Z",
  "processed": false
}
```

## Integration with Reasoning Loop

The reasoning loop automatically processes WhatsApp events:

1. **Event Detection**: Watcher creates event file in `Needs_Action/`
2. **Task Analysis**: Reasoning loop classifies message (sales, support, complaint, etc.)
3. **Plan Generation**: For complex tasks, generates structured Plan.md
4. **Execution**: Executes planned actions step-by-step
5. **Approval**: Sensitive actions (replies, external communications) require human approval
6. **Completion**: Event moved to `Done/` when complete

### Approval Workflow

WhatsApp replies follow the Human-in-the-Loop (HITL) approval process:

1. Reasoning loop drafts a reply
2. Reply saved to `Pending_Approval/` directory
3. Human reviews and approves/rejects
4. If approved, reply sent via bridge `/send` endpoint
5. All actions logged in `Logs/`

## Troubleshooting

### Bridge Won't Start

**Error**: `Cannot find module 'whatsapp-web.js'`
- **Solution**: Run `npm install` to install dependencies

**Error**: `Port 5002 already in use`
- **Solution**: Change `WHATSAPP_BRIDGE_PORT` in `.env` or kill the process using port 5002

### Authentication Issues

**Problem**: QR code not displaying
- **Solution**: Check terminal supports Unicode characters, or check bridge logs for QR code URL

**Problem**: Session expired
- **Solution**: Delete `.wwebjs_auth/` directory and re-authenticate with QR code

**Problem**: "Authentication failure" message
- **Solution**: Ensure WhatsApp is active on your phone and try re-scanning QR code

### Watcher Issues

**Error**: `Bridge unreachable`
- **Solution**: Ensure Node.js bridge is running (`node whatsapp_bridge.js`)
- **Solution**: Check `WHATSAPP_BRIDGE_URL` in configuration matches bridge server

**Problem**: No messages detected
- **Solution**: Check bridge status: `python AI_Employee_Vault/Watchers/whatsapp_watcher.py --check-bridge`
- **Solution**: Verify `personal_messages` is enabled in `watcher_config.json`
- **Solution**: Send a test message to your WhatsApp and check bridge logs

### Performance Issues

**Problem**: High memory usage
- **Solution**: Restart bridge server periodically (e.g., daily via cron)
- **Solution**: Reduce `poll_interval_seconds` to check less frequently

**Problem**: Slow message detection
- **Solution**: Decrease `poll_interval_seconds` in configuration (minimum: 60 seconds recommended)

## Security Considerations

### Session Security

- **Local Storage**: WhatsApp session stored locally in `.wwebjs_auth/`
- **Gitignore**: Ensure `.wwebjs_auth/` is in `.gitignore` (already configured)
- **Access Control**: Protect session directory with appropriate file permissions

### Message Privacy

- **Local Processing**: All messages processed locally, never sent to external services
- **Logging**: Messages logged to `Logs/` directory - ensure proper access controls
- **Attachments**: Media attachments stored as base64 in event files

### Approval Requirements

Per constitutional principles, WhatsApp replies require approval:
- **New Contacts**: Always require approval
- **Known Contacts**: Require approval for sensitive topics
- **Automated Replies**: Never send without human review

## Production Deployment

### Running as a Service

**Linux (systemd)**:

Create `/etc/systemd/system/whatsapp-bridge.service`:

```ini
[Unit]
Description=WhatsApp Bridge Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/AI-Employee-Hackathon
ExecStart=/usr/bin/node whatsapp_bridge.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable whatsapp-bridge
sudo systemctl start whatsapp-bridge
```

**Windows (Task Scheduler)**:

1. Open Task Scheduler
2. Create Basic Task → "WhatsApp Bridge"
3. Trigger: At startup
4. Action: Start a program
5. Program: `node.exe`
6. Arguments: `whatsapp_bridge.js`
7. Start in: `C:\path\to\AI-Employee-Hackathon`

### Monitoring

Monitor bridge health:
```bash
# Check if bridge is running
curl http://localhost:5002/health

# Expected response:
# {"status":"ok","ready":true,"qr_available":false,"unprocessed_count":0}
```

Add to monitoring script or health check system.

## Testing

### Manual Testing

1. **Test bridge connectivity**:
   ```bash
   python AI_Employee_Vault/Watchers/whatsapp_watcher.py --check-bridge
   ```

2. **Test message detection**:
   - Send a WhatsApp message to yourself
   - Run: `python scripts/run_watchers.py --watcher whatsapp --test`
   - Check `Needs_Action/` for new event file

3. **Test end-to-end flow**:
   - Send a test message
   - Run watcher to create event
   - Check reasoning loop processes event
   - Verify Plan.md created
   - Check approval workflow if reply needed

### Automated Testing

```bash
# Run integration tests
python -m pytest tests/integration/test_whatsapp_watcher.py -v
```

## Maintenance

### Regular Tasks

- **Weekly**: Review processed messages in `Done/` directory
- **Monthly**: Restart bridge server to clear memory
- **Quarterly**: Update Node.js dependencies (`npm update`)

### Session Management

- **Session Expiry**: WhatsApp sessions typically last 2-4 weeks
- **Re-authentication**: If session expires, re-scan QR code
- **Backup**: Consider backing up `.wwebjs_auth/` directory (encrypted)

## Limitations

- **WhatsApp Web Dependency**: Requires active WhatsApp Web session
- **Single Device**: Only one bridge instance per WhatsApp account
- **Rate Limits**: WhatsApp may rate-limit automated messages
- **Group Messages**: Limited support (disabled by default to reduce noise)
- **Media Handling**: Large media files may impact performance

## Future Enhancements

Potential improvements for future versions:

- **Reply Functionality**: Implement automated replies via bridge `/send` endpoint
- **Media Processing**: Enhanced handling of images, videos, documents
- **Group Chat Support**: Better filtering and handling of group messages
- **Contact Management**: Automatic contact classification and history tracking
- **Message Templates**: Pre-approved response templates for common scenarios
- **Multi-Account**: Support multiple WhatsApp accounts with separate bridges

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review bridge logs: `node whatsapp_bridge.js` output
3. Review watcher logs: `AI_Employee_Vault/Logs/`
4. Check GitHub issues: [project repository]

## Version History

- **1.0.0** (2026-02-20): Initial WhatsApp watcher implementation
  - Node.js bridge with whatsapp-web.js
  - Python watcher with event normalization
  - Integration with reasoning loop
  - HITL approval workflow support
