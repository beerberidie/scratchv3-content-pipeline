"""
Task management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.dependencies import get_current_active_user
from app.services.storage import storage_service

router = APIRouter()


class TaskCreateRequest(BaseModel):
    topic: str
    rules: str
    article_content: Optional[str] = None
    include_image: bool = False
    scheduled_time: Optional[datetime] = None
    process_enabled: bool = True
    wordpress_url: Optional[str] = None
    recipient_email: Optional[str] = None  # Support legacy field
    referenced_chats: List[str] = []


class TaskUpdateRequest(BaseModel):
    topic: Optional[str] = None
    rules: Optional[str] = None
    article_content: Optional[str] = None
    include_image: Optional[bool] = None
    scheduled_time: Optional[datetime] = None
    process_enabled: Optional[bool] = None
    wordpress_url: Optional[str] = None
    recipient_email: Optional[str] = None  # Support legacy field
    referenced_chats: Optional[List[str]] = None


class TaskResponse(BaseModel):
    id: str
    topic: str
    rules: str
    article_content: Optional[str]
    include_image: bool
    scheduled_time: Optional[datetime] = None
    process_enabled: bool
    wordpress_url: Optional[str] = None  # Made optional for backward compatibility
    recipient_email: Optional[str] = None  # Support legacy field
    referenced_chats: List[str]
    status: str
    created_at: str
    updated_at: str

    # Optional fields that may be present in stored data
    generated_content: Optional[str] = None
    image_urls: Optional[List[str]] = None
    content_id: Optional[str] = None
    email_sent: Optional[bool] = None
    email_sent_at: Optional[str] = None
    error_message: Optional[str] = None
    warning_message: Optional[str] = None
    wordpress_error: Optional[str] = None
    wordpress_posted: Optional[bool] = None
    wordpress_post_id: Optional[str] = None
    wordpress_edit_link: Optional[str] = None


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get all tasks for the current user
    """
    tasks = storage_service.get_user_tasks(current_user["username"])
    return [TaskResponse(**task) for task in tasks]


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a new task
    """
    # Determine if this should be executed immediately (no schedule time and no WordPress URL)
    should_execute_immediately = (
        request.scheduled_time is None and
        not request.wordpress_url and
        not request.recipient_email
    )

    task_data = {
        "topic": request.topic,
        "rules": request.rules,
        "article_content": request.article_content,
        "include_image": request.include_image,
        "process_enabled": request.process_enabled,
        "referenced_chats": request.referenced_chats
    }

    # Add scheduled_time if provided
    if request.scheduled_time:
        task_data["scheduled_time"] = request.scheduled_time.isoformat()

    # Add wordpress_url or recipient_email if provided
    if request.wordpress_url:
        task_data["wordpress_url"] = request.wordpress_url
    if request.recipient_email:
        task_data["recipient_email"] = request.recipient_email

    task = storage_service.create_task(current_user["username"], task_data)

    # If should execute immediately, process the task right away
    if should_execute_immediately:
        from app.services.content_generator import content_engine
        try:
            # Get user settings
            user_settings = current_user.get("settings", {})

            # Execute the task immediately
            result = await content_engine.process_task(task, user_settings)

            if result["success"]:
                # Task will be marked as completed and stored in history
                pass
            else:
                # Task will be marked as failed with error message
                pass

        except Exception as e:
            # If execution fails, the task will remain with error status
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing immediate task: {e}")

    # Schedule the task if it has a scheduled time and scheduler is running
    elif request.scheduled_time:
        from app.services.scheduler import task_scheduler
        if task_scheduler.is_running:
            await task_scheduler.schedule_task(task)

    # Reload task to get updated status after potential execution
    updated_task = storage_service.get_task(current_user["username"], task["id"])
    return TaskResponse(**updated_task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get a specific task by ID
    """
    task = storage_service.get_task(current_user["username"], task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(**task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update an existing task
    """
    # Prepare update data (only include non-None values)
    updates = {}
    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None:
            if field == "scheduled_time" and isinstance(value, datetime):
                updates[field] = value.isoformat()
            else:
                updates[field] = value

    task = storage_service.update_task(current_user["username"], task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(**task)


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a task
    """
    success = storage_service.delete_task(current_user["username"], task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/execute")
async def execute_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Manually execute a task (trigger content generation)
    """
    from app.services.content_generator import content_engine

    task = storage_service.get_task(current_user["username"], task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if task is already completed or in progress
    if task.get("status") in ["completed", "in_progress"]:
        raise HTTPException(
            status_code=400,
            detail=f"Task is already {task['status']}"
        )

    # Get user settings
    user_settings = current_user.get("settings", {})

    # Execute the task
    result = await content_engine.process_task(task, user_settings)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Task execution failed"))

    return {
        "message": "Task executed successfully",
        "task_id": task_id,
        "content_id": result.get("content_id"),
        "email_sent": result.get("email_result", {}).get("success", False)
    }


@router.post("/execute-all")
async def execute_all_pending_tasks(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Execute all pending tasks for the current user
    """
    from app.services.content_generator import content_engine

    # Get all pending tasks for user
    tasks = storage_service.get_user_tasks(current_user["username"])
    pending_tasks = [task for task in tasks if task.get("status") == "pending"]

    if not pending_tasks:
        return {
            "message": "No pending tasks found",
            "executed_count": 0,
            "results": []
        }

    # Get user settings
    user_settings = current_user.get("settings", {})

    # Execute all pending tasks
    results = []
    success_count = 0

    for task in pending_tasks:
        try:
            result = await content_engine.process_task(task, user_settings)
            results.append({
                "task_id": task["id"],
                "topic": task["topic"],
                "success": result["success"],
                "content_id": result.get("content_id"),
                "email_sent": result.get("email_result", {}).get("success", False),
                "error": result.get("error")
            })

            if result["success"]:
                success_count += 1

        except Exception as e:
            results.append({
                "task_id": task["id"],
                "topic": task["topic"],
                "success": False,
                "error": str(e)
            })

    return {
        "message": f"Executed {len(pending_tasks)} tasks, {success_count} successful",
        "executed_count": len(pending_tasks),
        "success_count": success_count,
        "results": results
    }
