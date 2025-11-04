from flask import Flask, request, jsonify
import json
import os
import time
from datetime import datetime
from rag_engine import get_rag_engine
from monitoring import get_query_logger


app = Flask(__name__)

# Initialize RAG engine once at startup

print("Initializing RAG engine...")
rag_engine = get_rag_engine()
print("RAG engine ready!")


# Load user data
def load_users():
    """Load user data from a JSON file."""
    users_file = os.path.join(os.path.dirname(__file__), 'data', 'users.json')
    with open(users_file, 'r') as f:
        data = json.load(f)
    return data['users']

def find_user_by_email(email):
    """Find a user by email address."""
    users = load_users()
    email_lower = email.lower().strip()
    
    for user in users:
        if user['email'].lower() == email_lower:
            return user
    return None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint for Dialogflow"""

    start_time = time.time() #track response time
    
    req = request.get_json(force=True)
    intent_name = req.get('queryResult').get('intent').get('displayName')
    parameters = req.get('queryResult').get('parameters', {})
    query_text = req.get('queryResult').get('queryText', '')

    
    # LLMOps: Log incoming requests for monitoring
    print(f"Intent: {intent_name}")
    print(f"Parameters: {parameters}")
    
    # Route to appropriate handler
    if intent_name == 'api_authentication':
        response_text = handle_api_authentication(parameters)
    elif intent_name == 'api_rate_limits':
        response_text = handle_api_rate_limits(parameters)
    elif intent_name == 'billing_question':
        response_text = handle_billing_question(parameters)
    elif intent_name == 'general_knowledge':  # NEW: RAG-powered intent
        response_text = handle_general_knowledge(parameters)
    else:
        response_text = "I can help with API authentication, rate limits, billing questions, or general documentation questions."
    
     # Log query for monitoring (LLMOps practice)
    response_time = time.time() - start_time
    logger = get_query_logger()
    logger.log_query(
        query=query_text,
        intent=intent_name,
        response_time=response_time,
        user_email=parameters.get('email')
    )

    # Return response to Dialogflow
    return jsonify({
        'fulfillmentText': response_text
    })

def handle_general_knowledge(parameters):
    """
    Handle general documentation questions using RAG.
    """
    start_time = time.time()
    query = parameters.get('query', '')
    
    if not query:
        return """I can help you find information in our documentation! 

Try asking about:
- Integration setup (Slack, Salesforce, Zapier, Webhooks)
- API documentation and best practices
- Billing and subscription management

What would you like to know?"""
    
    # Use RAG to search knowledge base
    # Software Engineering: Error handling for production reliability
    try:
        result = rag_engine.search(query)
        
        answer = result['answer']
        sources = result['sources']
        
        # Log with sources
        response_time = time.time() - start_time
        logger = get_query_logger()
        logger.log_query(
            query=query,
            intent="general_knowledge",
            response_time=response_time,
            sources=sources
        )

        # Format response with sources
        response = f"{answer}\n\n"
        
        if sources:
            # Clean up source paths for display
            source_names = [os.path.basename(s) for s in sources]
            response += f"📚 Sources: {', '.join(source_names)}"
        
        return response
        
    except Exception as e:
        # Software Engineering: Graceful error handling
        print(f"RAG Error: {str(e)}")
        return """I'm having trouble accessing our documentation right now. 

Let me connect you with a human agent who can help."""

def handle_api_authentication(parameters):
    """Handle API authentication queries."""
    email = parameters.get('email')
    if not email:
        return "To look up your API key, I'll need your email address. What email do you use to sign in?"
    
    user = find_user_by_email(email)
    if not user:
        return "I couldn't find an account with email {email}. Please double-check the email address."
    
    # Format the last used time nicely
    last_used = user['api_key_last_used']
    last_used_date = datetime.fromisoformat(last_used.replace('Z', '+00:00'))
    time_diff = datetime.now().astimezone() - last_used_date
    
    if time_diff.total_seconds() < 3600:
        time_ago = f"{int(time_diff.total_seconds() / 60)} minutes ago"
    elif time_diff.total_seconds() < 86400:
        time_ago = f"{int(time_diff.total_seconds() / 3600)} hours ago"
    else:
        time_ago = f"{int(time_diff.days)} days ago"
    
    response = f"""Hi {user['name']}! Here's your API key information:

🔑 API Key: `{user['api_key']}`
📅 Created: {user['api_key_created']}
⏰ Last used: {time_ago}

Remember to keep your API key secure and never share it publicly!

Need to regenerate your key? Go to Settings → Developers → API Keys"""
    
    return response

def handle_api_rate_limits(parameters):
    """Handle API rate limit queries"""
    email = parameters.get('email', '')
    
    if not email:
        return "To check your rate limits, I'll need your email address. What email do you use to sign in?"
    
    user = find_user_by_email(email)
    
    if not user:
        return f"I couldn't find an account with email {email}. Please check the email address."
    
    # Calculate usage percentage
    usage_percent = (user['requests_used_today'] / user['rate_limit_hourly']) * 100
    
    response = f"""Hi {user['name']}! Here's your API rate limit info:

📊 Plan: {user['subscription_tier']}
⚡ Rate Limit: {user['rate_limit_hourly']} requests/hour
📈 Today's Usage: {user['requests_used_today']} requests ({usage_percent:.1f}%)
🔄 Resets: Midnight UTC

"""
    
    if usage_percent > 80:
        response += "⚠️ You're approaching your rate limit! Consider:\n"
        response += "• Implementing request caching\n"
        response += "• Adding exponential backoff\n"
        response += f"• Upgrading to {'Pro' if user['subscription_tier'] == 'Free' else 'Enterprise'} plan\n"
    else:
        response += "✅ You have plenty of quota remaining.\n"
    
    response += "\n📚 Rate limit best practices: https://docs.yourcompany.com/api/rate-limits"
    
    return response

def handle_billing_question(parameters):
    """Handle billing queries"""
    email = parameters.get('email', '')
    
    if not email:
        return "To check your billing info, I'll need your email address. What email do you use to sign in?"
    
    user = find_user_by_email(email)
    
    if not user:
        return f"I couldn't find an account with email {email}. Please check the email address."
    
    if user['subscription_tier'] == 'Free':
        response = f"""Hi {user['name']}! You're currently on our Free plan.

💰 Monthly Cost: $0
📊 Features: Basic API access, {user['rate_limit_hourly']} requests/hour

Want to upgrade? Check out our Pro plan ($49/mo) for:
- 10x more API requests (1,000/hour)
- Priority support
- Advanced features

Upgrade: Settings → Billing → Change Plan"""
    else:
        response = f"""Hi {user['name']}! Here's your billing information:

💰 Current Plan: {user['subscription_tier']} (${user['monthly_cost']}/month)
📅 Next Billing Date: {user['next_billing_date']}
📧 Billing Email: {user['billing_email']}

View invoices: Settings → Billing → Invoice History
Update payment: Settings → Billing → Payment Methods

Need help with billing? I can connect you with our billing team."""
    
    return response

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)