"""
Simple Token System - User Credits Management
Manages user tokens for API usage without external dependencies
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib
import json


class TokenManager:
    """Simple in-memory token management system"""
    
    def __init__(self):
        # User tokens: {user_id: {"tokens": int, "created_at": datetime, "last_used": datetime}}
        self.user_tokens: Dict[str, dict] = {}
        
        # Request cache: {request_hash: {"result": any, "timestamp": datetime}}
        self.request_cache: Dict[str, dict] = {}
        
        # Rate limiting: {user_id: [timestamps]}
        self.rate_limits: Dict[str, list] = {}
        
        # Configuration
        self.INITIAL_TOKENS = 5
        self.CACHE_EXPIRY_MINUTES = 10
        self.RATE_LIMIT_REQUESTS = 10  # Max requests per minute
        self.RATE_LIMIT_WINDOW = 60  # seconds
    
    def create_user(self, user_id: str) -> dict:
        """Create new user with initial tokens"""
        if user_id not in self.user_tokens:
            self.user_tokens[user_id] = {
                "tokens": self.INITIAL_TOKENS,
                "created_at": datetime.now(),
                "last_used": None,
                "total_requests": 0
            }
        return self.user_tokens[user_id]
    
    def get_user_tokens(self, user_id: str) -> int:
        """Get user's remaining tokens"""
        if user_id not in self.user_tokens:
            self.create_user(user_id)
        return self.user_tokens[user_id]["tokens"]
    
    def consume_tokens(self, user_id: str, tokens: int) -> bool:
        """
        Consume tokens from user account
        Returns True if successful, False if insufficient tokens
        """
        if user_id not in self.user_tokens:
            self.create_user(user_id)
        
        user_data = self.user_tokens[user_id]
        
        if user_data["tokens"] >= tokens:
            user_data["tokens"] -= tokens
            user_data["last_used"] = datetime.now()
            user_data["total_requests"] += 1
            return True
        
        return False
    
    def add_tokens(self, user_id: str, tokens: int):
        """Add tokens to user account (for upgrades/purchases)"""
        if user_id not in self.user_tokens:
            self.create_user(user_id)
        
        self.user_tokens[user_id]["tokens"] += tokens
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user is within rate limits
        Returns True if within limits, False if exceeded
        """
        now = datetime.now()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Clean old timestamps
        cutoff_time = now - timedelta(seconds=self.RATE_LIMIT_WINDOW)
        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id]
            if ts > cutoff_time
        ]
        
        # Check limit
        if len(self.rate_limits[user_id]) >= self.RATE_LIMIT_REQUESTS:
            return False
        
        # Add current timestamp
        self.rate_limits[user_id].append(now)
        return True
    
    def create_request_hash(self, user_id: str, endpoint: str, data: dict) -> str:
        """Create unique hash for request deduplication"""
        request_str = f"{user_id}:{endpoint}:{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(request_str.encode()).hexdigest()
    
    def get_cached_result(self, request_hash: str) -> Optional[dict]:
        """Get cached result if exists and not expired"""
        if request_hash not in self.request_cache:
            return None
        
        cached = self.request_cache[request_hash]
        expiry_time = cached["timestamp"] + timedelta(minutes=self.CACHE_EXPIRY_MINUTES)
        
        if datetime.now() > expiry_time:
            # Cache expired
            del self.request_cache[request_hash]
            return None
        
        return cached["result"]
    
    def cache_result(self, request_hash: str, result: dict):
        """Cache request result"""
        self.request_cache[request_hash] = {
            "result": result,
            "timestamp": datetime.now()
        }
    
    def clean_expired_cache(self):
        """Clean expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, data in self.request_cache.items():
            expiry_time = data["timestamp"] + timedelta(minutes=self.CACHE_EXPIRY_MINUTES)
            if now > expiry_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.request_cache[key]
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get user statistics"""
        if user_id not in self.user_tokens:
            self.create_user(user_id)
        
        user_data = self.user_tokens[user_id]
        return {
            "user_id": user_id,
            "tokens_remaining": user_data["tokens"],
            "total_requests": user_data["total_requests"],
            "created_at": user_data["created_at"].isoformat(),
            "last_used": user_data["last_used"].isoformat() if user_data["last_used"] else None
        }
    
    def get_system_stats(self) -> dict:
        """Get system-wide statistics"""
        return {
            "total_users": len(self.user_tokens),
            "cached_requests": len(self.request_cache),
            "total_tokens_consumed": sum(
                self.INITIAL_TOKENS - data["tokens"]
                for data in self.user_tokens.values()
            )
        }


# Global token manager instance
token_manager = TokenManager()


def require_tokens(tokens: int):
    """
    Decorator to require tokens for endpoint
    Usage: @require_tokens(2)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This is a placeholder - will be integrated with FastAPI dependency injection
            return await func(*args, **kwargs)
        return wrapper
    return decorator
