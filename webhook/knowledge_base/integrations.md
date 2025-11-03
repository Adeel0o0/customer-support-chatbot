# Slack Integration

To connect Slack to our platform:

1. Go to Settings → Integrations
2. Click "Connect Slack"
3. You'll be redirected to Slack to authorize
4. Select the workspace you want to connect
5. Choose which channels to sync

Requirements:
- You must be a workspace admin
- The Slack workspace must be on a paid plan

Common issues:
- "Permission denied" - You need admin access
- "Already connected" - Disconnect existing integration first

# Salesforce Integration

To connect Salesforce:

1. Navigate to Settings → Integrations → Salesforce
2. Click "Authorize Salesforce"
3. Log in with your Salesforce credentials
4. Grant the requested permissions
5. Select which objects to sync (Contacts, Leads, Opportunities)

Requirements:
- Salesforce Professional edition or higher
- API access enabled in your Salesforce org

Sync frequency: Every 15 minutes

# Zapier Integration

Our Zapier app allows you to connect with 5,000+ apps.

Setup:
1. Go to Zapier.com
2. Search for "YourApp" in the app directory
3. Create a new Zap
4. Connect your account using your API key

Popular Zaps:
- New customer → Create Slack notification
- New ticket → Create Trello card
- Form submission → Add to Google Sheets

# Webhook Setup

To set up custom webhooks:

1. Go to Settings → Developers → Webhooks
2. Click "Create Webhook"
3. Enter your endpoint URL (must be HTTPS)
4. Select events you want to receive
5. Save and test

Webhook events:
- customer.created
- ticket.opened
- ticket.closed
- payment.succeeded

Retry policy: We retry failed webhooks 3 times with exponential backoff.