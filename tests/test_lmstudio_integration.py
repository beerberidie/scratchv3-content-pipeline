"""
Test LM Studio integration for the AI service
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai import AIService
from app.config import settings


class TestLMStudioIntegration:
    """Test LM Studio integration"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance"""
        return AIService()
    
    def test_lmstudio_client_initialization(self, ai_service):
        """Test that LM Studio client is initialized when URL is configured"""
        with patch.object(settings, 'lmstudio_api_url', 'http://localhost:1234/v1'):
            ai_service._initialize_clients()
            assert ai_service.lmstudio_client is not None
    
    def test_get_client_and_model_lmstudio(self, ai_service):
        """Test getting LM Studio client and model"""
        user_settings = {"lmstudio_api_url": "http://localhost:1234/v1"}
        
        client, model = ai_service._get_client_and_model("lmstudio", "local-model", user_settings)
        
        assert client is not None
        assert model == "local-model"
    
    def test_get_client_and_model_lmstudio_no_url(self, ai_service):
        """Test error when LM Studio URL is not configured"""
        user_settings = {}
        
        with patch.object(settings, 'lmstudio_api_url', None):
            with pytest.raises(ValueError, match="LM Studio API URL not configured"):
                ai_service._get_client_and_model("lmstudio", "local-model", user_settings)
    
    @pytest.mark.asyncio
    async def test_get_available_models_lmstudio(self, ai_service):
        """Test getting available models for LM Studio"""
        models = await ai_service.get_available_models("lmstudio")
        
        assert len(models) > 0
        assert any(model["id"] == "local-model" for model in models)
        assert any(model["id"] == "llama-3-8b" for model in models)
        assert any(model["id"] == "mistral-7b" for model in models)
        assert any(model["id"] == "phi-2" for model in models)
    
    @pytest.mark.asyncio
    async def test_test_api_key_lmstudio_success(self, ai_service):
        """Test successful LM Studio API key validation"""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Hello"
        
        with patch('app.services.ai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await ai_service.test_api_key("lmstudio", "http://localhost:1234/v1")
            
            assert result["valid"] is True
            assert "LM Studio connection is valid" in result["message"]
    
    @pytest.mark.asyncio
    async def test_test_api_key_lmstudio_failure(self, ai_service):
        """Test failed LM Studio API key validation"""
        with patch('app.services.ai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.side_effect = Exception("Connection failed")
            mock_openai.return_value = mock_client
            
            result = await ai_service.test_api_key("lmstudio", "http://localhost:1234/v1")
            
            assert result["valid"] is False
            assert "Connection failed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_generate_content_lmstudio(self, ai_service):
        """Test content generation with LM Studio"""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Generated content"
        mock_response.usage = AsyncMock()
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        
        user_settings = {"lmstudio_api_url": "http://localhost:1234/v1"}
        
        with patch('app.services.ai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = await ai_service.generate_content(
                prompt="Test prompt",
                provider="lmstudio",
                model="local-model",
                user_settings=user_settings
            )
            
            assert result["success"] is True
            assert result["content"] == "Generated content"
            assert result["provider"] == "lmstudio"
            assert result["model_used"] == "local-model"
            assert result["tokens_used"] == 100
