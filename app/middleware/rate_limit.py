"""
Rate limiting middleware for API endpoints.
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.logger import Logger
from app.config.settings import settings

logger = Logger.get_logger(__name__)


class RateLimitStore:
    """In-memory rate limit store using sliding window algorithm."""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(
        self, 
        identifier: str, 
        limit: int, 
        window_seconds: int
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: Unique identifier (IP address)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, headers_dict)
        """
        async with self._lock:
            current_time = time.time()
            window_start = current_time - window_seconds
            
            # Clean old requests outside the window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            
            request_count = len(self.requests[identifier])
            remaining = max(0, limit - request_count)
            reset_time = int(current_time + window_seconds)
            
            headers = {
                "X-RateLimit-Limit": limit,
                "X-RateLimit-Remaining": remaining,
                "X-RateLimit-Reset": reset_time,
                "X-RateLimit-Window": window_seconds
            }
            
            if request_count >= limit:
                # Find the oldest request to calculate retry-after
                if self.requests[identifier]:
                    oldest_request = min(self.requests[identifier])
                    retry_after = int(oldest_request + window_seconds - current_time)
                    headers["Retry-After"] = max(1, retry_after)
                return False, headers
            
            # Add current request
            self.requests[identifier].append(current_time)
            return True, headers


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI."""
    
    def __init__(self, app, store: Optional[RateLimitStore] = None):
        super().__init__(app)
        self.store = store or RateLimitStore()
        
        # Rate limit configurations from settings
        self.global_limit = getattr(settings, 'rate_limit_requests', 100)
        self.global_window = getattr(settings, 'rate_limit_window', 3600)  # 1 hour
        self.chat_limit = getattr(settings, 'rate_limit_chat_requests', 30)
        self.chat_window = getattr(settings, 'rate_limit_chat_window', 300)  # 5 minutes
        
        # Exempted paths
        self.exempted_paths = {
            "/",
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/api/v1/agents/health"
        }
    
    def get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Check for forwarded IP first (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client IP
        return request.client.host if request.client else "unknown"
    
    def get_rate_limit_config(self, request: Request) -> Tuple[int, int]:
        """Get rate limit configuration based on endpoint."""
        path = request.url.path
        
        # Chat endpoint has stricter limits
        if "/chat" in path:
            return self.chat_limit, self.chat_window
        
        # Default global limits
        return self.global_limit, self.global_window
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for exempted paths
        if request.url.path in self.exempted_paths:
            return await call_next(request)
        
        # Skip for health checks and static files
        if (request.url.path.startswith("/static") or 
            request.method == "OPTIONS"):
            return await call_next(request)
        
        client_id = self.get_client_identifier(request)
        limit, window = self.get_rate_limit_config(request)
        
        try:
            is_allowed, headers = await self.store.is_allowed(
                client_id, limit, window
            )
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for {client_id} on {request.url.path}"
                )
                
                error_response = {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "details": {
                        "limit": limit,
                        "window_seconds": window,
                        "retry_after": headers.get("Retry-After", window)
                    }
                }
                
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=error_response
                )
                
                # Add rate limit headers
                for key, value in headers.items():
                    response.headers[key] = str(value)
                
                return response
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers to successful response
            for key, value in headers.items():
                response.headers[key] = str(value)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in rate limiting: {e}")
            # Continue without rate limiting if there's an error
            return await call_next(request)


def create_rate_limit_middleware(store: Optional[RateLimitStore] = None) -> RateLimitMiddleware:
    """Factory function to create rate limit middleware."""
    return lambda app: RateLimitMiddleware(app, store)
