import pytest
from fastapi import HTTPException
from app.core.dependencies import get_current_user
from jose import jwt

def test_get_current_user_invalid_token(client):
    """Test get_current_user with invalid token"""
    with pytest.raises(HTTPException) as exc_info:
        next(get_current_user("invalid_token"))
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"

def test_get_current_user_expired_token(client, test_user):
    """Test get_current_user with expired token"""
    from app.core.config import settings
    import time
    
    # Create an expired token
    token_data = {
        "sub": test_user["email"],
        "exp": time.time() - 300  # 5 minutes ago
    }
    expired_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    with pytest.raises(HTTPException) as exc_info:
        next(get_current_user(expired_token))
    assert exc_info.value.status_code == 401 