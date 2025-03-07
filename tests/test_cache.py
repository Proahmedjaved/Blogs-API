import pytest
from unittest.mock import Mock
import json
from app.cache.redis import get_cache, set_cache, invalidate_cache, invalidate_pattern

def test_cache_operations(monkeypatch):
    """Test Redis cache operations with mocked Redis client"""
    # Mock storage for our fake Redis
    cache_storage = {}
    
    class MockRedis:
        def get(self, key):
            return json.dumps(cache_storage.get(key)).encode() if key in cache_storage else None
            
        def setex(self, key, expiry, value):
            cache_storage[key] = json.loads(value)
            
        def delete(self, key):
            if key in cache_storage:
                del cache_storage[key]
                
        def keys(self, pattern):
            # Simple pattern matching for test purposes
            # Pattern comes in as bytes, so decode it first
            pattern_str = pattern.decode() if isinstance(pattern, bytes) else pattern
            pattern_str = pattern_str.replace('*', '')
            matching_keys = [k.encode() for k in cache_storage.keys() if k.startswith(pattern_str)]
            for key in [k.decode() for k in matching_keys]:
                self.delete(key)
            return matching_keys
    
    # Create and inject mock Redis client
    mock_redis = MockRedis()
    monkeypatch.setattr("app.cache.redis.redis_client", mock_redis)
    
    # Test setting and getting cache
    test_data = {"id": 1, "title": "Test Post"}
    set_cache("test:1", test_data, 3600)
    cached_result = get_cache("test:1")
    assert cached_result == test_data
    
    # Test cache miss
    assert get_cache("nonexistent") is None
    
    # Test cache invalidation
    invalidate_cache("test:1")
    assert get_cache("test:1") is None
    
    # Test pattern invalidation
    set_cache("pattern:1", {"data": "1"}, 3600)
    set_cache("pattern:2", {"data": "2"}, 3600)
    invalidate_pattern("pattern:*")
    assert get_cache("pattern:1") is None
    assert get_cache("pattern:2") is None

def test_post_caching(client, test_user_token):
    """Test caching for post endpoints"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Create a test post
    create_response = client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Cache Test Post",
            "content": "Testing cache functionality"
        }
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    
    # First request should hit the database
    first_response = client.get(f"/api/posts/{post_id}")
    assert first_response.status_code == 200
    first_data = first_response.json()
    
    # Second request should hit the cache
    second_response = client.get(f"/api/posts/{post_id}")
    assert second_response.status_code == 200
    second_data = second_response.json()
    
    # Both responses should be identical
    assert first_data == second_data
    
    # Update post should invalidate cache
    update_response = client.put(
        f"/api/posts/{post_id}",
        headers=headers,
        json={
            "title": "Updated Cache Test Post",
            "content": "Updated content"
        }
    )
    assert update_response.status_code == 200
    
    # Next get request should have updated data
    updated_response = client.get(f"/api/posts/{post_id}")
    assert updated_response.status_code == 200
    assert updated_response.json()["title"] == "Updated Cache Test Post"
    
def test_user_posts_caching(client, test_user_token):
    """Test caching for user posts endpoint"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Create user posts
    for i in range(2):
        client.post(
            "/api/posts/",
            headers=headers,
            json={
                "title": f"User Post {i}",
                "content": f"User Content {i}"
            }
        )
    
    # First request should hit the database
    first_response = client.get("/api/posts/me", headers=headers)
    assert first_response.status_code == 200
    first_data = first_response.json()
    
    # Second request should hit the cache
    second_response = client.get("/api/posts/me", headers=headers)
    assert second_response.status_code == 200
    second_data = second_response.json()
    
    # Both responses should be identical
    assert first_data == second_data
    
    # Delete a post should invalidate user posts cache
    post_id = first_data[0]["id"]
    delete_response = client.delete(f"/api/posts/{post_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # Next request should have updated data
    updated_response = client.get("/api/posts/me", headers=headers)
    assert updated_response.status_code == 200
    assert len(updated_response.json()) == len(first_data) - 1 