from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import json


class TaskBase(SQLModel):
    """Base model for Task with common fields"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium", regex="^(low|medium|high)$")  # Using regex as a placeholder for enum
    tags: Optional[List[str]] = Field(default=None)  # API accepts list of tags
    due_date: Optional[datetime] = Field(default=None)
    recurrence: Optional[str] = Field(default="none", regex="^(none|daily|weekly|monthly)$")  # Using regex as a placeholder for enum


class Task(TaskBase, table=True):
    # Store tags as a JSON string in the DB model
    tags: Optional[str] = Field(default=None)  # type: ignore[assignment]
    # user_id belongs on the DB model (provided in the path for create/update requests)
    user_id: str = Field(index=True)
    """Task model for database table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(SQLModel):
    """Schema for updating an existing task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(default=None, regex="^(low|medium|high)$")
    tags: Optional[List[str]] = Field(default=None)  # Store as list in API, will convert to JSON for DB
    due_date: Optional[datetime] = Field(default=None)
    recurrence: Optional[str] = Field(default=None, regex="^(none|daily|weekly|monthly)$")


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    def dict(self, *args, **kwargs):
        """Override dict method to properly serialize tags as a list whether stored as str or list"""
        result = super().dict(*args, **kwargs)
        tags_value = getattr(self, "tags", None)
        if tags_value is None:
            result["tags"] = []
        elif isinstance(tags_value, list):
            result["tags"] = tags_value
        else:
            # tags stored as JSON string in DB
            try:
                result["tags"] = json.loads(tags_value)
            except json.JSONDecodeError:
                result["tags"] = []
        return result