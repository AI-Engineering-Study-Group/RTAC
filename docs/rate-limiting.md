# API Rate Limiting

This document describes the rate limiting implementation for the RTAC API Conference AI Agent.

## Overview

The API implements rate limiting to prevent abuse and ensure fair usage for all users. The rate limiting uses a sliding window algorithm to track requests over time.

## Configuration

Rate limiting is configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Global requests per window |
| `RATE_LIMIT_WINDOW` | `3600` | Global window size in seconds (1 hour) |
| `RATE_LIMIT_CHAT_REQUESTS` | `30` | Chat endpoint requests per window |
| `RATE_LIMIT_CHAT_WINDOW` | `300` | Chat window size in seconds (5 minutes) |

## Rate Limits

### Global Limits
- **100 requests per hour** for all endpoints (except chat)
- Applied to: `/api/v1/agents/status`, `/api/v1/agents/info`, `/api/v1/agents/rate-limits`

### Chat Limits
- **30 requests per 5 minutes** for chat endpoint
- Applied to: `/api/v1/agents/chat`

### Exempted Endpoints
The following endpoints are exempt from rate limiting:
- `/` (root)
- `/docs` (API documentation)
- `/redoc` (API documentation)
- `/openapi.json` (OpenAPI specification)
- `/api/v1/agents/health` (health check)
- Static files under `/static`
- `OPTIONS` requests (CORS preflight)

## Client Identification

Clients are identified using the following order of precedence:
1. `X-Forwarded-For` header (first IP if comma-separated)
2. `X-Real-IP` header
3. Client IP address from request

## Rate Limit Headers

All responses include rate limiting headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests allowed in window |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Unix timestamp when window resets |
| `X-RateLimit-Window` | Window size in seconds |
| `Retry-After` | Seconds to wait before retrying (when rate limited) |

## Rate Limit Exceeded Response

When rate limit is exceeded, the API returns:

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "details": {
    "limit": 30,
    "window_seconds": 300,
    "retry_after": 120
  }
}
```

HTTP Status Code: `429 Too Many Requests`

## Example Responses

### Successful Request
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1691751600
X-RateLimit-Window: 3600
Content-Type: application/json

{
  "success": true,
  "data": {...},
  "message": "Request processed successfully"
}
```

### Rate Limited Request
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1691751600
X-RateLimit-Window: 300
Retry-After: 120
Content-Type: application/json

{
  "success": false,
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "details": {
    "limit": 30,
    "window_seconds": 300,
    "retry_after": 120
  }
}
```

## Rate Limit Information Endpoint

Get current rate limiting configuration:

```http
GET /api/v1/agents/rate-limits
```

Response:
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "global_limits": {
      "requests": 100,
      "window_seconds": 3600,
      "window_description": "60 minutes"
    },
    "chat_limits": {
      "requests": 30,
      "window_seconds": 300,
      "window_description": "5 minutes"
    },
    "headers_included": [
      "X-RateLimit-Limit",
      "X-RateLimit-Remaining",
      "X-RateLimit-Reset",
      "X-RateLimit-Window",
      "Retry-After (when limit exceeded)"
    ]
  },
  "message": "Rate limit information retrieved successfully"
}
```

## Implementation Details

### Sliding Window Algorithm

The rate limiting uses a sliding window algorithm that:
1. Tracks timestamps of all requests for each client
2. Removes requests older than the window size
3. Counts remaining requests to check against limit
4. Calculates appropriate headers

### Memory Management

The implementation includes automatic cleanup of old request records to prevent memory leaks.

### Concurrency Safety

The rate limiting store uses async locks to handle concurrent requests safely.

## Monitoring and Observability

Rate limiting events are logged with appropriate log levels:
- **INFO**: Normal rate limiting operations
- **WARNING**: Rate limit exceeded events
- **ERROR**: Rate limiting system errors

Log example:
```
2024-08-10 12:00:00 WARNING Rate limit exceeded for 192.168.1.1 on /api/v1/agents/chat
```

## Best Practices for Clients

### Respect Rate Limits
- Monitor rate limit headers in responses
- Implement exponential backoff when rate limited
- Cache responses when appropriate

### Handle Rate Limit Errors
```javascript
// Example client handling
const response = await fetch('/api/v1/agents/chat', options);

if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  console.log(`Rate limited. Retry after ${retryAfter} seconds`);
  
  // Wait and retry
  setTimeout(() => {
    // Retry request
  }, retryAfter * 1000);
}
```

### Monitor Usage
```javascript
// Check remaining requests
const remaining = response.headers.get('X-RateLimit-Remaining');
const limit = response.headers.get('X-RateLimit-Limit');

console.log(`Requests remaining: ${remaining}/${limit}`);
```

## Configuration for Different Environments

### Development
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_CHAT_REQUESTS=100
RATE_LIMIT_CHAT_WINDOW=300
```

### Production
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_CHAT_REQUESTS=30
RATE_LIMIT_CHAT_WINDOW=300
```

### Testing
```env
RATE_LIMIT_ENABLED=false
# OR very high limits for load testing
RATE_LIMIT_REQUESTS=10000
RATE_LIMIT_WINDOW=60
```

## Troubleshooting

### Rate Limiting Not Working
1. Check `RATE_LIMIT_ENABLED=true` in environment
2. Verify middleware is added to FastAPI app
3. Check logs for rate limiting errors

### False Rate Limiting
1. Verify client identification (check headers)
2. Consider proxy/load balancer configuration
3. Review exempted paths configuration

### Performance Issues
1. Monitor memory usage of rate limit store
2. Consider Redis-based store for distributed deployment
3. Adjust cleanup intervals if needed

## Future Enhancements

Potential improvements to consider:
- Redis-based distributed rate limiting
- Different limits for authenticated vs anonymous users
- IP whitelisting for trusted clients
- Rate limiting by user ID instead of IP
- Configurable rate limiting per endpoint
