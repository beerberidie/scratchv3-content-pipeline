#!/usr/bin/env python3
"""
Test script to verify that WordPress posting failures are now properly handled
and cause task failures instead of being silently ignored.
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.content_generator import ContentGenerationEngine
from app.models.base import TaskStatus


async def test_wordpress_failure_handling():
    """Test that WordPress posting failures cause task failures"""
    
    print("🧪 Testing WordPress failure handling...")
    
    # Create content engine
    engine = ContentGenerationEngine()
    
    # Mock task with WordPress URL
    mock_task = {
        "id": "test-task-123",
        "user_id": "test-user",
        "topic": "Test Topic",
        "rules": "Test rules",
        "wordpress_url": "https://example.com/wp-json/wp/v2",
        "include_image": False
    }
    
    # Mock user settings
    mock_user_settings = {
        "ai_provider": "openai",
        "ai_model": "gpt-3.5-turbo"
    }
    
    # Test 1: WordPress posting failure should cause task failure
    print("\n1. Testing WordPress posting failure...")
    
    with patch('app.services.content_generator.ai_service') as mock_ai:
        with patch('app.services.content_generator.storage_service') as mock_storage:
            with patch.object(engine, '_post_to_wordpress') as mock_wp_post:
                
                # Mock successful content generation
                mock_ai.generate_content_with_messages.return_value = {
                    "success": True,
                    "content": "Test content"
                }
                
                # Mock WordPress posting failure
                mock_wp_post.return_value = {
                    "success": False,
                    "error": "WordPress authentication failed"
                }
                
                # Mock storage operations
                mock_storage.save_generated_content.return_value = "content-123"
                
                # Execute task
                result = await engine.process_task(mock_task, mock_user_settings)
                
                # Verify task failed due to WordPress posting failure
                if not result["success"]:
                    print("✅ Task correctly failed when WordPress posting failed")
                    print(f"   Error: {result.get('error')}")
                    
                    # Verify task was marked as failed in storage
                    update_calls = mock_storage.update_task.call_args_list
                    failed_update = None
                    for call in update_calls:
                        if call[0][2].get("status") == TaskStatus.FAILED.value:
                            failed_update = call[0][2]
                            break
                    
                    if failed_update:
                        print("✅ Task was correctly marked as FAILED in storage")
                        print(f"   Error message: {failed_update.get('error_message')}")
                        print(f"   WordPress error: {failed_update.get('wordpress_error')}")
                    else:
                        print("❌ Task was not marked as FAILED in storage")
                        return False
                        
                else:
                    print("❌ Task should have failed but didn't")
                    return False
    
    # Test 2: No WordPress URL should still succeed
    print("\n2. Testing task without WordPress URL...")
    
    mock_task_no_wp = mock_task.copy()
    del mock_task_no_wp["wordpress_url"]
    
    with patch('app.services.content_generator.ai_service') as mock_ai:
        with patch('app.services.content_generator.storage_service') as mock_storage:
            
            # Mock successful content generation
            mock_ai.generate_content_with_messages.return_value = {
                "success": True,
                "content": "Test content"
            }
            
            # Mock storage operations
            mock_storage.save_generated_content.return_value = "content-123"
            
            # Execute task
            result = await engine.process_task(mock_task_no_wp, mock_user_settings)
            
            # Verify task succeeded
            if result["success"]:
                print("✅ Task without WordPress URL succeeded correctly")
                
                # Verify task was marked as completed
                update_calls = mock_storage.update_task.call_args_list
                completed_update = None
                for call in update_calls:
                    if call[0][2].get("status") == TaskStatus.COMPLETED.value:
                        completed_update = call[0][2]
                        break
                
                if completed_update:
                    print("✅ Task was correctly marked as COMPLETED in storage")
                else:
                    print("❌ Task was not marked as COMPLETED in storage")
                    return False
                    
            else:
                print("❌ Task without WordPress URL should have succeeded")
                return False
    
    # Test 3: Successful WordPress posting should succeed
    print("\n3. Testing successful WordPress posting...")
    
    with patch('app.services.content_generator.ai_service') as mock_ai:
        with patch('app.services.content_generator.storage_service') as mock_storage:
            with patch.object(engine, '_post_to_wordpress') as mock_wp_post:
                
                # Mock successful content generation
                mock_ai.generate_content_with_messages.return_value = {
                    "success": True,
                    "content": "Test content"
                }
                
                # Mock successful WordPress posting
                mock_wp_post.return_value = {
                    "success": True,
                    "post": {"id": "123", "edit_link": "https://example.com/edit/123"}
                }
                
                # Mock storage operations
                mock_storage.save_generated_content.return_value = "content-123"
                
                # Execute task
                result = await engine.process_task(mock_task, mock_user_settings)
                
                # Verify task succeeded
                if result["success"]:
                    print("✅ Task with successful WordPress posting succeeded")
                    
                    # Verify task was marked as completed with WordPress data
                    update_calls = mock_storage.update_task.call_args_list
                    completed_update = None
                    for call in update_calls:
                        if call[0][2].get("status") == TaskStatus.COMPLETED.value:
                            completed_update = call[0][2]
                            break
                    
                    if completed_update and completed_update.get("wordpress_posted"):
                        print("✅ Task was correctly marked as COMPLETED with WordPress posting")
                        print(f"   WordPress post ID: {completed_update.get('wordpress_post_id')}")
                    else:
                        print("❌ Task was not properly updated with WordPress posting data")
                        return False
                        
                else:
                    print("❌ Task with successful WordPress posting should have succeeded")
                    return False
    
    print("\n🎉 All tests passed! WordPress failure handling is working correctly.")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_wordpress_failure_handling())
    if not success:
        sys.exit(1)
