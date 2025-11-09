"""
Task scheduling service for automated content generation with Redis locking
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import logging
import redis.asyncio as redis
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from app.services.storage import storage_service
from app.services.content_generator import content_engine
from app.services.auth import auth_service
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Service for scheduling and executing tasks automatically with Redis locking"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            job_defaults={
                'max_instances': 1,
                'misfire_grace_time': 60
            }
        )
        self.is_running = False
        self.redis_client = None
        self._setup_redis()
        self._setup_listeners()

    def _setup_redis(self):
        """Initialize Redis client for locking"""
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            logger.info("Redis client initialized for task locking")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            self.redis_client = None

    def _setup_listeners(self):
        """Setup APScheduler event listeners"""
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED)

    def _job_error_listener(self, event):
        """Handle job execution errors"""
        job_id = event.job_id
        exception = event.exception
        logger.error(f"Job {job_id} failed with exception: {exception}")

        # Extract task_id from job_id (format: "task_{task_id}")
        if job_id.startswith("task_"):
            task_id = job_id[5:]  # Remove "task_" prefix
            try:
                # Mark task as failed in storage
                # We need to get user_id from the job args or find another way
                # For now, we'll log the error and let the task execution handle it
                logger.error(f"Task {task_id} execution failed: {exception}")
            except Exception as e:
                logger.error(f"Failed to mark task {task_id} as failed: {e}")

    def _job_executed_listener(self, event):
        """Handle successful job execution"""
        job_id = event.job_id
        logger.info(f"Job {job_id} executed successfully")

    @asynccontextmanager
    async def redis_lock(self, lock_key: str, timeout: int = 300):
        """
        Redis-based distributed lock to prevent duplicate task execution

        Args:
            lock_key: Unique key for the lock
            timeout: Lock timeout in seconds
        """
        if not self.redis_client:
            # If Redis is not available, proceed without locking
            logger.warning("Redis not available, proceeding without lock")
            yield True  # Proceed as if lock was acquired
            return

        lock = None
        acquired = False
        try:
            # Acquire lock
            lock = self.redis_client.lock(lock_key, timeout=timeout)
            acquired = await lock.acquire(blocking=False)

            if not acquired:
                logger.warning(f"Could not acquire lock {lock_key}, task may already be running")
                # Don't yield - this prevents duplicate task execution
                # But we need to yield something to make the context manager work
                yield False  # Indicate lock was not acquired
                return

            logger.debug(f"Acquired lock {lock_key}")
            yield True  # Indicate lock was successfully acquired

        except Exception as e:
            logger.error(f"Error with Redis lock {lock_key}: {e}")
            yield True  # Proceed without lock if Redis fails
        finally:
            # Only try to release the lock if it was actually acquired
            if lock and acquired:
                try:
                    await lock.release()
                    logger.debug(f"Released lock {lock_key}")
                except Exception as e:
                    logger.error(f"Error releasing lock {lock_key}: {e}")
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            
            # Schedule periodic check for due tasks
            self.scheduler.add_job(
                self._check_due_tasks,
                IntervalTrigger(minutes=5),  # Check every 5 minutes
                id="check_due_tasks",
                replace_existing=True
            )
            
            logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Task scheduler stopped")
    
    async def schedule_task(self, task: Dict[str, Any]):
        """Schedule a task for execution at its scheduled time"""
        
        task_id = task["id"]
        scheduled_time_str = task.get("scheduled_time")
        
        if not scheduled_time_str:
            logger.warning(f"Task {task_id} has no scheduled time")
            return
        
        try:
            # Parse scheduled time
            if isinstance(scheduled_time_str, str):
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            else:
                scheduled_time = scheduled_time_str
            
            # Only schedule if the time is in the future
            if scheduled_time > datetime.now(timezone.utc):
                self.scheduler.add_job(
                    self._execute_scheduled_task,
                    DateTrigger(run_date=scheduled_time),
                    args=[task_id, task["user_id"]],
                    id=f"task_{task_id}",
                    replace_existing=True
                )
                
                logger.info(f"Scheduled task {task_id} for {scheduled_time}")
            else:
                logger.info(f"Task {task_id} scheduled time is in the past, will be processed immediately")
                
        except Exception as e:
            logger.error(f"Failed to schedule task {task_id}: {e}")
    
    async def unschedule_task(self, task_id: str):
        """Remove a task from the schedule"""
        try:
            self.scheduler.remove_job(f"task_{task_id}")
            logger.info(f"Unscheduled task {task_id}")
        except Exception as e:
            logger.warning(f"Failed to unschedule task {task_id}: {e}")
    
    async def _check_due_tasks(self):
        """Check for tasks that are due for execution"""
        try:
            # Get all pending tasks across all users
            pending_tasks = storage_service.get_pending_tasks()
            current_time = datetime.now(timezone.utc)
            
            for task in pending_tasks:
                # Check if task is due and process_enabled
                if not task.get("process_enabled", True):
                    continue
                
                scheduled_time_str = task.get("scheduled_time")
                if not scheduled_time_str:
                    continue
                
                try:
                    if isinstance(scheduled_time_str, str):
                        scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                    else:
                        scheduled_time = scheduled_time_str
                    
                    # If task is due (scheduled time has passed)
                    if scheduled_time <= current_time:
                        await self._execute_scheduled_task(task["id"], task["user_id"])
                        
                except Exception as e:
                    logger.error(f"Error processing due task {task['id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking due tasks: {e}")
    
    async def _execute_scheduled_task(self, task_id: str, user_id: str):
        """Execute a scheduled task with Redis locking"""
        lock_key = f"task-{task_id}"

        async with self.redis_lock(lock_key) as lock_acquired:
            # If lock_acquired is False, another instance is already processing this task
            if lock_acquired is False:
                logger.info(f"Task {task_id} is already being processed by another instance")
                return

            try:
                logger.info(f"Executing scheduled task {task_id} for user {user_id}")

                # Get the task
                task = storage_service.get_task(user_id, task_id)
                if not task:
                    logger.error(f"Task {task_id} not found")
                    return

                # Check if task is still pending and enabled
                if task.get("status") != "pending":
                    logger.info(f"Task {task_id} is no longer pending (status: {task.get('status')})")
                    return

                if not task.get("process_enabled", True):
                    logger.info(f"Task {task_id} is disabled")
                    return

                # Get user settings
                user_data = auth_service.get_user(user_id)
                if not user_data:
                    logger.error(f"User {user_id} not found")
                    return

                user_settings = user_data.get("settings", {})

                # Execute the task
                result = await content_engine.process_task(task, user_settings)

                if result["success"]:
                    logger.info(f"Successfully executed task {task_id}")
                else:
                    logger.error(f"Failed to execute task {task_id}: {result.get('error')}")
                    # Mark task as failed
                    storage_service.update_task(user_id, task_id, {
                        "status": "failed",
                        "error_message": result.get('error', 'Task execution failed')
                    })

            except Exception as e:
                logger.error(f"Error executing scheduled task {task_id}: {e}")

                # Mark task as failed
                try:
                    storage_service.update_task(user_id, task_id, {
                        "status": "failed",
                        "error_message": str(e)
                    })
                except Exception as update_error:
                    logger.error(f"Failed to update task status: {update_error}")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of currently scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    async def reschedule_all_pending_tasks(self):
        """Reschedule all pending tasks (useful after restart)"""
        try:
            pending_tasks = storage_service.get_pending_tasks()
            scheduled_count = 0
            
            for task in pending_tasks:
                if task.get("process_enabled", True) and task.get("scheduled_time"):
                    await self.schedule_task(task)
                    scheduled_count += 1
            
            logger.info(f"Rescheduled {scheduled_count} pending tasks")
            return scheduled_count
            
        except Exception as e:
            logger.error(f"Error rescheduling tasks: {e}")
            return 0


# Global scheduler instance
task_scheduler = TaskScheduler()


# Startup and shutdown functions
async def start_scheduler():
    """Start the task scheduler"""
    task_scheduler.start()
    await task_scheduler.reschedule_all_pending_tasks()


async def stop_scheduler():
    """Stop the task scheduler"""
    task_scheduler.stop()
