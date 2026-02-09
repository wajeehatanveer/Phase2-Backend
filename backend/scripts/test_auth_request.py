import sys, os
# Ensure project root is on sys.path so 'backend' package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logging
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.jwt_handler import create_access_token
from datetime import timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = TestClient(app)

print("\n--- TEST: request with valid token ---")
valid_token = create_access_token({"user_id": "test_user_123", "sub": "test_user_123"}, expires_delta=timedelta(minutes=30))
headers = {"Authorization": f"Bearer {valid_token}", "Content-Type": "application/json"}
payload = {"title": "Integration Test Task", "priority": "medium"}
resp = client.post("/api/test_user_123/tasks", json=payload, headers=headers)
print("Status:", resp.status_code)
print("Body:", resp.text)

print("\n--- TEST: request with no token (expect 401) ---")
resp2 = client.post("/api/test_user_123/tasks", json=payload)
print("Status:", resp2.status_code)
print("Body:", resp2.text)

print("\n--- TEST: token missing user_id/sub (expect 401) ---")
bad_token = create_access_token({"foo": "bar"}, expires_delta=timedelta(minutes=30))
headers_bad = {"Authorization": f"Bearer {bad_token}", "Content-Type": "application/json"}
resp3 = client.post("/api/test_user_123/tasks", json=payload, headers=headers_bad)
print("Status:", resp3.status_code)
print("Body:", resp3.text)
