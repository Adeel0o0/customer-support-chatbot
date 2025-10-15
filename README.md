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

**Phase 2**
- Webhook integration for dynamic responses
- Sentiment detection for escalation
- Multi-channel deployment (Slack)


## Success Metrics

- **Target Resolution Rate:** 60%
- **Response Time:** <2 seconds
- **Escalation Triggers:** 3 failed attempts or negative sentiment
- **Success Criteria:** CSAT >4.0/5.0


## Technologies

- Google Dialogflow (NLU)
- Python 3.x (webhook - coming)
- Flask (API server - coming)