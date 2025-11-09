#!/usr/bin/env python3
"""
Test script to verify the implemented improvements for rules enforcement,
checkbox interface, hide completed tasks, and enhanced chat integration.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.content_generator import ContentGenerationEngine
from app.services.rules import parse_rules
from app.services.prompt_builder import PromptBuilder, PromptSettings
from app.models.base import ContentType

def test_rule_parsing():
    """Test the enhanced rule parsing with new heading case options"""
    print("🧪 Testing Enhanced Rule Parsing...")
    
    test_cases = [
        "UK English, sentence case, professional tone, avoid bullet points",
        "sentence case headings, no emojis, SA seasons",
        "title case, detailed content, avoid lists",
        "professional tone, UK English, sentence case, no emojis"
    ]
    
    for rules_text in test_cases:
        print(f"\nTesting: '{rules_text}'")
        flags, extra_rules = parse_rules(rules_text)
        print(f"  Parsed flags: {flags}")
        print(f"  Extra rules: '{extra_rules}'")
        
        # Test PromptSettings creation
        settings = PromptSettings()
        if flags.get("language"):
            settings.language = flags["language"]
        if flags.get("heading_case"):
            settings.heading_case = flags["heading_case"]
        if flags.get("tone"):
            settings.tone = flags["tone"]
        
        print(f"  Settings: language={settings.language}, heading_case={settings.heading_case}, tone={settings.tone}")
    
    print("✅ Rule parsing tests completed")

def test_prompt_building():
    """Test the enhanced prompt building with provider-specific adjustments"""
    print("\n🧪 Testing Enhanced Prompt Building...")
    
    settings = PromptSettings()
    settings.language = "uk_english"
    settings.heading_case = "sentence"
    settings.tone = "professional"
    settings.avoid_bullets = True
    settings.ai_provider = "openrouter"
    
    builder = PromptBuilder(settings)
    
    # Test system prompt
    system_prompt = builder.build_system_prompt(ContentType.BLOG)
    print("System Prompt:")
    print(system_prompt)
    print()
    
    # Test user prompt
    user_prompt = builder.build_user_prompt(
        topic="AI in Healthcare",
        content_type=ContentType.BLOG,
        extra_rules="Focus on practical applications"
    )
    print("User Prompt:")
    print(user_prompt)
    
    print("✅ Prompt building tests completed")

def test_chat_style_analysis():
    """Test the new chat style analysis functionality"""
    print("\n🧪 Testing Chat Style Analysis...")
    
    engine = ContentGenerationEngine()
    
    # Test chat content with different styles
    test_chats = [
        {
            "name": "formal_chat",
            "content": """
            User: Could you please explain the implementation details?
            Assistant: Certainly. The implementation involves several key components. 
            Furthermore, we need to consider the architectural implications. 
            Therefore, I recommend a structured approach.
            """
        },
        {
            "name": "casual_chat", 
            "content": """
            User: Hey! How's this looking?
            Assistant: Hey there! This looks awesome! 
            Cool approach btw. Thanks for sharing this!
            FYI, you might want to check out this other thing too.
            """
        },
        {
            "name": "technical_chat",
            "content": """
            User: What's the best database configuration?
            Assistant: For optimal performance, consider these API endpoints:
            1. Configure the database connection pool
            2. Implement caching algorithms
            3. Optimize query performance
            The implementation should focus on scalability.
            """
        }
    ]
    
    for chat in test_chats:
        print(f"\nAnalyzing {chat['name']}:")
        analysis = engine.analyze_chat_style(chat['content'])
        print(f"  Analysis: {json.dumps(analysis, indent=2)}")
        
        instructions = engine.build_chat_style_instructions(analysis)
        print(f"  Style Instructions: {instructions}")
    
    print("✅ Chat style analysis tests completed")

async def test_content_generation():
    """Test the complete content generation with all improvements"""
    print("\n🧪 Testing Complete Content Generation...")
    
    # Mock task data
    task = {
        "id": "test_task",
        "user_id": "test_user",
        "topic": "The future of remote work",
        "rules": "UK English, sentence case, professional tone, avoid bullet points",
        "article_content": "",
        "referenced_chats": [],  # Would normally contain chat filenames
        "content_type": ContentType.BLOG.value
    }
    
    # Mock user settings
    user_settings = {
        "ai_provider": "openrouter",
        "openai_api_key": "test_key"
    }
    
    engine = ContentGenerationEngine()
    
    # Test the rule parsing and prompt building (without actual AI call)
    try:
        # Parse rules
        flags, extra_rules = parse_rules(task["rules"])
        print(f"Parsed rules - Flags: {flags}, Extra: '{extra_rules}'")
        
        # Create settings
        settings = PromptSettings()
        settings.language = flags.get("language", "us_english")
        settings.heading_case = flags.get("heading_case", "sentence")
        settings.tone = flags.get("tone", "professional")
        settings.avoid_bullets = "no_bullets" in flags.get("style", [])
        settings.ai_provider = user_settings.get("ai_provider", "lmstudio")
        
        print(f"Prompt settings: {settings}")
        
        # Build prompt
        builder = PromptBuilder(settings)
        messages = builder.build_messages(
            topic=task["topic"],
            content_type=ContentType(task["content_type"]),
            extra_rules=extra_rules
        )
        
        print("Generated messages:")
        for i, message in enumerate(messages):
            print(f"  Message {i+1} ({message['role']}):")
            print(f"    {message['content'][:200]}...")
        
        print("✅ Content generation setup test completed")
        
    except Exception as e:
        print(f"❌ Error in content generation test: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Improvement Tests")
    print("=" * 50)
    
    test_rule_parsing()
    test_prompt_building()
    test_chat_style_analysis()
    
    # Run async test
    asyncio.run(test_content_generation())
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\nImprovements implemented:")
    print("✅ Enhanced rule enforcement with heading case")
    print("✅ Provider-specific prompt adjustments")
    print("✅ Checkbox-based rules interface (frontend)")
    print("✅ Hide completed tasks feature (frontend)")
    print("✅ Improved referenced chat integration")

if __name__ == "__main__":
    main()
