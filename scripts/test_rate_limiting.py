#!/usr/bin/env python3
"""
Rate limiting test script.

This script tests the rate limiting functionality by making multiple requests
to the API and checking the rate limit headers and responses.
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, Any


class RateLimitTester:
    """Test rate limiting functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Make a request and return response data with headers."""
        url = f"{self.base_url}{endpoint}"
        
        async with self.session.request(method, url, **kwargs) as response:
            headers = dict(response.headers)
            
            try:
                data = await response.json()
            except:
                data = await response.text()
            
            return {
                "status": response.status,
                "headers": headers,
                "data": data,
                "timestamp": time.time()
            }
    
    def print_rate_limit_info(self, response: Dict[str, Any]):
        """Print rate limit information from response."""
        headers = response["headers"]
        status = response["status"]
        
        print(f"Status: {status}")
        print(f"Rate Limit Headers:")
        
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset",
            "X-RateLimit-Window",
            "Retry-After"
        ]
        
        for header in rate_limit_headers:
            value = headers.get(header.lower(), "Not present")
            print(f"  {header}: {value}")
        
        print("-" * 50)
    
    async def test_global_rate_limits(self, requests_count: int = 10):
        """Test global rate limits on status endpoint."""
        print(f"Testing global rate limits with {requests_count} requests to /api/v1/agents/status")
        print("=" * 60)
        
        for i in range(requests_count):
            response = await self.make_request("/api/v1/agents/status")
            
            print(f"Request {i+1}:")
            self.print_rate_limit_info(response)
            
            if response["status"] == 429:
                print("🚫 Rate limit exceeded!")
                break
            
            # Small delay between requests
            await asyncio.sleep(0.1)
    
    async def test_chat_rate_limits(self, requests_count: int = 10):
        """Test chat endpoint rate limits."""
        print(f"Testing chat rate limits with {requests_count} requests to /api/v1/agents/chat")
        print("=" * 60)
        
        chat_payload = {
            "message": "Hello, this is a test message",
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        for i in range(requests_count):
            response = await self.make_request(
                "/api/v1/agents/chat",
                method="POST",
                json=chat_payload
            )
            
            print(f"Chat Request {i+1}:")
            self.print_rate_limit_info(response)
            
            if response["status"] == 429:
                print("🚫 Rate limit exceeded!")
                retry_after = response["headers"].get("retry-after")
                if retry_after:
                    print(f"Retry after: {retry_after} seconds")
                break
            
            # Small delay between requests
            await asyncio.sleep(0.1)
    
    async def test_exempted_endpoints(self):
        """Test that exempted endpoints don't have rate limits."""
        print("Testing exempted endpoints")
        print("=" * 60)
        
        exempted_endpoints = [
            "/",
            "/api/v1/agents/health",
            "/docs"
        ]
        
        for endpoint in exempted_endpoints:
            response = await self.make_request(endpoint)
            
            print(f"Exempted endpoint {endpoint}:")
            print(f"Status: {response['status']}")
            
            # Check if rate limit headers are present
            headers = response["headers"]
            has_rate_limit = any(
                h.startswith("x-ratelimit") for h in headers.keys()
            )
            
            if has_rate_limit:
                print("⚠️  Rate limit headers found (unexpected)")
            else:
                print("✅ No rate limit headers (expected)")
            
            print("-" * 30)
    
    async def test_rate_limit_info_endpoint(self):
        """Test the rate limit info endpoint."""
        print("Testing rate limit info endpoint")
        print("=" * 60)
        
        response = await self.make_request("/api/v1/agents/rate-limits")
        
        print(f"Status: {response['status']}")
        
        if response["status"] == 200:
            data = response["data"]
            if isinstance(data, dict) and "data" in data:
                rate_info = data["data"]
                print("Rate Limit Configuration:")
                print(f"  Enabled: {rate_info.get('enabled')}")
                
                global_limits = rate_info.get('global_limits', {})
                print(f"  Global: {global_limits.get('requests')} requests per {global_limits.get('window_description')}")
                
                chat_limits = rate_info.get('chat_limits', {})
                print(f"  Chat: {chat_limits.get('requests')} requests per {chat_limits.get('window_description')}")
        
        print("-" * 50)
    
    async def test_concurrent_requests(self, concurrent_count: int = 5):
        """Test concurrent requests to check for race conditions."""
        print(f"Testing {concurrent_count} concurrent requests")
        print("=" * 60)
        
        async def make_concurrent_request(request_id: int):
            response = await self.make_request("/api/v1/agents/status")
            return request_id, response
        
        # Make concurrent requests
        tasks = [
            make_concurrent_request(i) 
            for i in range(concurrent_count)
        ]
        
        results = await asyncio.gather(*tasks)
        
        for request_id, response in results:
            print(f"Concurrent Request {request_id + 1}:")
            print(f"  Status: {response['status']}")
            
            headers = response["headers"]
            remaining = headers.get("x-ratelimit-remaining", "N/A")
            print(f"  Remaining: {remaining}")
        
        print("-" * 50)


async def main():
    """Run all rate limiting tests."""
    print("🧪 RTAC API Rate Limiting Test Suite")
    print("=" * 60)
    
    async with RateLimitTester() as tester:
        try:
            # Test rate limit info endpoint first
            await tester.test_rate_limit_info_endpoint()
            
            # Test exempted endpoints
            await tester.test_exempted_endpoints()
            
            # Test concurrent requests
            await tester.test_concurrent_requests()
            
            # Test global rate limits
            await tester.test_global_rate_limits(5)
            
            # Wait a bit
            print("Waiting 2 seconds...")
            await asyncio.sleep(2)
            
            # Test chat rate limits
            await tester.test_chat_rate_limits(5)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return
    
    print("✅ Rate limiting tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
