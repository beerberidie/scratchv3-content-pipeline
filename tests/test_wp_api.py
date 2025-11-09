"""
Tests for WordPress Settings API endpoints
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.wp import get_decrypted_wp_auth
from app.api.keys import encrypt_key, decrypt_key


class TestWordPressAPI:
    """Test WordPress settings management functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = TestClient(app)
        self.test_user = {"email": "test@example.com", "username": "testuser"}
        
        # Mock authentication
        self.auth_patcher = patch('app.dependencies.get_current_active_user')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = self.test_user
        
        # Mock storage service
        self.storage_patcher = patch('app.api.wp.storage_service')
        self.mock_storage = self.storage_patcher.start()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.auth_patcher.stop()
        self.storage_patcher.stop()
    
    def test_get_wp_sites_empty(self):
        """Test getting WordPress sites when none exist"""
        self.mock_storage.get_wp_sites.return_value = []
        
        response = self.client.get("/api/wp/sites")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_wp_sites_with_data(self):
        """Test getting WordPress sites when they exist"""
        mock_sites = [
            {
                "id": "site-1",
                "url": "https://example.com",
                "created_at": "2023-01-01T00:00:00"
            },
            {
                "id": "site-2", 
                "url": "https://blog.example.com",
                "created_at": "2023-01-02T00:00:00"
            }
        ]
        self.mock_storage.get_wp_sites.return_value = mock_sites
        
        response = self.client.get("/api/wp/sites")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["url"] == "https://example.com"
        assert data[1]["url"] == "https://blog.example.com"
    
    def test_add_wp_site_success(self):
        """Test successfully adding a WordPress site"""
        self.mock_storage.get_wp_sites.return_value = []  # No existing sites
        self.mock_storage.add_wp_site.return_value = True
        
        response = self.client.post("/api/wp/sites", json={
            "url": "https://newsite.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://newsite.com"
        assert "id" in data
        assert "created_at" in data
        
        # Verify storage was called
        self.mock_storage.add_wp_site.assert_called_once()
    
    def test_add_wp_site_duplicate(self):
        """Test adding a WordPress site that already exists"""
        existing_sites = [
            {"id": "site-1", "url": "https://example.com", "created_at": "2023-01-01T00:00:00"}
        ]
        self.mock_storage.get_wp_sites.return_value = existing_sites
        
        response = self.client.post("/api/wp/sites", json={
            "url": "https://example.com"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"]
    
    def test_add_wp_site_invalid_url(self):
        """Test adding an invalid WordPress site URL"""
        response = self.client.post("/api/wp/sites", json={
            "url": "not-a-valid-url"
        })
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_delete_wp_site_success(self):
        """Test successfully deleting a WordPress site"""
        existing_sites = [
            {"id": "site-1", "url": "https://example.com", "created_at": "2023-01-01T00:00:00"}
        ]
        self.mock_storage.get_wp_sites.return_value = existing_sites
        self.mock_storage.delete_wp_site.return_value = True
        
        response = self.client.delete("/api/wp/sites/site-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "deleted successfully" in data["message"]
        
        # Verify storage was called
        self.mock_storage.delete_wp_site.assert_called_once_with("test@example.com", "site-1")
    
    def test_delete_wp_site_not_found(self):
        """Test deleting a WordPress site that doesn't exist"""
        self.mock_storage.get_wp_sites.return_value = []
        
        response = self.client.delete("/api/wp/sites/nonexistent-site")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_get_wp_auth_status_not_configured(self):
        """Test getting WordPress auth status when not configured"""
        self.mock_storage.get_wp_auth.return_value = None
        
        response = self.client.get("/api/wp/auth")
        
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] == False
        assert data["username"] is None
    
    def test_get_wp_auth_status_configured(self):
        """Test getting WordPress auth status when configured"""
        mock_auth = {
            "username_encrypted": encrypt_key("testuser"),
            "password_encrypted": encrypt_key("testpass"),
            "created_at": "2023-01-01T00:00:00"
        }
        self.mock_storage.get_wp_auth.return_value = mock_auth
        
        response = self.client.get("/api/wp/auth")
        
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] == True
        assert data["username"] == "testuser"
    
    def test_save_wp_auth_success(self):
        """Test successfully saving WordPress authentication"""
        self.mock_storage.save_wp_auth.return_value = True
        
        response = self.client.post("/api/wp/auth", json={
            "username": "wpuser",
            "password": "wppassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "saved successfully" in data["message"]
        assert data["status"]["configured"] == True
        assert data["status"]["username"] == "wpuser"
        
        # Verify storage was called
        self.mock_storage.save_wp_auth.assert_called_once()
    
    def test_save_wp_auth_missing_username(self):
        """Test saving WordPress auth with missing username"""
        response = self.client.post("/api/wp/auth", json={
            "username": "",
            "password": "wppassword123"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Both username and password are required" in data["detail"]
    
    def test_save_wp_auth_short_password(self):
        """Test saving WordPress auth with too short password"""
        response = self.client.post("/api/wp/auth", json={
            "username": "wpuser",
            "password": "short"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "at least 6 characters" in data["detail"]
    
    def test_delete_wp_auth_success(self):
        """Test successfully deleting WordPress authentication"""
        self.mock_storage.delete_wp_auth.return_value = True
        
        response = self.client.delete("/api/wp/auth")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "deleted successfully" in data["message"]
        assert data["status"]["configured"] == False
        
        # Verify storage was called
        self.mock_storage.delete_wp_auth.assert_called_once_with("test@example.com")


class TestWordPressAuthEncryption:
    """Test WordPress authentication encryption functionality"""
    
    def test_get_decrypted_wp_auth_success(self):
        """Test getting decrypted WordPress auth when configured"""
        mock_auth = {
            "username_encrypted": encrypt_key("testuser"),
            "password_encrypted": encrypt_key("testpass")
        }
        
        with patch('app.api.wp.storage_service') as mock_storage:
            mock_storage.get_wp_auth.return_value = mock_auth
            
            result = get_decrypted_wp_auth("test@example.com")
            
            assert result is not None
            assert result["username"] == "testuser"
            assert result["password"] == "testpass"
    
    def test_get_decrypted_wp_auth_not_configured(self):
        """Test getting decrypted WordPress auth when not configured"""
        with patch('app.api.wp.storage_service') as mock_storage:
            mock_storage.get_wp_auth.return_value = None
            
            result = get_decrypted_wp_auth("test@example.com")
            
            assert result is None
    
    def test_get_decrypted_wp_auth_partial_data(self):
        """Test getting decrypted WordPress auth with incomplete data"""
        mock_auth = {
            "username_encrypted": encrypt_key("testuser"),
            # Missing password_encrypted
        }
        
        with patch('app.api.wp.storage_service') as mock_storage:
            mock_storage.get_wp_auth.return_value = mock_auth
            
            result = get_decrypted_wp_auth("test@example.com")
            
            assert result is None


class TestWordPressAPIIntegration:
    """Integration tests for the complete WordPress settings flow"""
    
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
    
    def test_complete_wp_sites_lifecycle(self):
        """Test the complete lifecycle of WordPress sites management"""
        # 1. Check initial sites (should be empty)
        response = self.client.get("/api/wp/sites")
        assert response.status_code == 200
        initial_sites = response.json()
        
        # 2. Add a site
        add_response = self.client.post("/api/wp/sites", json={
            "url": "https://integration-test.com"
        })
        assert add_response.status_code == 200
        site_data = add_response.json()
        site_id = site_data["id"]
        
        # 3. Check sites again (should show new site)
        sites_response = self.client.get("/api/wp/sites")
        assert sites_response.status_code == 200
        updated_sites = sites_response.json()
        assert len(updated_sites) >= 1
        assert any(site["url"] == "https://integration-test.com" for site in updated_sites)
        
        # 4. Delete the site
        delete_response = self.client.delete(f"/api/wp/sites/{site_id}")
        assert delete_response.status_code == 200
        
        # 5. Check final sites (should not contain deleted site)
        final_response = self.client.get("/api/wp/sites")
        assert final_response.status_code == 200
        final_sites = final_response.json()
        assert not any(site["url"] == "https://integration-test.com" for site in final_sites)
    
    def test_complete_wp_auth_lifecycle(self):
        """Test the complete lifecycle of WordPress authentication"""
        # 1. Check initial auth status (should be not configured)
        response = self.client.get("/api/wp/auth")
        assert response.status_code == 200
        initial_status = response.json()
        
        # 2. Save auth credentials
        save_response = self.client.post("/api/wp/auth", json={
            "username": "integration_user",
            "password": "integration_password_123"
        })
        assert save_response.status_code == 200
        
        # 3. Check auth status again (should be configured)
        status_response = self.client.get("/api/wp/auth")
        assert status_response.status_code == 200
        updated_status = status_response.json()
        assert updated_status["configured"] == True
        assert updated_status["username"] == "integration_user"
        
        # 4. Delete auth credentials
        delete_response = self.client.delete("/api/wp/auth")
        assert delete_response.status_code == 200
        
        # 5. Check final auth status (should be not configured again)
        final_response = self.client.get("/api/wp/auth")
        assert final_response.status_code == 200
        final_status = final_response.json()
        assert final_status["configured"] == False
