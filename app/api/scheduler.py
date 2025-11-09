"""
Scheduler management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.dependencies import get_current_active_user
from app.services.scheduler import task_scheduler
from app.services.storage import storage_service

router = APIRouter()


class SchedulerStatus(BaseModel):
    is_running: bool
    scheduled_jobs_count: int
    pending_tasks_count: int
    jobs: List[Dict[str, Any]]


@router.get("/status", response_model=SchedulerStatus)
async def get_scheduler_status(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get scheduler status and information
    """
    # Get pending tasks for current user
    user_tasks = storage_service.get_user_tasks(current_user["username"])
    pending_tasks = [task for task in user_tasks if task.get("status") == "pending"]
    
    # Get scheduled jobs
    jobs = task_scheduler.get_scheduled_jobs() if task_scheduler.is_running else []
    
    return SchedulerStatus(
        is_running=task_scheduler.is_running,
        scheduled_jobs_count=len(jobs),
        pending_tasks_count=len(pending_tasks),
        jobs=jobs
    )


@router.post("/start")
async def start_scheduler(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Start the task scheduler
    """
    if task_scheduler.is_running:
        return {"message": "Scheduler is already running"}
    
    task_scheduler.start()
    scheduled_count = await task_scheduler.reschedule_all_pending_tasks()
    
    return {
        "message": "Scheduler started successfully",
        "scheduled_tasks": scheduled_count
    }


@router.post("/stop")
async def stop_scheduler(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Stop the task scheduler
    """
    if not task_scheduler.is_running:
        return {"message": "Scheduler is not running"}
    
    task_scheduler.stop()
    
    return {"message": "Scheduler stopped successfully"}


@router.post("/reschedule")
async def reschedule_all_tasks(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Reschedule all pending tasks
    """
    if not task_scheduler.is_running:
        raise HTTPException(status_code=400, detail="Scheduler is not running")
    
    scheduled_count = await task_scheduler.reschedule_all_pending_tasks()
    
    return {
        "message": f"Rescheduled {scheduled_count} pending tasks",
        "scheduled_count": scheduled_count
    }


@router.post("/schedule-task/{task_id}")
async def schedule_specific_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Schedule a specific task
    """
    if not task_scheduler.is_running:
        raise HTTPException(status_code=400, detail="Scheduler is not running")
    
    # Get the task
    task = storage_service.get_task(current_user["username"], task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Schedule the task
    await task_scheduler.schedule_task(task)
    
    return {
        "message": f"Task {task_id} scheduled successfully",
        "task_id": task_id,
        "scheduled_time": task.get("scheduled_time")
    }


@router.delete("/unschedule-task/{task_id}")
async def unschedule_specific_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Remove a specific task from the schedule
    """
    if not task_scheduler.is_running:
        raise HTTPException(status_code=400, detail="Scheduler is not running")
    
    # Verify task belongs to user
    task = storage_service.get_task(current_user["username"], task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Unschedule the task
    await task_scheduler.unschedule_task(task_id)
    
    return {
        "message": f"Task {task_id} unscheduled successfully",
        "task_id": task_id
    }


@router.get("/jobs")
async def get_scheduled_jobs(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get list of all scheduled jobs
    """
    if not task_scheduler.is_running:
        return {"jobs": [], "message": "Scheduler is not running"}
    
    jobs = task_scheduler.get_scheduled_jobs()
    
    return {
        "jobs": jobs,
        "count": len(jobs),
        "scheduler_running": True
    }


@router.get("/pending-tasks")
async def get_pending_tasks(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get pending tasks for the current user
    """
    user_tasks = storage_service.get_user_tasks(current_user["username"])
    pending_tasks = []
    
    for task in user_tasks:
        if task.get("status") == "pending":
            # Check if task is due
            scheduled_time_str = task.get("scheduled_time")
            is_due = False
            
            if scheduled_time_str:
                try:
                    if isinstance(scheduled_time_str, str):
                        scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                    else:
                        scheduled_time = scheduled_time_str
                    
                    is_due = scheduled_time <= datetime.now(timezone.utc)
                except:
                    pass
            
            pending_tasks.append({
                "id": task["id"],
                "topic": task["topic"],
                "scheduled_time": scheduled_time_str,
                "process_enabled": task.get("process_enabled", True),
                "recipient_email": task.get("recipient_email", ""),
                "is_due": is_due,
                "created_at": task.get("created_at")
            })
    
    # Sort by scheduled time
    pending_tasks.sort(key=lambda x: x.get("scheduled_time", ""))
    
    return {
        "pending_tasks": pending_tasks,
        "count": len(pending_tasks),
        "due_count": sum(1 for task in pending_tasks if task["is_due"])
    }
