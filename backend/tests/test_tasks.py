import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.jwt_handler import create_access_token
from datetime import timedelta, datetime


client = TestClient(app)


def create_test_token(user_id: str = "test_user_123"):
    """Helper function to create a test token"""
    token_data = {"user_id": user_id, "sub": user_id}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=30))
    return token


def test_create_task():
    """Test creating a new task"""
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium",
        "tags": ["test", "important"],
        "due_date": "2023-12-31T10:00:00",
        "recurrence": "none"
    }
    
    response = client.post("/api/test_user_123/tasks", json=task_data, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["priority"] == "medium"
    assert data["tags"] == ["test", "important"]
    assert data["recurrence"] == "none"
    assert data["user_id"] == "test_user_123"
    assert data["completed"] is False


def test_get_tasks():
    """Test retrieving all tasks for a user"""
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/test_user_123/tasks", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_single_task():
    """Test retrieving a single task"""
    # First create a task
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    task_data = {
        "title": "Single Task",
        "description": "This is a single test task",
        "priority": "high",
        "tags": ["single", "test"],
        "due_date": "2023-12-31T10:00:00",
        "recurrence": "none"
    }
    
    create_response = client.post("/api/test_user_123/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Now get the task
    response = client.get(f"/api/test_user_123/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Single Task"


def test_update_task():
    """Test updating an existing task"""
    # First create a task
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    task_data = {
        "title": "Original Task",
        "description": "Original description",
        "priority": "low",
        "tags": ["original"],
        "due_date": "2023-12-31T10:00:00",
        "recurrence": "none"
    }
    
    create_response = client.post("/api/test_user_123/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Now update the task
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "priority": "high",
        "tags": ["updated", "important"],
        "due_date": "2024-12-31T10:00:00",
        "recurrence": "weekly",
        "completed": True
    }
    
    response = client.put(f"/api/test_user_123/tasks/{task_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated description"
    assert data["priority"] == "high"
    assert data["tags"] == ["updated", "important"]
    assert data["recurrence"] == "weekly"
    assert data["completed"] is True


def test_delete_task():
    """Test deleting a task"""
    # First create a task
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    task_data = {
        "title": "Task to Delete",
        "description": "This task will be deleted",
        "priority": "medium",
        "tags": ["delete"],
        "due_date": "2023-12-31T10:00:00",
        "recurrence": "none"
    }
    
    create_response = client.post("/api/test_user_123/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Verify the task exists
    get_response = client.get(f"/api/test_user_123/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 200
    
    # Now delete the task
    delete_response = client.delete(f"/api/test_user_123/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # Verify the task is gone
    get_deleted_response = client.get(f"/api/test_user_123/tasks/{task_id}", headers=headers)
    assert get_deleted_response.status_code == 404


def test_mark_task_complete():
    """Test marking a task as complete/incomplete"""
    # First create a task
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    task_data = {
        "title": "Task to Complete",
        "description": "This task will be marked complete",
        "priority": "medium",
        "tags": ["complete"],
        "due_date": "2023-12-31T10:00:00",
        "recurrence": "none"
    }
    
    create_response = client.post("/api/test_user_123/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Mark the task as complete
    response = client.patch(f"/api/test_user_123/tasks/{task_id}/complete?completed=true", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is True
    
    # Mark the task as incomplete
    response = client.patch(f"/api/test_user_123/tasks/{task_id}/complete?completed=false", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is False


def test_cross_user_access_prevention():
    """Test that users cannot access other users' tasks"""
    # Create a task for user 1
    token_user1 = create_test_token("user1")
    headers_user1 = {"Authorization": f"Bearer {token_user1}"}
    
    task_data = {
        "title": "User 1 Task",
        "description": "This belongs to user 1",
        "priority": "medium",
        "tags": ["user1"],
        "due_date": "2023-12-31T10:00:00",
        "recurrence": "none"
    }
    
    create_response = client.post("/api/user1/tasks", json=task_data, headers=headers_user1)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Try to access user 1's task as user 2
    token_user2 = create_test_token("user2")
    headers_user2 = {"Authorization": f"Bearer {token_user2}"}
    
    # This should fail with 403 or 404
    response = client.get(f"/api/user1/tasks/{task_id}", headers=headers_user2)
    assert response.status_code in [403, 404]  # Either forbidden or not found to prevent enumeration


def test_search_and_filter():
    """Test search and filtering functionality"""
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a few tasks with different properties
    tasks = [
        {
            "title": "High Priority Task",
            "description": "This is a high priority task",
            "priority": "high",
            "tags": ["urgent"],
            "due_date": "2023-12-31T10:00:00",
            "recurrence": "none"
        },
        {
            "title": "Low Priority Task",
            "description": "This is a low priority task",
            "priority": "low",
            "tags": ["later"],
            "due_date": "2024-12-31T10:00:00",
            "recurrence": "none"
        },
        {
            "title": "Completed Task",
            "description": "This task is completed",
            "priority": "medium",
            "tags": ["done"],
            "due_date": "2023-06-15T10:00:00",
            "recurrence": "none",
            "completed": True
        }
    ]
    
    # Create the tasks
    task_ids = []
    for task_data in tasks:
        response = client.post("/api/test_user_123/tasks", json=task_data, headers=headers)
        assert response.status_code == 201
        task_ids.append(response.json()["id"])
    
    # Test search by title
    search_response = client.get("/api/test_user_123/tasks?search=High", headers=headers)
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert len(search_results) >= 1
    assert any("High Priority Task" in task["title"] for task in search_results)
    
    # Test filter by priority
    priority_response = client.get("/api/test_user_123/tasks?priority=high", headers=headers)
    assert priority_response.status_code == 200
    priority_results = priority_response.json()
    assert len(priority_results) >= 1
    assert all(task["priority"] == "high" for task in priority_results)
    
    # Test filter by status
    status_response = client.get("/api/test_user_123/tasks?status=completed", headers=headers)
    assert status_response.status_code == 200
    status_results = status_response.json()
    assert len(status_results) >= 1
    assert all(task["completed"] is True for task in status_results)
    
    # Clean up created tasks
    for task_id in task_ids:
        client.delete(f"/api/test_user_123/tasks/{task_id}", headers=headers)