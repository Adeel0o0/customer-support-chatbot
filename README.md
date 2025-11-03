# Customer Support Chatbot
AI-powered customer support chatbot for SaaS companies using Google Dialogflow. Handles password resets, billing questions, integrations, and API troubleshooting.

## Project Overview

This chatbot demonstrates end-to-end implemntation for customers by handling Tier-1 queries

**Built for** SaaS/API companies with small technical support needs
**Platform*** Google Diaglogflow
**Status:** Phase 1 Complete (Intent-based responses)

##  Features

- **Password Reset**: Guides users through password recovery process
- **Billing Support**: Answers common billing and invoice questions
- **Integration Help**: Assists with third-party integrations (Slack, Salesforce, etc.)
- **API Authentication**: Troubleshoots API key and authentication issues
- **Rate Limit Support**: Explains API rate limits and quota errors

## Architecture

**Phase 1**

- Intent-based responses using Dialogflow
- 5 core intents covering common support quries
- Custom fallback handling for unknown queries

**Phase 2: Webhook Integration (Local dev)**
- Added Python Flask webhook for dynamic, personalised responses:
```
User Query → Dialogflow (NLU) → Webhook (Flask) → User Database → Personalized Response
```

### Dynamic Features Implemented

**API Authentication Intent:**
- Looks up user's API key by email
- Shows key creation date and last usage
- Personalizes response with user's name

**Rate Limits Intent:**
- Displays user's current plan and quota
- Shows real-time usage (e.g., "247/1000 requests used")
- Warns if approaching limit (>80%)
- Suggests upgrade path based on current tier

**Billing Intent:**
- Shows subscription details and costs
- Displays next billing date
- Different responses for Free vs. Paid users


## Demo

**[Try live demo](https://console.dialogflow.com/api-client/demo/embedded/df67e36a-8f8f-4635-be10-06df92db4a04)**

![Chatbot Demo](assets/demo-screenshot.png) 

### Local testing

Webhook successfully tested locally:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"queryResult": {"intent": {"displayName": "api_authentication"}, "parameters": {"email": "john@company.com"}}}'
```

**Response:**
```json
{
  "fulfillmentText": "Hi John Smith! Here's your API key information:\n\n🔑 API Key: `sk_live_abc123xyz789`\n📅 Created: 2025-10-01\n⏰ Last used: 19 hours ago..."
}
```

## Technologies

- Google Dialogflow (NLU)
- Python 3.x + Flask
- JSON-based mock database
- RESTful webhook endpoint

## Success Metrics

- **Target Resolution Rate:** 60%
- **Response Time:** <2 seconds
- **Escalation Triggers:** 3 failed attempts or negative sentiment
- **Success Criteria:** CSAT >4.0/5.0