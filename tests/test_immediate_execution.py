"""
Tests for immediate task execution when no schedule time or WordPress URL is provided
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


class TestImmediateExecution:
    """Test immediate task execution functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = TestClient(app)
        self.test_user = {"email": "test@example.com", "username": "testuser"}
        
        # Mock authentication
        self.auth_patcher = patch('app.dependencies.get_current_active_user')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = self.test_user
        
        # Mock storage service
        self.storage_patcher = patch('app.api.tasks.storage_service')
        self.mock_storage = self.storage_patcher.start()
        
        # Mock content engine
        self.content_patcher = patch('app.api.tasks.content_engine')
        self.mock_content_engine = self.content_patcher.start()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.auth_patcher.stop()
        self.storage_patcher.stop()
        self.content_patcher.stop()
    
    def test_immediate_execution_no_schedule_no_wordpress(self):
        """Test that task executes immediately when no schedule time and no WordPress URL"""
        # Mock task creation
        mock_task = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        self.mock_storage.create_task.return_value = mock_task
        
        # Mock successful content generation
        self.mock_content_engine.process_task.return_value = {
            "success": True,
            "content_id": "content-123"
        }
        
        # Mock updated task after execution
        updated_task = {**mock_task, "status": "completed"}
        self.mock_storage.get_task.return_value = updated_task
        
        # Create task without scheduled_time and wordpress_url
        response = self.client.post("/api/tasks/", json={
            "topic": "Test Topic",
            "rules": "Test rules",
            "article_content": "",
            "include_image": False,
            "process_enabled": True,
            "referenced_chats": []
        })
        
        assert response.status_code == 200
        
        # Verify task was created
        self.mock_storage.create_task.assert_called_once()
        
        # Verify content engine was called for immediate execution
        self.mock_content_engine.process_task.assert_called_once()
        
        # Verify task was retrieved after execution
        self.mock_storage.get_task.assert_called_once()
    
    def test_scheduled_execution_with_time(self):
        """Test that task is scheduled when scheduled_time is provided"""
        # Mock task creation
        mock_task = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "scheduled_time": "2024-12-31T23:59:59",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        self.mock_storage.create_task.return_value = mock_task
        self.mock_storage.get_task.return_value = mock_task
        
        # Mock scheduler
        with patch('app.api.tasks.task_scheduler') as mock_scheduler:
            mock_scheduler.is_running = True
            
            # Create task with scheduled_time
            response = self.client.post("/api/tasks/", json={
                "topic": "Test Topic",
                "rules": "Test rules",
                "scheduled_time": "2024-12-31T23:59:59",
                "process_enabled": True,
                "referenced_chats": []
            })
        
        assert response.status_code == 200
        
        # Verify task was created
        self.mock_storage.create_task.assert_called_once()
        
        # Verify content engine was NOT called (should be scheduled instead)
        self.mock_content_engine.process_task.assert_not_called()
        
        # Verify scheduler was called
        mock_scheduler.schedule_task.assert_called_once()
    
    def test_scheduled_execution_with_wordpress_url(self):
        """Test that task is scheduled when wordpress_url is provided"""
        # Mock task creation
        mock_task = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "wordpress_url": "https://example.com",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        self.mock_storage.create_task.return_value = mock_task
        self.mock_storage.get_task.return_value = mock_task
        
        # Create task with wordpress_url but no scheduled_time
        response = self.client.post("/api/tasks/", json={
            "topic": "Test Topic",
            "rules": "Test rules",
            "wordpress_url": "https://example.com",
            "process_enabled": True,
            "referenced_chats": []
        })
        
        assert response.status_code == 200
        
        # Verify task was created
        self.mock_storage.create_task.assert_called_once()
        
        # Verify content engine was NOT called (has WordPress URL so not immediate)
        self.mock_content_engine.process_task.assert_not_called()
    
    def test_immediate_execution_failure_handling(self):
        """Test that immediate execution failures are handled gracefully"""
        # Mock task creation
        mock_task = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        self.mock_storage.create_task.return_value = mock_task
        
        # Mock failed content generation
        self.mock_content_engine.process_task.return_value = {
            "success": False,
            "error": "Content generation failed"
        }
        
        # Mock updated task after failed execution
        failed_task = {**mock_task, "status": "failed"}
        self.mock_storage.get_task.return_value = failed_task
        
        # Create task without scheduled_time and wordpress_url
        response = self.client.post("/api/tasks/", json={
            "topic": "Test Topic",
            "rules": "Test rules",
            "process_enabled": True,
            "referenced_chats": []
        })
        
        # Should still return 200 even if execution fails
        assert response.status_code == 200
        
        # Verify task was created
        self.mock_storage.create_task.assert_called_once()
        
        # Verify content engine was called
        self.mock_content_engine.process_task.assert_called_once()
        
        # Verify task was retrieved after execution
        self.mock_storage.get_task.assert_called_once()
    
    def test_immediate_execution_exception_handling(self):
        """Test that exceptions during immediate execution are handled"""
        # Mock task creation
        mock_task = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        self.mock_storage.create_task.return_value = mock_task
        self.mock_storage.get_task.return_value = mock_task
        
        # Mock exception during content generation
        self.mock_content_engine.process_task.side_effect = Exception("Unexpected error")
        
        # Create task without scheduled_time and wordpress_url
        response = self.client.post("/api/tasks/", json={
            "topic": "Test Topic",
            "rules": "Test rules",
            "process_enabled": True,
            "referenced_chats": []
        })
        
        # Should still return 200 even if execution throws exception
        assert response.status_code == 200
        
        # Verify task was created
        self.mock_storage.create_task.assert_called_once()
        
        # Verify content engine was called
        self.mock_content_engine.process_task.assert_called_once()
        
        # Verify task was retrieved after execution attempt
        self.mock_storage.get_task.assert_called_once()


class TestTaskResponseModel:
    """Test that TaskResponse model handles optional scheduled_time"""
    
    def test_task_response_with_scheduled_time(self):
        """Test TaskResponse with scheduled_time"""
        from app.api.tasks import TaskResponse
        from datetime import datetime
        
        task_data = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "article_content": None,
            "include_image": False,
            "scheduled_time": datetime(2024, 12, 31, 23, 59, 59),
            "process_enabled": True,
            "referenced_chats": [],
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        response = TaskResponse(**task_data)
        assert response.scheduled_time is not None
        assert response.topic == "Test Topic"
    
    def test_task_response_without_scheduled_time(self):
        """Test TaskResponse without scheduled_time"""
        from app.api.tasks import TaskResponse
        
        task_data = {
            "id": "task-123",
            "topic": "Test Topic",
            "rules": "Test rules",
            "article_content": None,
            "include_image": False,
            "scheduled_time": None,
            "process_enabled": True,
            "referenced_chats": [],
            "status": "completed",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        response = TaskResponse(**task_data)
        assert response.scheduled_time is None
        assert response.topic == "Test Topic"
