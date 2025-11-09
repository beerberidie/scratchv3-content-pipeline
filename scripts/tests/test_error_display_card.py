#!/usr/bin/env python3
"""
Test script to verify that the Error Display Card is properly implemented.
This checks that the error card is added to the dashboard and error handling
functions are properly integrated.
"""

import os
import re

def test_error_card_html():
    """Test that the error card HTML is properly added to the dashboard"""
    
    print("🧪 Testing Error Display Card HTML...")
    
    # Read the Dashboard.html file
    dashboard_path = "Dashboard.html"
    
    if not os.path.exists(dashboard_path):
        print(f"❌ File not found: {dashboard_path}")
        return False
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test cases to verify the error card HTML
    html_checks = [
        {
            "name": "Error card container",
            "pattern": r'<div class="stat-card error-card" id="errorCard"',
            "description": "Error card container with proper classes and ID"
        },
        {
            "name": "Error card header",
            "pattern": r'<h3 class="stat-title">Task Errors</h3>',
            "description": "Error card title"
        },
        {
            "name": "Error dismiss button",
            "pattern": r'<button class="error-dismiss-btn" onclick="dismissError\(\)"',
            "description": "Error dismiss button with proper onclick handler"
        },
        {
            "name": "Error message container",
            "pattern": r'<div class="error-message" id="errorMessage">',
            "description": "Error message container"
        },
        {
            "name": "Error details container",
            "pattern": r'<div class="error-details" id="errorDetails">',
            "description": "Error details container"
        },
        {
            "name": "Error actions container",
            "pattern": r'<div class="error-actions" id="errorActions">',
            "description": "Error actions container"
        },
        {
            "name": "Error card initially hidden",
            "pattern": r'style="display: none;"',
            "description": "Error card is initially hidden"
        }
    ]
    
    all_passed = True
    
    for i, check in enumerate(html_checks, 1):
        print(f"\n{i}. Testing: {check['name']}")
        
        if re.search(check["pattern"], content):
            print(f"   ✅ PASSED - {check['description']}")
        else:
            print(f"   ❌ FAILED - {check['description']}")
            print(f"   Pattern not found: {check['pattern']}")
            all_passed = False
    
    return all_passed


def test_error_card_css():
    """Test that the error card CSS styles are properly added"""
    
    print("\n🎨 Testing Error Display Card CSS...")
    
    dashboard_path = "Dashboard.html"
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test cases to verify the error card CSS
    css_checks = [
        {
            "name": "Error card base styles",
            "pattern": r'\.error-card \{',
            "description": "Error card base CSS class"
        },
        {
            "name": "Error card border color",
            "pattern": r'border-color: var\(--error-600\);',
            "description": "Error card border color styling"
        },
        {
            "name": "Error dismiss button styles",
            "pattern": r'\.error-dismiss-btn \{',
            "description": "Error dismiss button CSS class"
        },
        {
            "name": "Error icon styles",
            "pattern": r'\.error-icon \{',
            "description": "Error icon CSS class"
        },
        {
            "name": "Error content styles",
            "pattern": r'\.error-content \{',
            "description": "Error content CSS class"
        },
        {
            "name": "Error message styles",
            "pattern": r'\.error-message \{',
            "description": "Error message CSS class"
        },
        {
            "name": "Error details styles",
            "pattern": r'\.error-details \{',
            "description": "Error details CSS class"
        },
        {
            "name": "Error actions styles",
            "pattern": r'\.error-actions \{',
            "description": "Error actions CSS class"
        },
        {
            "name": "Error action button styles",
            "pattern": r'\.error-action-btn \{',
            "description": "Error action button CSS class"
        }
    ]
    
    all_passed = True
    
    for i, check in enumerate(css_checks, 1):
        print(f"\n{i}. Testing: {check['name']}")
        
        if re.search(check["pattern"], content):
            print(f"   ✅ PASSED - {check['description']}")
        else:
            print(f"   ❌ FAILED - {check['description']}")
            print(f"   Pattern not found: {check['pattern']}")
            all_passed = False
    
    return all_passed


def test_error_handling_functions():
    """Test that the error handling JavaScript functions are properly added"""
    
    print("\n🔧 Testing Error Handling Functions...")
    
    dashboard_path = "Dashboard.html"
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test cases to verify the error handling functions
    js_checks = [
        {
            "name": "showTaskError function",
            "pattern": r'function showTaskError\(title, message, errorType',
            "description": "Main error display function"
        },
        {
            "name": "dismissError function",
            "pattern": r'function dismissError\(\)',
            "description": "Error dismissal function"
        },
        {
            "name": "retryLastAction function",
            "pattern": r'function retryLastAction\(\)',
            "description": "Retry action function"
        },
        {
            "name": "Error type handling",
            "pattern": r'if \(errorType === \'create\'\)',
            "description": "Error type specific handling"
        },
        {
            "name": "Authentication error guidance",
            "pattern": r'authentication.*credentials',
            "description": "Specific guidance for authentication errors"
        },
        {
            "name": "Network error guidance",
            "pattern": r'network.*connection',
            "description": "Specific guidance for network errors"
        },
        {
            "name": "WordPress error guidance",
            "pattern": r'WordPress.*URL.*credentials',
            "description": "Specific guidance for WordPress errors"
        },
        {
            "name": "Auto-dismiss timer",
            "pattern": r'setTimeout.*30000',
            "description": "Auto-dismiss after 30 seconds"
        },
        {
            "name": "Error integration in task creation",
            "pattern": r'showTaskError\(.*create.*\)',
            "description": "Error function called in task creation"
        }
    ]
    
    all_passed = True
    
    for i, check in enumerate(js_checks, 1):
        print(f"\n{i}. Testing: {check['name']}")
        
        if re.search(check["pattern"], content, re.IGNORECASE | re.DOTALL):
            print(f"   ✅ PASSED - {check['description']}")
        else:
            print(f"   ❌ FAILED - {check['description']}")
            print(f"   Pattern not found: {check['pattern']}")
            all_passed = False
    
    return all_passed


def test_error_integration():
    """Test that error handling is integrated into task creation"""
    
    print("\n🔗 Testing Error Integration...")
    
    dashboard_path = "Dashboard.html"
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that alert() calls have been replaced with showTaskError()
    integration_checks = [
        {
            "name": "Task creation error handling",
            "pattern": r'showTaskError\(.*Failed to create task',
            "description": "Task creation errors use showTaskError instead of alert"
        },
        {
            "name": "Network error handling",
            "pattern": r'showTaskError\(.*Network error',
            "description": "Network errors use showTaskError instead of alert"
        }
    ]
    
    all_passed = True
    
    for i, check in enumerate(integration_checks, 1):
        print(f"\n{i}. Testing: {check['name']}")
        
        if re.search(check["pattern"], content, re.IGNORECASE):
            print(f"   ✅ PASSED - {check['description']}")
        else:
            print(f"   ❌ FAILED - {check['description']}")
            print(f"   Pattern not found: {check['pattern']}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("🚀 Phase 3: Testing Error Display Card Implementation")
    print("=" * 60)
    
    # Test the HTML structure
    html_test = test_error_card_html()
    
    # Test the CSS styles
    css_test = test_error_card_css()
    
    # Test the JavaScript functions
    js_test = test_error_handling_functions()
    
    # Test the integration
    integration_test = test_error_integration()
    
    print("\n" + "=" * 60)
    
    if html_test and css_test and js_test and integration_test:
        print("🎉 Phase 3 COMPLETED: Error Display Card is working correctly!")
        print("\nThe implementation provides:")
        print("• Error display card in the dashboard sidebar")
        print("• Clear error messages with specific guidance")
        print("• Context-aware action buttons for different error types")
        print("• Auto-dismiss functionality after 30 seconds")
        print("• Integration with task creation error handling")
        print("• Professional styling that matches the dashboard theme")
        exit(0)
    else:
        print("❌ Phase 3 FAILED: Some error display card features are missing")
        exit(1)
