"""
Tests for rate limiting middleware.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.rate_limit import RateLimitMiddleware, RateLimitStore
from app.config.settings import settings


class MockRequest:
    """Mock request for testing."""
    
    def __init__(self, path="/", method="GET", client_host="127.0.0.1", headers=None):
        self.url = Mock()
        self.url.path = path
        self.method = method
        self.client = Mock()
        self.client.host = client_host
        self.headers = headers or {}


class TestRateLimitStore:
    """Test rate limit store functionality."""
    
    @pytest.fixture
    def store(self):
        return RateLimitStore()
    
    @pytest.mark.asyncio
    async def test_first_request_allowed(self, store):
        """Test that first request is allowed."""
        is_allowed, headers = await store.is_allowed("client1", 10, 60)
        
        assert is_allowed is True
        assert headers["X-RateLimit-Limit"] == 10
        assert headers["X-RateLimit-Remaining"] == 9
        assert "X-RateLimit-Reset" in headers
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, store):
        """Test rate limit exceeded."""
        # Make requests up to the limit
        for i in range(5):
            is_allowed, _ = await store.is_allowed("client1", 5, 60)
            assert is_allowed is True
        
        # Next request should be blocked
        is_allowed, headers = await store.is_allowed("client1", 5, 60)
        assert is_allowed is False
        assert headers["X-RateLimit-Remaining"] == 0
        assert "Retry-After" in headers
    
    @pytest.mark.asyncio
    async def test_sliding_window(self, store):
        """Test sliding window behavior."""
        # Make requests
        for i in range(3):
            await store.is_allowed("client1", 5, 2)  # 2 second window
            if i < 2:
                await asyncio.sleep(0.1)
        
        # Wait for window to slide
        await asyncio.sleep(2.5)
        
        # Should be allowed again
        is_allowed, headers = await store.is_allowed("client1", 5, 2)
        assert is_allowed is True
        assert headers["X-RateLimit-Remaining"] == 4
    
    @pytest.mark.asyncio
    async def test_different_clients(self, store):
        """Test that different clients have separate limits."""
        # Client 1 uses up their limit
        for i in range(3):
            await store.is_allowed("client1", 3, 60)
        
        # Client 1 should be blocked
        is_allowed, _ = await store.is_allowed("client1", 3, 60)
        assert is_allowed is False
        
        # Client 2 should still be allowed
        is_allowed, _ = await store.is_allowed("client2", 3, 60)
        assert is_allowed is True


class TestRateLimitMiddleware:
    """Test rate limit middleware."""
    
    @pytest.fixture
    def app(self):
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.post("/chat")
        async def chat_endpoint():
            return {"message": "chat response"}
        
        @app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}
        
        return app
    
    @pytest.fixture
    def middleware(self):
        store = RateLimitStore()
        return RateLimitMiddleware(None, store)
    
    def test_get_client_identifier_forwarded_for(self, middleware):
        """Test client identification with X-Forwarded-For header."""
        request = MockRequest(headers={"X-Forwarded-For": "192.168.1.1, 10.0.0.1"})
        client_id = middleware.get_client_identifier(request)
        assert client_id == "192.168.1.1"
    
    def test_get_client_identifier_real_ip(self, middleware):
        """Test client identification with X-Real-IP header."""
        request = MockRequest(headers={"X-Real-IP": "192.168.1.2"})
        client_id = middleware.get_client_identifier(request)
        assert client_id == "192.168.1.2"
    
    def test_get_client_identifier_fallback(self, middleware):
        """Test client identification fallback to client host."""
        request = MockRequest(client_host="127.0.0.1")
        client_id = middleware.get_client_identifier(request)
        assert client_id == "127.0.0.1"
    
    def test_get_rate_limit_config_chat(self, middleware):
        """Test rate limit config for chat endpoint."""
        request = MockRequest(path="/api/v1/agents/chat")
        limit, window = middleware.get_rate_limit_config(request)
        assert limit == middleware.chat_limit
        assert window == middleware.chat_window
    
    def test_get_rate_limit_config_global(self, middleware):
        """Test rate limit config for other endpoints."""
        request = MockRequest(path="/api/v1/agents/status")
        limit, window = middleware.get_rate_limit_config(request)
        assert limit == middleware.global_limit
        assert window == middleware.global_window
    
    @pytest.mark.asyncio
    async def test_exempted_paths(self, middleware):
        """Test that exempted paths bypass rate limiting."""
        request = MockRequest(path="/health")
        
        async def mock_call_next(req):
            return JSONResponse({"status": "healthy"})
        
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_options_requests_bypassed(self, middleware):
        """Test that OPTIONS requests bypass rate limiting."""
        request = MockRequest(path="/api/v1/agents/chat", method="OPTIONS")
        
        async def mock_call_next(req):
            return JSONResponse({"message": "options"})
        
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200


@pytest.mark.integration
class TestRateLimitIntegration:
    """Integration tests with FastAPI."""
    
    @pytest.fixture
    def app_with_middleware(self):
        app = FastAPI()
        
        # Add middleware
        app.add_middleware(RateLimitMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.post("/chat")
        async def chat_endpoint():
            return {"message": "chat response"}
        
        return app
    
    def test_rate_limit_headers_included(self, app_with_middleware):
        """Test that rate limit headers are included in response."""
        with patch.object(settings, 'rate_limit_requests', 100):
            with patch.object(settings, 'rate_limit_window', 3600):
                client = TestClient(app_with_middleware)
                response = client.get("/test")
                
                assert response.status_code == 200
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                assert "X-RateLimit-Reset" in response.headers
                assert "X-RateLimit-Window" in response.headers
    
    def test_rate_limit_exceeded_response(self, app_with_middleware):
        """Test response when rate limit is exceeded."""
        with patch.object(settings, 'rate_limit_requests', 2):
            with patch.object(settings, 'rate_limit_window', 60):
                client = TestClient(app_with_middleware)
                
                # Make requests up to limit
                response1 = client.get("/test")
                response2 = client.get("/test")
                assert response1.status_code == 200
                assert response2.status_code == 200
                
                # Next request should be rate limited
                response3 = client.get("/test")
                assert response3.status_code == 429
                
                data = response3.json()
                assert data["success"] is False
                assert data["error"] == "Rate limit exceeded"
                assert "Retry-After" in response3.headers


@pytest.mark.performance
class TestRateLimitPerformance:
    """Performance tests for rate limiting."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        store = RateLimitStore()
        
        async def make_request(client_id):
            return await store.is_allowed(client_id, 100, 60)
        
        # Make 50 concurrent requests for same client
        tasks = [make_request("client1") for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        # All should be processed
        assert len(results) == 50
        
        # Should respect rate limit
        allowed_count = sum(1 for is_allowed, _ in results if is_allowed)
        assert allowed_count <= 100
    
    @pytest.mark.asyncio
    async def test_memory_cleanup(self):
        """Test that old requests are cleaned up to prevent memory leaks."""
        store = RateLimitStore()
        
        # Make requests for many different clients
        for i in range(1000):
            await store.is_allowed(f"client_{i}", 10, 1)  # 1 second window
        
        # Wait for cleanup
        await asyncio.sleep(2)
        
        # Make a new request to trigger cleanup
        await store.is_allowed("new_client", 10, 1)
        
        # Check that old requests are cleaned up
        # (This is more of a smoke test - in practice you'd monitor memory usage)
        assert len(store.requests) < 1000
