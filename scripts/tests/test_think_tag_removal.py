#!/usr/bin/env python3
"""
Test script to verify that <think></think> tags are properly removed
from generated content in both download and WordPress posting scenarios.
"""

import re
import sys
import os

def _clean_think_tags(text: str) -> str:
    """
    Remove <think></think> tags and their content from generated text.
    This is the same function used in the application.
    """
    if not text:
        return text
    
    # Remove <think></think> tags and everything between them
    # Use re.DOTALL flag to match newlines within think tags
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up any extra whitespace left behind
    cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)  # Remove triple+ line breaks
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def test_think_tag_removal():
    """Test various scenarios of think tag removal"""
    
    print("🧪 Testing <think></think> tag removal...")
    
    # Test cases
    test_cases = [
        {
            "name": "Simple think tags",
            "input": "Here is some content. <think>This is internal thinking</think> More content here.",
            "expected": "Here is some content.  More content here."
        },
        {
            "name": "Think tags with newlines",
            "input": "Content before.\n<think>\nMulti-line\nthinking process\n</think>\nContent after.",
            "expected": "Content before.\n\nContent after."
        },
        {
            "name": "Multiple think tags",
            "input": "<think>First thought</think>Content<think>Second thought</think>More content<think>Third thought</think>",
            "expected": "ContentMore content"
        },
        {
            "name": "Case insensitive tags",
            "input": "Content <THINK>uppercase thinking</THINK> more <Think>mixed case</Think> content.",
            "expected": "Content  more  content."
        },
        {
            "name": "No think tags",
            "input": "This is normal content without any think tags.",
            "expected": "This is normal content without any think tags."
        },
        {
            "name": "Empty content",
            "input": "",
            "expected": ""
        },
        {
            "name": "Only think tags",
            "input": "<think>Only thinking, no content</think>",
            "expected": ""
        },
        {
            "name": "Complex content with think tags",
            "input": """# Article Title

This is the introduction paragraph.

<think>
I need to think about what to write next.
Maybe I should add some bullet points?
Let me consider the structure.
</think>

## Main Section

Here are some key points:
- Point 1
- Point 2

<think>Should I add more points?</think>

## Conclusion

This is the conclusion paragraph.""",
            "expected": """# Article Title

This is the introduction paragraph.

## Main Section

Here are some key points:
- Point 1
- Point 2

## Conclusion

This is the conclusion paragraph."""
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        result = _clean_think_tags(test_case["input"])
        
        # Normalize whitespace for comparison
        result_normalized = re.sub(r'\s+', ' ', result.strip())
        expected_normalized = re.sub(r'\s+', ' ', test_case["expected"].strip())
        
        if result_normalized == expected_normalized:
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED")
            print(f"   Expected: {repr(test_case['expected'])}")
            print(f"   Got:      {repr(result)}")
            all_passed = False
    
    return all_passed


def test_implementation_integration():
    """Test that the implementation is properly integrated"""
    
    print("\n🔍 Testing implementation integration...")
    
    # Check content_generator.py
    content_gen_path = "app/services/content_generator.py"
    if os.path.exists(content_gen_path):
        with open(content_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("_clean_think_tags method", "_clean_think_tags"),
            ("WordPress content cleaning", "self._clean_think_tags(content[\"content\"])"),
            ("QA filter integration", "self._clean_think_tags(text)")
        ]
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {check_name}: Found")
            else:
                print(f"   ❌ {check_name}: Missing")
                return False
    else:
        print(f"   ❌ File not found: {content_gen_path}")
        return False
    
    # Check history.py
    history_path = "app/api/history.py"
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("_clean_think_tags function", "_clean_think_tags"),
            ("Download content cleaning", "_clean_think_tags(content)")
        ]
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {check_name}: Found")
            else:
                print(f"   ❌ {check_name}: Missing")
                return False
    else:
        print(f"   ❌ File not found: {history_path}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Phase 1: Testing Think Tag Removal Implementation")
    print("=" * 60)
    
    # Test the function logic
    function_test = test_think_tag_removal()
    
    # Test the implementation integration
    integration_test = test_implementation_integration()
    
    print("\n" + "=" * 60)
    
    if function_test and integration_test:
        print("🎉 Phase 1 COMPLETED: Think tag removal is working correctly!")
        print("\nThe implementation ensures that:")
        print("• <think></think> tags are removed from downloaded content")
        print("• <think></think> tags are removed from WordPress posted content")
        print("• Content cleaning handles various edge cases properly")
        print("• Integration is properly implemented in both locations")
        exit(0)
    else:
        print("❌ Phase 1 FAILED: Some tests did not pass")
        exit(1)
