import os
import sys
import pytest
from fastapi.testclient import TestClient
# Ensure project root is on sys.path so `backend` package is importable when tests run
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# Use an in-memory SQLite DB for tests to avoid touching production DB schema
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("BETTER_AUTH_SECRET", "testsecret")
os.environ.setdefault("BETTER_AUTH_URL", "http://localhost:3000")

from backend.main import app
from backend.db import engine
from sqlmodel import Session, SQLModel
from backend.auth.jwt_handler import create_access_token
from datetime import timedelta


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create and teardown the test database schema for the entire session"""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
    # Optionally remove the test DB file if it's file-based; leave it for debugging



@pytest.fixture(scope="module")
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    with Session(engine) as session:
        # Create tables for testing
        SQLModel.metadata.create_all(engine)
        yield session
        # Clean up after each test
        session.rollback()


@pytest.fixture
def valid_token():
    """Create a valid JWT token for testing"""
    token_data = {"user_id": "test_user_123", "sub": "test_user_123"}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=30))
    return token


@pytest.fixture
def another_user_token():
    """Create a JWT token for a different user"""
    token_data = {"user_id": "another_user_456", "sub": "another_user_456"}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=30))
    return token