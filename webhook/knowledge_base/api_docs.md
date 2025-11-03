# API Authentication

All API requests require authentication using your API key.

Finding your API key:
1. Log in to your account
2. Go to Settings → Developers → API Keys
3. Click "Generate New Key" if you don't have one
4. Copy the key immediately (shown only once)

Using your API key:
Include it in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

Security best practices:
- Never commit API keys to version control
- Rotate keys every 90 days
- Use different keys for dev/production
- Revoke keys immediately if compromised

# Rate Limits

Rate limits prevent abuse and ensure system stability.

Limits by plan:
- Free: 100 requests/hour
- Pro: 1,000 requests/hour  
- Enterprise: 10,000 requests/hour

Rate limit headers:
- X-RateLimit-Limit: Your plan's limit
- X-RateLimit-Remaining: Requests remaining
- X-RateLimit-Reset: Unix timestamp when limit resets

Best practices:
- Cache responses when possible
- Implement exponential backoff
- Monitor your usage
- Batch requests where supported

Error codes:
- 429 Too Many Requests: You've exceeded your rate limit
- 401 Unauthorized: Invalid or missing API key
- 403 Forbidden: Valid key but insufficient permissions

# Error Handling

Common error responses:

400 Bad Request:
- Missing required parameters
- Invalid parameter format
- Malformed JSON

401 Unauthorized:
- Missing API key
- Invalid API key
- Expired API key

404 Not Found:
- Resource doesn't exist
- Wrong endpoint URL

500 Internal Server Error:
- Server-side issue
- We're notified automatically
- Retry with exponential backoff

Error response format:
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Missing required parameter: email"
  }
}
```