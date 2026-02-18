# Gmail API Setup Guide

## Prerequisites
- Google account with Gmail
- Access to Google Cloud Console

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "AI Employee" and click "Create"

### 2. Enable Gmail API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on it and press "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: AI Employee
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip this (click "Save and Continue")
   - Test users: Add your Gmail address
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: Desktop app
   - Name: AI Employee Gmail Watcher
   - Click "Create"

5. Download the JSON file:
   - Click the download button (⬇️) next to your new credential
   - Save it as `gmail_credentials.json`

### 4. Install Credentials

Move the downloaded file to the correct location:

```powershell
# Move to the Watchers directory
Move-Item -Path "Downloads\gmail_credentials.json" -Destination "AI_Employee_Vault\Watchers\gmail_credentials.json"
```

Or manually copy it to:
```
AI_Employee_Vault\Watchers\gmail_credentials.json
```

### 5. First-Time Authentication

Run the authentication flow:

```powershell
$env:PYTHONPATH = $PWD
python AI_Employee_Vault/Watchers/gmail_watcher.py --authenticate
```

This will:
1. Open your browser
2. Ask you to sign in to Google
3. Show a warning "Google hasn't verified this app" - Click "Advanced" → "Go to AI Employee (unsafe)"
4. Grant permissions to read Gmail
5. Save the token to `gmail_token.json`

### 6. Test Gmail Watcher

```powershell
$env:PYTHONPATH = $PWD
python AI_Employee_Vault/Watchers/gmail_watcher.py --test
```

### 7. Enable in Config

Edit `AI_Employee_Vault/Watchers/watcher_config.json`:

```json
"gmail": {
  "enabled": true,
  ...
}
```

### 8. Run Orchestrator

```powershell
.\run_test.ps1
```

## Troubleshooting

**"Access blocked: This app's request is invalid"**
- Make sure you added your email as a test user in OAuth consent screen

**"The file token.json is missing"**
- Run the `--authenticate` command first

**"Invalid grant" error**
- Delete `gmail_token.json` and re-authenticate

## Security Notes

- `gmail_credentials.json` contains your OAuth client ID and secret
- `gmail_token.json` contains your access token
- Both files are in `.gitignore` and should NEVER be committed
- The app only has read-only access to Gmail
- You can revoke access anytime at https://myaccount.google.com/permissions

## Alternative: Use Without Gmail

If you don't need Gmail monitoring, keep it disabled in the config. The system works fine without it.
