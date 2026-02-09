import sys
import os
from fastapi.testclient import TestClient
# Ensure project root is on sys.path so `backend` package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# Use a local sqlite DB for this script to avoid touching production DB
import os as _os
_os.environ.setdefault('DATABASE_URL', 'sqlite:///./dev_test.db')
from backend.main import app

with TestClient(app) as client:
    # Login to get a token
    resp = client.post('/auth/login', json={'user_id':'test_user_123'})
    print('login', resp.status_code, resp.json())

    token = resp.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    # Create a task
    payload = {
        'title':'E2E Task',
        'description':'End to end created task',
        'priority':'medium',
        'tags':['e2e'],
        'due_date':'2025-12-31T10:00:00',
        'recurrence':'none'
    }

    resp2 = client.post('/api/test_user_123/tasks', json=payload, headers=headers)
    print('create task', resp2.status_code, resp2.json())
