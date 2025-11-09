"""
Tests for API Keys management endpoints
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.keys import encrypt_key, decrypt_key, get_encryption_key
from app.services.storage import storage_service


class TestKeysAPI:
    """Test API Keys management functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = TestClient(app)
        self.test_user = {"email": "test@example.com", "username": "testuser"}
        
        # Mock authentication
        self.auth_patcher = patch('app.dependencies.get_current_active_user')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = self.test_user
        
        # Mock storage service
        self.storage_patcher = patch('app.api.keys.storage_service')
        self.mock_storage = self.storage_patcher.start()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.auth_patcher.stop()
        self.storage_patcher.stop()
    
    def test_get_keys_status_empty(self):
        """Test getting keys status when no keys are configured"""
        self.mock_storage.get_user_keys.return_value = []
        
        response = self.client.get("/api/keys/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["openai"] == False
        assert data["openrouter"] == False
        assert data["pexels"] == False
    
    def test_get_keys_status_with_keys(self):
        """Test getting keys status when keys are configured"""
        self.mock_storage.get_user_keys.return_value = [
            {"provider": "openai", "key_encrypted": "encrypted_key_1"},
            {"provider": "pexels", "key_encrypted": "encrypted_key_2"}
        ]
        
        response = self.client.get("/api/keys/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["openai"] == True
        assert data["openrouter"] == False
        assert data["pexels"] == True
    
    def test_save_api_key_success(self):
        """Test successfully saving an API key"""
        self.mock_storage.upsert_user_key.return_value = True
        self.mock_storage.get_user_keys.return_value = [
            {"provider": "openai", "key_encrypted": "encrypted_key"}
        ]
        
        response = self.client.post("/api/keys/", json={
            "provider": "openai",
            "key": "sk-test-key-12345678901234567890"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "OpenAI API key saved successfully" in data["message"]
        assert "status" in data
    
    def test_save_api_key_invalid_provider(self):
        """Test saving API key with invalid provider"""
        response = self.client.post("/api/keys/", json={
            "provider": "invalid_provider",
            "key": "sk-test-key-12345678901234567890"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid provider" in data["detail"]
    
    def test_save_api_key_too_short(self):
        """Test saving API key that's too short"""
        response = self.client.post("/api/keys/", json={
            "provider": "openai",
            "key": "short"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "at least 10 characters" in data["detail"]
    
    def test_delete_api_key_success(self):
        """Test successfully deleting an API key"""
        self.mock_storage.delete_user_key.return_value = True
        self.mock_storage.get_user_keys.return_value = []
        
        response = self.client.delete("/api/keys/openai")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "OpenAI API key deleted successfully" in data["message"]
    
    def test_delete_api_key_invalid_provider(self):
        """Test deleting API key with invalid provider"""
        response = self.client.delete("/api/keys/invalid_provider")
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid provider" in data["detail"]
    
    def test_get_api_key_masked(self):
        """Test getting a masked API key"""
        self.mock_storage.get_user_key.return_value = {
            "key_encrypted": encrypt_key("sk-test-key-12345678901234567890"),
            "created_at": "2023-01-01T00:00:00"
        }
        
        response = self.client.get("/api/keys/openai")
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "openai"
        assert data["has_key"] == True
        assert "sk-t****7890" in data["key_masked"]  # Properly masked
    
    def test_get_api_key_not_found(self):
        """Test getting API key that doesn't exist"""
        self.mock_storage.get_user_key.return_value = None
        
        response = self.client.get("/api/keys/openai")
        
        assert response.status_code == 404
        data = response.json()
        assert "No API key found" in data["detail"]


class TestKeyEncryption:
    """Test key encryption and decryption functionality"""
    
    def test_encrypt_decrypt_key(self):
        """Test that encryption and decryption work correctly"""
        original_key = "sk-test-key-12345678901234567890"
        
        # Encrypt the key
        encrypted = encrypt_key(original_key)
        assert encrypted != original_key
        assert len(encrypted) > len(original_key)
        
        # Decrypt the key
        decrypted = decrypt_key(encrypted)
        assert decrypted == original_key
    
    def test_encryption_key_generation(self):
        """Test that encryption key is generated consistently"""
        key1 = get_encryption_key()
        key2 = get_encryption_key()
        
        # Should be the same key (from environment or generated)
        assert key1 == key2
        assert len(key1) > 0
    
    def test_different_keys_encrypt_differently(self):
        """Test that different keys encrypt to different values"""
        key1 = "sk-test-key-1"
        key2 = "sk-test-key-2"
        
        encrypted1 = encrypt_key(key1)
        encrypted2 = encrypt_key(key2)
        
        assert encrypted1 != encrypted2
        assert decrypt_key(encrypted1) == key1
        assert decrypt_key(encrypted2) == key2


class TestKeyAPIIntegration:
    """Integration tests for the complete key management flow"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = TestClient(app)
        self.test_user = {"email": "integration_test@example.com", "username": "testuser"}
        
        # Mock authentication
        self.auth_patcher = patch('app.dependencies.get_current_active_user')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = self.test_user
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.auth_patcher.stop()
    
    def test_complete_key_lifecycle(self):
        """Test the complete lifecycle of key management"""
        # 1. Check initial status (should be empty)
        response = self.client.get("/api/keys/status")
        assert response.status_code == 200
        initial_status = response.json()
        
        # 2. Save a key
        save_response = self.client.post("/api/keys/", json={
            "provider": "openai",
            "key": "sk-test-integration-key-123456789"
        })
        assert save_response.status_code == 200
        
        # 3. Check status again (should show key exists)
        status_response = self.client.get("/api/keys/status")
        assert status_response.status_code == 200
        updated_status = status_response.json()
        assert updated_status["openai"] == True
        
        # 4. Get the masked key
        get_response = self.client.get("/api/keys/openai")
        assert get_response.status_code == 200
        key_data = get_response.json()
        assert key_data["has_key"] == True
        assert "sk-t****" in key_data["key_masked"]
        
        # 5. Delete the key
        delete_response = self.client.delete("/api/keys/openai")
        assert delete_response.status_code == 200
        
        # 6. Check final status (should be empty again)
        final_response = self.client.get("/api/keys/status")
        assert final_response.status_code == 200
        final_status = final_response.json()
        assert final_status["openai"] == False
