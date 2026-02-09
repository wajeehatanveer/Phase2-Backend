import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.jwt_handler import create_access_token
from datetime import timedelta


client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_missing_authorization_header():
    """Test that endpoints return 403 when no authorization header is provided"""
    response = client.get("/api/test_user/tasks")
    assert response.status_code == 403  # Should be 403 since no token provided


def test_invalid_token():
    """Test that endpoints return 401 with an invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/test_user/tasks", headers=headers)
    assert response.status_code == 401


def test_valid_token_format():
    """Test that a valid token format works"""
    # Create a valid token
    token_data = {"user_id": "test_user_123", "sub": "test_user_123"}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=30))
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/test_user_123/tasks", headers=headers)
    # This should return 200 even if no tasks exist, just to verify auth worked
    # It might return 200 or 404 depending on implementation, but not 401/403
    assert response.status_code in [200, 404]  # 200 if empty list returned, 404 if error in implementation