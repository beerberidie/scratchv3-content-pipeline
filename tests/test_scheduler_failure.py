"""
Tests for scheduler failure handling and resilience
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.services.scheduler import TaskScheduler
from app.services.storage import storage_service


class TestSchedulerFailure:
    """Test that forced exceptions mark jobs as FAILED"""
    
    def setup_method(self):
        """Setup test environment"""
        self.scheduler = TaskScheduler()
        
    def test_redis_lock_initialization(self):
        """Test Redis lock setup"""
        # Test that scheduler initializes with Redis client
        assert hasattr(self.scheduler, 'redis_client')
        assert hasattr(self.scheduler, 'redis_lock')
    
    @pytest.mark.asyncio
    async def test_redis_lock_context_manager(self):
        """Test Redis lock context manager functionality"""
        # Mock Redis client
        mock_redis = Mock()
        mock_lock = Mock()
        mock_lock.acquire = AsyncMock(return_value=True)
        mock_lock.release = AsyncMock()
        mock_redis.lock.return_value = mock_lock
        
        self.scheduler.redis_client = mock_redis
        
        # Test successful lock acquisition and release
        async with self.scheduler.redis_lock("test-lock"):
            pass
        
        mock_redis.lock.assert_called_once_with("test-lock", timeout=300)
        mock_lock.acquire.assert_called_once_with(blocking=False)
        mock_lock.release.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redis_lock_acquisition_failure(self):
        """Test behavior when Redis lock cannot be acquired"""
        # Mock Redis client with failed lock acquisition
        mock_redis = Mock()
        mock_lock = Mock()
        mock_lock.acquire = AsyncMock(return_value=False)
        mock_redis.lock.return_value = mock_lock

        self.scheduler.redis_client = mock_redis

        # Test that context manager handles failed acquisition gracefully
        executed = False
        async with self.scheduler.redis_lock("test-lock"):
            executed = True

        # Should not execute the block if lock acquisition fails
        assert not executed
        mock_lock.acquire.assert_called_once_with(blocking=False)
        # Should not try to release a lock that was never acquired
        mock_lock.release.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_redis_unavailable_fallback(self):
        """Test behavior when Redis is unavailable"""
        # Set Redis client to None (unavailable)
        self.scheduler.redis_client = None
        
        executed = False
        async with self.scheduler.redis_lock("test-lock"):
            executed = True
        
        # Should execute without locking when Redis is unavailable
        assert executed
    
    @pytest.mark.asyncio
    async def test_task_execution_with_exception(self):
        """Test that task execution exceptions are handled and marked as FAILED"""
        # Mock task data
        task_id = "test-task-123"
        user_id = "test-user"
        
        mock_task = {
            "id": task_id,
            "user_id": user_id,
            "status": "pending",
            "process_enabled": True,
            "topic": "Test Topic"
        }
        
        # Mock storage service
        with patch.object(storage_service, 'get_task') as mock_get_task:
            with patch.object(storage_service, 'update_task') as mock_update_task:
                with patch('app.services.auth.auth_service.get_user') as mock_get_user:
                    with patch('app.services.content_generator.content_engine.process_task') as mock_process:
                        
                        mock_get_task.return_value = mock_task
                        mock_get_user.return_value = {"settings": {}}
                        
                        # Make process_task raise an exception
                        mock_process.side_effect = Exception("Simulated task failure")
                        
                        # Execute the task
                        await self.scheduler._execute_scheduled_task(task_id, user_id)
                        
                        # Verify task was marked as failed
                        mock_update_task.assert_called_once_with(
                            user_id, 
                            task_id, 
                            {
                                "status": "failed",
                                "error_message": "Simulated task failure"
                            }
                        )
    
    @pytest.mark.asyncio
    async def test_task_execution_with_redis_lock(self):
        """Test that task execution uses Redis locking"""
        task_id = "test-task-456"
        user_id = "test-user"
        
        mock_task = {
            "id": task_id,
            "user_id": user_id,
            "status": "pending",
            "process_enabled": True,
            "topic": "Test Topic"
        }
        
        # Mock Redis lock
        mock_redis = Mock()
        mock_lock = Mock()
        mock_lock.acquire = AsyncMock(return_value=True)
        mock_lock.release = AsyncMock()
        mock_redis.lock.return_value = mock_lock
        
        self.scheduler.redis_client = mock_redis
        
        with patch.object(storage_service, 'get_task') as mock_get_task:
            with patch('app.services.auth.auth_service.get_user') as mock_get_user:
                with patch('app.services.content_generator.content_engine.process_task') as mock_process:
                    
                    mock_get_task.return_value = mock_task
                    mock_get_user.return_value = {"settings": {}}
                    mock_process.return_value = {"success": True}
                    
                    # Execute the task
                    await self.scheduler._execute_scheduled_task(task_id, user_id)
                    
                    # Verify Redis lock was used
                    mock_redis.lock.assert_called_once_with(f"task-{task_id}", timeout=300)
                    mock_lock.acquire.assert_called_once_with(blocking=False)
                    mock_lock.release.assert_called_once()
    
    def test_job_error_listener(self):
        """Test APScheduler job error listener"""
        # Mock event
        mock_event = Mock()
        mock_event.job_id = "task_test-123"
        mock_event.exception = Exception("Test exception")
        
        # Test error listener
        self.scheduler._job_error_listener(mock_event)
        
        # Should log error (we can't easily test logging, but ensure no exceptions)
        assert True  # If we get here, no exception was raised
    
    def test_job_executed_listener(self):
        """Test APScheduler job executed listener"""
        # Mock event
        mock_event = Mock()
        mock_event.job_id = "task_test-456"
        
        # Test executed listener
        self.scheduler._job_executed_listener(mock_event)
        
        # Should log success (we can't easily test logging, but ensure no exceptions)
        assert True  # If we get here, no exception was raised
    
    @pytest.mark.asyncio
    async def test_task_not_found_handling(self):
        """Test handling when task is not found"""
        task_id = "nonexistent-task"
        user_id = "test-user"
        
        with patch.object(storage_service, 'get_task') as mock_get_task:
            mock_get_task.return_value = None
            
            # Should handle gracefully without raising exception
            await self.scheduler._execute_scheduled_task(task_id, user_id)
            
            # No update should be called for nonexistent task
            with patch.object(storage_service, 'update_task') as mock_update_task:
                mock_update_task.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_task_already_processed_handling(self):
        """Test handling when task is no longer pending"""
        task_id = "completed-task"
        user_id = "test-user"
        
        mock_task = {
            "id": task_id,
            "user_id": user_id,
            "status": "completed",  # Not pending
            "process_enabled": True,
            "topic": "Test Topic"
        }
        
        with patch.object(storage_service, 'get_task') as mock_get_task:
            with patch('app.services.content_generator.content_engine.process_task') as mock_process:
                
                mock_get_task.return_value = mock_task
                
                # Execute the task
                await self.scheduler._execute_scheduled_task(task_id, user_id)
                
                # Process should not be called for non-pending task
                mock_process.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_disabled_task_handling(self):
        """Test handling when task is disabled"""
        task_id = "disabled-task"
        user_id = "test-user"
        
        mock_task = {
            "id": task_id,
            "user_id": user_id,
            "status": "pending",
            "process_enabled": False,  # Disabled
            "topic": "Test Topic"
        }
        
        with patch.object(storage_service, 'get_task') as mock_get_task:
            with patch('app.services.content_generator.content_engine.process_task') as mock_process:
                
                mock_get_task.return_value = mock_task
                
                # Execute the task
                await self.scheduler._execute_scheduled_task(task_id, user_id)
                
                # Process should not be called for disabled task
                mock_process.assert_not_called()
    
    def test_scheduler_configuration(self):
        """Test that scheduler is configured with proper settings"""
        # Verify scheduler has correct job defaults
        job_defaults = self.scheduler.scheduler.job_defaults
        
        assert job_defaults.get('max_instances') == 1
        assert job_defaults.get('misfire_grace_time') == 60
