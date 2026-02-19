/**
 * WhatsApp Bridge Server
 *
 * Node.js bridge using whatsapp-web.js to provide HTTP API for Python watcher.
 * Handles WhatsApp session management, QR code generation, and message fetching.
 */

const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');

const app = express();
app.use(express.json());

// Configuration
const PORT = process.env.WHATSAPP_BRIDGE_PORT || 5002;
const SESSION_PATH = process.env.WHATSAPP_SESSION_PATH || '.wwebjs_auth';

// State
let client = null;
let isReady = false;
let currentQR = null;
let unprocessedMessages = [];

// Initialize WhatsApp client
function initializeClient() {
    console.log('🔄 Initializing WhatsApp client...');

    client = new Client({
        authStrategy: new LocalAuth({
            dataPath: SESSION_PATH
        }),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        }
    });

    // QR code event
    client.on('qr', async (qr) => {
        console.log('📱 QR Code received. Scan with WhatsApp to authenticate.');
        try {
            currentQR = await qrcode.toString(qr, { type: 'terminal', small: true });
            console.log(currentQR);
        } catch (err) {
            console.error('Error generating QR code:', err);
            currentQR = qr;
        }
    });

    // Ready event
    client.on('ready', () => {
        console.log('✅ WhatsApp client is ready!');
        isReady = true;
        currentQR = null;
    });

    // Authenticated event
    client.on('authenticated', () => {
        console.log('✅ WhatsApp authenticated');
    });

    // Authentication failure event
    client.on('auth_failure', (msg) => {
        console.error('❌ Authentication failure:', msg);
        isReady = false;
    });

    // Disconnected event
    client.on('disconnected', (reason) => {
        console.log('⚠️  WhatsApp disconnected:', reason);
        isReady = false;
        currentQR = null;
    });

    // Message event
    client.on('message', async (message) => {
        try {
            const chat = await message.getChat();
            const contact = await message.getContact();

            // Build message object
            const messageData = {
                id: message.id._serialized,
                body: message.body,
                from: message.from,
                to: message.to,
                timestamp: new Date(message.timestamp * 1000).toISOString(),
                isGroup: chat.isGroup,
                groupName: chat.isGroup ? chat.name : '',
                chatId: chat.id._serialized,
                contactName: contact.pushname || contact.name || message.from,
                hasMedia: message.hasMedia,
                isImportant: false, // Can be enhanced with custom logic
                quotedMsg: message.hasQuotedMsg ? message._data.quotedMsg : null,
                attachments: []
            };

            // Handle media attachments
            if (message.hasMedia) {
                try {
                    const media = await message.downloadMedia();
                    messageData.attachments.push({
                        mimetype: media.mimetype,
                        filename: media.filename || 'attachment',
                        data: media.data // Base64 encoded
                    });
                } catch (err) {
                    console.error('Error downloading media:', err);
                }
            }

            // Add to unprocessed messages queue
            unprocessedMessages.push(messageData);

            console.log(`📨 New message from ${messageData.contactName}: ${message.body.substring(0, 50)}...`);

        } catch (err) {
            console.error('Error processing message:', err);
        }
    });

    // Initialize client
    client.initialize();
}

// API Routes

/**
 * Health check endpoint
 * Returns bridge status and WhatsApp session readiness
 */
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        ready: isReady,
        qr_available: currentQR !== null,
        unprocessed_count: unprocessedMessages.length
    });
});

/**
 * Get QR code for authentication
 * Returns QR code string if available
 */
app.get('/qr', (req, res) => {
    if (currentQR) {
        res.json({
            qr: currentQR,
            message: 'Scan this QR code with WhatsApp'
        });
    } else if (isReady) {
        res.json({
            qr: null,
            message: 'Already authenticated'
        });
    } else {
        res.json({
            qr: null,
            message: 'QR code not yet generated'
        });
    }
});

/**
 * Get unprocessed messages
 * Returns list of messages that haven't been marked as processed
 */
app.get('/messages', (req, res) => {
    if (!isReady) {
        return res.status(503).json({
            error: 'WhatsApp client not ready',
            messages: []
        });
    }

    const personal = req.query.personal === 'true' || req.query.personal === true;
    const group = req.query.group === 'true' || req.query.group === true;

    // Filter messages based on preferences
    let filteredMessages = unprocessedMessages;

    if (!group) {
        filteredMessages = filteredMessages.filter(msg => !msg.isGroup);
    }

    if (!personal) {
        filteredMessages = filteredMessages.filter(msg => msg.isGroup);
    }

    res.json({
        messages: filteredMessages,
        count: filteredMessages.length
    });
});

/**
 * Mark message as processed
 * Removes message from unprocessed queue
 */
app.post('/mark-processed', (req, res) => {
    const { message_id } = req.body;

    if (!message_id) {
        return res.status(400).json({
            error: 'message_id is required'
        });
    }

    const initialLength = unprocessedMessages.length;
    unprocessedMessages = unprocessedMessages.filter(msg => msg.id !== message_id);
    const removed = initialLength - unprocessedMessages.length;

    res.json({
        success: removed > 0,
        removed_count: removed
    });
});

/**
 * Send message (for future use with approval workflow)
 * Sends a WhatsApp message to specified recipient
 */
app.post('/send', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({
            error: 'WhatsApp client not ready'
        });
    }

    const { to, message } = req.body;

    if (!to || !message) {
        return res.status(400).json({
            error: 'to and message are required'
        });
    }

    try {
        // Format phone number (ensure it has country code)
        const chatId = to.includes('@') ? to : `${to}@c.us`;

        await client.sendMessage(chatId, message);

        console.log(`✅ Message sent to ${to}`);

        res.json({
            success: true,
            message: 'Message sent successfully'
        });

    } catch (err) {
        console.error('Error sending message:', err);
        res.status(500).json({
            error: 'Failed to send message',
            details: err.message
        });
    }
});

/**
 * Logout and clear session
 */
app.post('/logout', async (req, res) => {
    try {
        if (client) {
            await client.logout();
            console.log('✅ Logged out successfully');
        }

        res.json({
            success: true,
            message: 'Logged out successfully'
        });

    } catch (err) {
        console.error('Error logging out:', err);
        res.status(500).json({
            error: 'Failed to logout',
            details: err.message
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 WhatsApp Bridge Server running on http://localhost:${PORT}`);
    console.log(`📁 Session path: ${SESSION_PATH}`);
    initializeClient();
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n⚠️  Shutting down gracefully...');
    if (client) {
        await client.destroy();
    }
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('\n⚠️  Shutting down gracefully...');
    if (client) {
        await client.destroy();
    }
    process.exit(0);
});
