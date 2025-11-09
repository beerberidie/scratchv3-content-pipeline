"""
Tests for chat reference usage functionality
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from app.services.content_generator import ContentGenerationEngine


class TestChatReferenceUsage:
    """Test that markers from multiple chats appear in generated content"""
    
    def setup_method(self):
        """Setup test environment"""
        self.content_engine = ContentGenerationEngine()
        
    def test_load_multiple_chats(self):
        """Test loading content from multiple chat files"""
        # Create temporary chat files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test chat files
            chat1_content = """
User: I need help with AI content strategy.
Assistant: Here are key considerations for AI content strategy:
1. Define clear objectives
2. Maintain brand voice consistency
3. Ensure quality control processes
"""
            
            chat2_content = """
User: What about WordPress integration?
Assistant: For WordPress integration, consider:
- Use REST API for automated posting
- Implement proper authentication
- Set up draft workflows for review
"""
            
            chat1_path = os.path.join(temp_dir, "chat1.txt")
            chat2_path = os.path.join(temp_dir, "chat2.txt")
            
            with open(chat1_path, 'w', encoding='utf-8') as f:
                f.write(chat1_content)
            
            with open(chat2_path, 'w', encoding='utf-8') as f:
                f.write(chat2_content)
            
            # Test loading chats
            result = self.content_engine.load_chats("test_user", ["chat1.txt", "chat2.txt"])
            
            # Verify both chat contents are included
            assert "AI content strategy" in result
            assert "WordPress integration" in result
            assert "--- From chat1.txt ---" in result
            assert "--- From chat2.txt ---" in result
    
    def test_chat_summarization(self):
        """Test chat content summarization"""
        long_chat_content = """
User: I have a very long conversation about content marketing strategies.
Assistant: Content marketing is a strategic approach focused on creating and distributing valuable, relevant, and consistent content to attract and retain a clearly defined audience.

The key principles include:
1. Understanding your target audience deeply
2. Creating content that provides genuine value
3. Maintaining consistency in publishing
4. Measuring and analyzing performance
5. Adapting based on data insights

Content marketing differs from traditional advertising in that it focuses on providing value rather than directly promoting products or services. This approach builds trust and establishes authority in your industry.

When developing a content marketing strategy, consider these elements:
- Content pillars that align with your brand
- Distribution channels that reach your audience
- Content formats that resonate with your users
- Metrics that matter for your business goals
- Resources and budget allocation

The most successful content marketing campaigns are those that consistently deliver value to their audience while subtly guiding them through the customer journey.
""" * 5  # Make it very long
        
        summary = self.content_engine.summarise_chat(long_chat_content, "long_chat.txt")
        
        # Verify summarization works
        assert len(summary) < len(long_chat_content)
        assert "content marketing" in summary.lower()
        assert "strategic approach" in summary.lower()
    
    def test_token_safe_concatenation(self):
        """Test that chat loading respects token limits"""
        # Create multiple large chat files
        large_content = "This is a very long chat content. " * 200  # ~1200 chars
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create 5 large chat files
            chat_files = []
            for i in range(5):
                filename = f"large_chat_{i}.txt"
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Chat {i}: {large_content}")
                chat_files.append(filename)
            
            # Mock the user chat directory
            with patch('os.path.join') as mock_join:
                mock_join.side_effect = lambda *args: os.path.join(temp_dir, args[-1])
                
                result = self.content_engine.load_chats("test_user", chat_files)
                
                # Should not exceed reasonable length (token-safe)
                # Rough estimate: 4000 tokens * 4 chars = 16000 chars max
                assert len(result) < 20000
                
                # Should include some content from multiple chats
                assert "Chat 0:" in result or "Chat 1:" in result
    
    def test_empty_chat_handling(self):
        """Test handling of empty or missing chat files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty chat file
            empty_chat = os.path.join(temp_dir, "empty.txt")
            with open(empty_chat, 'w', encoding='utf-8') as f:
                f.write("")
            
            # Mock the user chat directory
            with patch('os.path.join') as mock_join:
                mock_join.side_effect = lambda *args: os.path.join(temp_dir, args[-1])
                
                result = self.content_engine.load_chats("test_user", ["empty.txt", "nonexistent.txt"])
                
                # Should handle gracefully
                assert isinstance(result, str)
                assert "empty.txt" in result or len(result) == 0
    
    def test_chat_markers_preservation(self):
        """Test that chat file markers are preserved in output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            chat_content = "Important discussion about AI ethics and responsible development."
            
            chat_file = os.path.join(temp_dir, "ethics_chat.txt")
            with open(chat_file, 'w', encoding='utf-8') as f:
                f.write(chat_content)
            
            with patch('os.path.join') as mock_join:
                mock_join.side_effect = lambda *args: os.path.join(temp_dir, args[-1])
                
                result = self.content_engine.load_chats("test_user", ["ethics_chat.txt"])
                
                # Verify file marker is present
                assert "--- From ethics_chat.txt ---" in result
                assert "AI ethics" in result
    
    @pytest.mark.asyncio
    async def test_integration_with_content_generation(self):
        """Test that chat references integrate properly with content generation"""
        # Mock the AI service response
        mock_ai_response = {
            "success": True,
            "content": "Generated content about AI strategy based on chat references.",
            "model_used": "test-model",
            "provider": "test",
            "tokens_used": 100
        }
        
        # Mock task with chat references
        task = {
            "id": "test-task",
            "user_id": "test-user",
            "topic": "AI Content Strategy",
            "rules": "professional tone, UK English",
            "referenced_chats": ["strategy_chat.txt"],
            "content_type": "blog"
        }
        
        user_settings = {
            "ai_provider": "openrouter",
            "openrouter_model": "test-model"
        }
        
        with patch.object(self.content_engine, 'load_chats') as mock_load_chats:
            mock_load_chats.return_value = "Chat context about AI strategy"
            
            with patch('app.services.ai.ai_service.generate_content_with_messages') as mock_ai:
                mock_ai.return_value = mock_ai_response
                
                result = await self.content_engine._generate_content(task, user_settings)
                
                # Verify chat loading was called
                mock_load_chats.assert_called_once_with("test-user", ["strategy_chat.txt"])
                
                # Verify AI was called with chat context
                mock_ai.assert_called_once()
                call_args = mock_ai.call_args[1]
                messages = call_args['messages']
                
                # Check that chat context is included in the prompt
                user_message = next((msg for msg in messages if msg['role'] == 'user'), None)
                assert user_message is not None
                assert "Chat context about AI strategy" in user_message['content']
