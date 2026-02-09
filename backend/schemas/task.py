from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="medium", regex="^(low|medium|high)$")
    tags: Optional[List[str]] = Field(None)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(default="none", regex="^(none|daily|weekly|monthly)$")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, regex="^(low|medium|high)$")
    tags: Optional[List[str]] = Field(None)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(None, regex="^(none|daily|weekly|monthly)$")


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurrence: str
    created_at: datetime
    updated_at: datetime