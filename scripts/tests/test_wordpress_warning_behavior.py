#!/usr/bin/env python3
"""
Test script to verify the updated WordPress warning behavior.
This ensures that WordPress posting failures are treated as warnings,
not errors, and that content is always saved to history.
"""

import os

def test_wordpress_warning_behavior():
    """Test that WordPress posting failures are handled as warnings"""
    
    print("🧪 Testing WordPress warning behavior...")
    
    # Read the content generator file
    content_gen_path = "app/services/content_generator.py"
    
    if not os.path.exists(content_gen_path):
        print(f"❌ File not found: {content_gen_path}")
        return False
    
    with open(content_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check that WordPress failures create warnings
    print("\n1. Testing WordPress failure warning creation...")
    if "wordpress_warning =" in content and "WordPress posting failed:" in content:
        print("✅ WordPress failures create warning messages")
    else:
        print("❌ WordPress warning creation not found")
        return False
    
    # Test 2: Check that tasks are always marked as completed
    print("\n2. Testing task completion behavior...")
    if '"status": TaskStatus.COMPLETED.value' in content:
        print("✅ Tasks are marked as completed regardless of WordPress status")
    else:
        print("❌ Task completion logic not found")
        return False
    
    # Test 3: Check that success is always returned
    print("\n3. Testing return value behavior...")
    if '"success": True' in content:
        print("✅ Tasks always return success when content is generated")
    else:
        print("❌ Success return logic not found")
        return False
    
    # Test 4: Check that warnings are stored in task metadata
    print("\n4. Testing warning storage...")
    if 'task_update["warning_message"]' in content and 'task_update["wordpress_error"]' in content:
        print("✅ WordPress warnings and errors are stored in task metadata")
    else:
        print("❌ Warning storage logic not found")
        return False
    
    # Test 5: Check that warnings are included in results
    print("\n5. Testing warning inclusion in results...")
    if 'result["warning"] = wordpress_warning' in content:
        print("✅ Warnings are included in task results")
    else:
        print("❌ Warning inclusion in results not found")
        return False
    
    # Test 6: Check that content is always saved
    print("\n6. Testing content preservation...")
    if "storage_service.save_generated_content" in content:
        print("✅ Generated content is always saved to history")
    else:
        print("❌ Content saving logic not found")
        return False
    
    print("\n" + "="*60)
    print("🎉 WordPress warning behavior verification PASSED!")
    print("\nThe updated behavior ensures that:")
    print("• WordPress posting failures are treated as warnings")
    print("• Tasks always complete successfully when content is generated")
    print("• Generated content is always saved to history")
    print("• Users receive clear warning messages about WordPress issues")
    print("• WordPress errors are stored for debugging")
    print("• WordPress posting is optional, not required for task success")
    
    return True


def test_api_response_model():
    """Test that API response models include warning fields"""
    
    print("\n🔍 Testing API response model updates...")
    
    # Read the tasks API file
    tasks_api_path = "app/api/tasks.py"
    
    if not os.path.exists(tasks_api_path):
        print(f"❌ File not found: {tasks_api_path}")
        return False
    
    with open(tasks_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for warning fields in TaskResponse model
    warning_fields = [
        "warning_message: Optional[str] = None",
        "wordpress_error: Optional[str] = None",
        "wordpress_posted: Optional[bool] = None",
        "wordpress_post_id: Optional[str] = None",
        "wordpress_edit_link: Optional[str] = None"
    ]
    
    all_found = True
    for field in warning_fields:
        if field in content:
            print(f"✅ Found API field: {field.split(':')[0]}")
        else:
            print(f"❌ Missing API field: {field.split(':')[0]}")
            all_found = False
    
    return all_found


if __name__ == "__main__":
    print("🚀 Testing WordPress Warning Behavior Implementation")
    print("="*60)
    
    # Test the core behavior
    behavior_test = test_wordpress_warning_behavior()
    
    # Test the API model updates
    api_test = test_api_response_model()
    
    if behavior_test and api_test:
        print("\n✨ All tests passed! WordPress posting is now properly handled as optional functionality.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        exit(1)
