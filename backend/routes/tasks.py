from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from ..auth.dependencies import get_current_user, verify_user_id
from ..models.task import Task, TaskCreate, TaskUpdate, TaskResponse
from ..db import engine
from datetime import datetime
import json
import logging


router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])


@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search term to match against title and description"),
    status_param: Optional[str] = Query(None, alias="status", description="Filter by completion status ('completed' or 'pending')"),
    priority: Optional[str] = Query(None, description="Filter by priority ('low', 'medium', 'high')"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort: Optional[str] = Query(None, description="Sort order ('created_at', 'title', 'priority', 'due_date')")
):
    """
    Retrieve all tasks for a specific user with optional filtering, searching, and sorting.
    """
    # Verify that the user ID in the token matches the user ID in the path
    verify_user_id(current_user_id, user_id)
    
    with Session(engine) as session:
        # Build the query
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where((Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern)))
        
        # Apply status filter
        if status_param:
            if status_param.lower() == "completed":
                query = query.where(Task.completed == True)
            elif status_param.lower() == "pending":
                query = query.where(Task.completed == False)
            else:
                raise HTTPException(status_code=400, detail="Status must be 'completed' or 'pending'")
        
        # Apply priority filter
        if priority:
            query = query.where(Task.priority == priority)
        
        # Apply tag filter
        if tag:
            # Since tags are stored as JSON, we need to search within the JSON
            query = query.where(Task.tags.like(f'%{tag}%'))
        
        # Apply sorting
        if sort:
            if sort == "created_at":
                query = query.order_by(Task.created_at.desc())
            elif sort == "title":
                query = query.order_by(Task.title.asc())
            elif sort == "priority":
                query = query.order_by(Task.priority.asc())
            elif sort == "due_date":
                query = query.order_by(Task.due_date.asc())
            else:
                # Default to created_at if invalid sort parameter
                query = query.order_by(Task.created_at.desc())
        else:
            # Default sorting
            query = query.order_by(Task.created_at.desc())
        
        tasks = session.exec(query).all()
        
        # Convert to response model
        response_tasks = []
        for task in tasks:
            task_dict = task.dict()
            # Normalize tags whether stored as JSON string or as a list (Postgres array)
            if isinstance(task.tags, list):
                task_dict["tags"] = task.tags
            elif isinstance(task.tags, str):
                try:
                    parsed_tags = json.loads(task.tags)
                    task_dict["tags"] = parsed_tags if isinstance(parsed_tags, list) else []
                except Exception:
                    task_dict["tags"] = []
            else:
                task_dict["tags"] = []

            response_task = TaskResponse(**task_dict)
            response_tasks.append(response_task)
        
        return response_tasks


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(user_id: str, task_data: TaskCreate, current_user_id: str = Depends(get_current_user)):
    """
    Create a new task for the specified user.
    """
    # Verify that the user ID in the token matches the user ID in the path
    verify_user_id(current_user_id, user_id)
    
    logger = logging.getLogger(__name__)
    try:
        with Session(engine) as session:
            # Determine DB dialect to decide how to store tags
            try:
                dialect = engine.dialect.name
            except Exception:
                dialect = None

            # Prepare tags for DB storage
            tags_for_db = None
            if task_data.tags:
                if dialect == "postgresql":
                    # Let the DB driver accept a Python list for Postgres array columns
                    tags_for_db = task_data.tags
                else:
                    # Default: store as JSON string
                    tags_for_db = json.dumps(task_data.tags)

            # Create the task object
            db_task = Task(
                title=task_data.title,
                description=task_data.description,
                completed=False,  # Default to not completed
                priority=task_data.priority,
                tags=tags_for_db,
                due_date=task_data.due_date,
                recurrence=task_data.recurrence,
                user_id=user_id
            )

            session.add(db_task)
            session.commit()
            session.refresh(db_task)

            # Convert to response model
            # Normalize tags for response: if the DB returned a JSON string, parse it,
            # if it returned a list already, use it directly.
            task_dict = db_task.dict()
            if isinstance(db_task.tags, list):
                task_dict["tags"] = db_task.tags
            elif isinstance(db_task.tags, str):
                try:
                    task_dict["tags"] = json.loads(db_task.tags)
                except Exception:
                    task_dict["tags"] = []
            else:
                task_dict["tags"] = []

            return TaskResponse(**task_dict)
    except Exception as e:
        logger.exception("Error creating task for user %s: %s", user_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{id}", response_model=TaskResponse)
def get_task(user_id: str, id: int, current_user_id: str = Depends(get_current_user)):
    """
    Retrieve a specific task by ID for the specified user.
    """
    # Verify that the user ID in the token matches the user ID in the path
    verify_user_id(current_user_id, user_id)
    
    with Session(engine) as session:
        task = session.get(Task, id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: Task does not belong to user")
        
        # Convert to response model
        task_dict = task.dict()
        # Normalize tags stored as list or JSON string
        if isinstance(task.tags, list):
            task_dict["tags"] = task.tags
        elif isinstance(task.tags, str):
            try:
                parsed_tags = json.loads(task.tags)
                task_dict["tags"] = parsed_tags if isinstance(parsed_tags, list) else []
            except Exception:
                task_dict["tags"] = []
        else:
            task_dict["tags"] = []

        return TaskResponse(**task_dict)


@router.put("/tasks/{id}", response_model=TaskResponse)
def update_task(user_id: str, id: int, task_data: TaskUpdate, current_user_id: str = Depends(get_current_user)):
    """
    Update an existing task for the specified user.
    """
    # Verify that the user ID in the token matches the user ID in the path
    verify_user_id(current_user_id, user_id)
    
    with Session(engine) as session:
        task = session.get(Task, id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: Task does not belong to user")
        
        # Update the task with provided data
        update_data = task_data.dict(exclude_unset=True)
        
        # Handle tags separately: if DB is Postgres and expects an array, leave as list;
        # otherwise convert to JSON string for storage.
        if "tags" in update_data and update_data["tags"] is not None:
            try:
                dialect = engine.dialect.name
            except Exception:
                dialect = None

            if dialect == "postgresql":
                # leave as list
                pass
            else:
                update_data["tags"] = json.dumps(update_data["tags"])
        
        # Update updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Convert to response model
        task_dict = task.dict()
        # Normalize tags stored as list or JSON string
        if isinstance(task.tags, list):
            task_dict["tags"] = task.tags
        elif isinstance(task.tags, str):
            try:
                parsed_tags = json.loads(task.tags)
                task_dict["tags"] = parsed_tags if isinstance(parsed_tags, list) else []
            except Exception:
                task_dict["tags"] = []
        else:
            task_dict["tags"] = []

        return TaskResponse(**task_dict)


@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(user_id: str, id: int, current_user_id: str = Depends(get_current_user)):
    """
    Delete a specific task for the specified user.
    """
    # Verify that the user ID in the token matches the user ID in the path
    verify_user_id(current_user_id, user_id)
    
    with Session(engine) as session:
        task = session.get(Task, id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: Task does not belong to user")
        
        session.delete(task)
        session.commit()
        
        return


@router.patch("/tasks/{id}/complete", response_model=TaskResponse)
def update_task_completion(
    user_id: str, 
    id: int, 
    completed: bool = Query(..., description="Whether the task is completed"),
    current_user_id: str = Depends(get_current_user)
):
    """
    Mark a task as complete or incomplete for the specified user.
    """
    # Verify that the user ID in the token matches the user ID in the path
    verify_user_id(current_user_id, user_id)
    
    with Session(engine) as session:
        task = session.get(Task, id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: Task does not belong to user")
        
        # Update the completion status
        task.completed = completed
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Convert to response model
        task_dict = task.dict()
        # Normalize tags whether stored as a list or JSON string
        if isinstance(task.tags, list):
            task_dict["tags"] = task.tags
        elif isinstance(task.tags, str):
            try:
                parsed_tags = json.loads(task.tags)
                task_dict["tags"] = parsed_tags if isinstance(parsed_tags, list) else []
            except Exception:
                task_dict["tags"] = []
        else:
            task_dict["tags"] = []
        
        return TaskResponse(**task_dict)