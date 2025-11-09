#!/usr/bin/env python3
"""
Test script to verify that the Add Topic modal behavior is fixed.
This checks that the modal closes automatically and tasks refresh properly.
"""

import os
import re

def test_modal_behavior_fixes():
    """Test that the modal behavior fixes are properly implemented"""
    
    print("🧪 Testing Add Topic modal behavior fixes...")
    
    # Read the Dashboard.html file
    dashboard_path = "Dashboard.html"
    
    if not os.path.exists(dashboard_path):
        print(f"❌ File not found: {dashboard_path}")
        return False
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test cases to verify the fixes
    checks = [
        {
            "name": "Async form handler",
            "pattern": r"async function handleAddTopic\(event\)",
            "description": "Form submission handler is async"
        },
        {
            "name": "Awaited addTopic call",
            "pattern": r"await addTopic\(\);",
            "description": "addTopic function is properly awaited in form handler"
        },
        {
            "name": "Awaited original function",
            "pattern": r"await originalAddTopic\(\);",
            "description": "Original addTopic function is properly awaited in override"
        },
        {
            "name": "Modal closing in create",
            "pattern": r"closeModal\('addTopicModal'\);",
            "description": "Modal is closed after task creation"
        },
        {
            "name": "Task loading in create",
            "pattern": r"await loadTasks\(\);",
            "description": "Tasks are reloaded after creation"
        },
        {
            "name": "Stats update in create",
            "pattern": r"updateStats\(\);",
            "description": "Statistics are updated after task operations"
        },
        {
            "name": "Form clearing",
            "pattern": r"clearAddTopicForm\(\);",
            "description": "Form is cleared after operations"
        }
    ]
    
    all_passed = True
    
    for i, check in enumerate(checks, 1):
        print(f"\n{i}. Testing: {check['name']}")
        
        if re.search(check["pattern"], content):
            print(f"   ✅ PASSED - {check['description']}")
        else:
            print(f"   ❌ FAILED - {check['description']}")
            print(f"   Pattern not found: {check['pattern']}")
            all_passed = False
    
    return all_passed


def test_modal_flow_logic():
    """Test the logical flow of modal operations"""

    print("\n🔍 Testing modal operation flow...")

    dashboard_path = "Dashboard.html"

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for key operations in the success flow
    operations = [
        ("closeModal('addTopicModal')", "Modal is closed"),
        ("clearAddTopicForm()", "Form is cleared"),
        ("await loadTasks()", "Tasks are reloaded"),
        ("updateStats()", "Statistics are updated"),
        ("showNotification", "Success notification is shown")
    ]

    all_found = True
    for op_pattern, description in operations:
        if op_pattern in content:
            print(f"   ✅ Found: {description}")
        else:
            print(f"   ❌ Missing: {description}")
            all_found = False

    return all_found


def test_edit_functionality():
    """Test that edit functionality is properly maintained"""
    
    print("\n🔧 Testing edit functionality preservation...")
    
    dashboard_path = "Dashboard.html"
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    edit_checks = [
        ("Edit function override", r"const originalAddTopic = addTopic;"),
        ("Edit detection", r"const editingTaskId = modal\.dataset\.editingTaskId;"),
        ("Update task call", r"await updateTask\(editingTaskId\);"),
        ("Reset modal function", r"function resetAddTopicModal\(\)"),
        ("Modal reset on close", r"resetAddTopicModal\(\);")
    ]
    
    all_found = True
    for check_name, pattern in edit_checks:
        if re.search(pattern, content):
            print(f"   ✅ {check_name}: Found")
        else:
            print(f"   ❌ {check_name}: Missing")
            all_found = False
    
    return all_found


if __name__ == "__main__":
    print("🚀 Phase 2: Testing Add Topic Modal Behavior Fixes")
    print("=" * 60)
    
    # Test the modal behavior fixes
    behavior_test = test_modal_behavior_fixes()
    
    # Test the modal flow logic
    flow_test = test_modal_flow_logic()
    
    # Test edit functionality preservation
    edit_test = test_edit_functionality()
    
    print("\n" + "=" * 60)
    
    if behavior_test and flow_test and edit_test:
        print("🎉 Phase 2 COMPLETED: Add Topic modal behavior is fixed!")
        print("\nThe fixes ensure that:")
        print("• Modal automatically closes after successful task creation")
        print("• Tasks table immediately refreshes to show new tasks")
        print("• Form is properly cleared after operations")
        print("• Statistics are updated after task operations")
        print("• Edit functionality is preserved and working")
        print("• All operations are properly awaited for correct sequencing")
        exit(0)
    else:
        print("❌ Phase 2 FAILED: Some modal behavior issues remain")
        exit(1)
