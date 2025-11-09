"""
JSON-based storage service for tasks and data
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.config import settings
from app.models.base import Task, TaskStatus


class StorageService:
    """JSON-based storage service"""
    
    def __init__(self):
        self.tasks_dir = os.path.join(settings.data_dir, "tasks")
        self.history_dir = os.path.join(settings.data_dir, "history")
        os.makedirs(self.tasks_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
    
    def _get_user_tasks_file(self, user_id: str) -> str:
        """Get the tasks file path for a user"""
        return os.path.join(self.tasks_dir, f"{user_id}.json")
    
    def _load_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Load tasks for a user"""
        tasks_file = self._get_user_tasks_file(user_id)
        if not os.path.exists(tasks_file):
            return []
        
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_user_tasks(self, user_id: str, tasks: List[Dict[str, Any]]):
        """Save tasks for a user"""
        tasks_file = self._get_user_tasks_file(user_id)
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, default=str)
    
    def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        tasks = self._load_user_tasks(user_id)
        
        # Generate task ID and add metadata
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        task = {
            "id": task_id,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            "status": TaskStatus.PENDING.value,
            **task_data
        }
        
        tasks.append(task)
        self._save_user_tasks(user_id, tasks)
        
        return task
    
    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user"""
        tasks = self._load_user_tasks(user_id)

        # Fix any integer wordpress_post_id values to strings for Pydantic compatibility
        needs_save = False
        for task in tasks:
            if "wordpress_post_id" in task and task["wordpress_post_id"] is not None:
                if isinstance(task["wordpress_post_id"], int):
                    task["wordpress_post_id"] = str(task["wordpress_post_id"])
                    needs_save = True

        # Save back if we made any changes
        if needs_save:
            self._save_user_tasks(user_id, tasks)

        return tasks
    
    def get_task(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        tasks = self._load_user_tasks(user_id)
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def update_task(self, user_id: str, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task"""
        tasks = self._load_user_tasks(user_id)
        
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                task.update(updates)
                task["updated_at"] = datetime.now(timezone.utc).isoformat()
                tasks[i] = task
                self._save_user_tasks(user_id, tasks)
                return task
        
        return None
    
    def delete_task(self, user_id: str, task_id: str) -> bool:
        """Delete a task"""
        tasks = self._load_user_tasks(user_id)
        
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                tasks.pop(i)
                self._save_user_tasks(user_id, tasks)
                return True
        
        return False
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks across all users"""
        pending_tasks = []
        
        for filename in os.listdir(self.tasks_dir):
            if filename.endswith('.json'):
                user_id = filename[:-5]  # Remove .json extension
                tasks = self._load_user_tasks(user_id)
                
                for task in tasks:
                    if task.get("status") == TaskStatus.PENDING.value:
                        pending_tasks.append(task)
        
        return pending_tasks
    
    def save_generated_content(self, user_id: str, task_id: str, content_data: Dict[str, Any]) -> str:
        """Save generated content to history"""
        history_file = os.path.join(self.history_dir, f"{user_id}.json")
        
        # Load existing history
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                history = []
        
        # Add new content
        content_id = str(uuid.uuid4())
        content_entry = {
            "id": content_id,
            "task_id": task_id,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **content_data
        }
        
        history.append(content_entry)
        
        # Save history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, default=str)
        
        return content_id
    
    def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get content generation history for a user"""
        history_file = os.path.join(self.history_dir, f"{user_id}.json")
        
        if not os.path.exists(history_file):
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_history_item(self, user_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific history item"""
        history = self.get_user_history(user_id)
        for item in history:
            if item["id"] == item_id:
                return item
        return None
    
    def delete_history_item(self, user_id: str, item_id: str) -> bool:
        """Delete a history item"""
        history_file = os.path.join(self.history_dir, f"{user_id}.json")
        history = self.get_user_history(user_id)
        
        for i, item in enumerate(history):
            if item["id"] == item_id:
                history.pop(i)
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, default=str)
                return True
        
        return False

    def get_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            user_keys_dir = os.path.join(settings.data_dir, "user_keys")
            user_keys_file = os.path.join(user_keys_dir, f"{user_id}.json")
            if os.path.exists(user_keys_file):
                with open(user_keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            return []

    def get_user_key(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """Get a specific API key for a user and provider"""
        user_keys = self.get_user_keys(user_id)
        for key_data in user_keys:
            if key_data.get("provider") == provider:
                return key_data
        return None

    def upsert_user_key(self, user_id: str, provider: str, encrypted_key: str):
        """Add or update an API key for a user"""
        try:
            user_keys = self.get_user_keys(user_id)

            # Find existing key for this provider
            existing_index = None
            for i, key_data in enumerate(user_keys):
                if key_data.get("provider") == provider:
                    existing_index = i
                    break

            # Create new key data
            key_data = {
                "provider": provider,
                "key_encrypted": encrypted_key,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            # Update or append
            if existing_index is not None:
                key_data["created_at"] = user_keys[existing_index].get("created_at", key_data["created_at"])
                user_keys[existing_index] = key_data
            else:
                user_keys.append(key_data)

            # Save to file
            user_keys_dir = os.path.join(settings.data_dir, "user_keys")
            os.makedirs(user_keys_dir, exist_ok=True)

            user_keys_file = os.path.join(user_keys_dir, f"{user_id}.json")
            with open(user_keys_file, 'w', encoding='utf-8') as f:
                json.dump(user_keys, f, indent=2)

            return True
        except Exception as e:
            return False

    def delete_user_key(self, user_id: str, provider: str):
        """Delete an API key for a user and provider"""
        try:
            user_keys = self.get_user_keys(user_id)

            # Filter out the key for this provider
            user_keys = [key_data for key_data in user_keys if key_data.get("provider") != provider]

            # Save updated list
            user_keys_dir = os.path.join(settings.data_dir, "user_keys")
            os.makedirs(user_keys_dir, exist_ok=True)

            user_keys_file = os.path.join(user_keys_dir, f"{user_id}.json")
            with open(user_keys_file, 'w', encoding='utf-8') as f:
                json.dump(user_keys, f, indent=2)

            return True
        except Exception as e:
            return False

    # === WORDPRESS SITES MANAGEMENT ===

    def get_wp_sites(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all WordPress sites for a user"""
        try:
            wp_sites_dir = os.path.join(settings.data_dir, "wp_sites")
            wp_sites_file = os.path.join(wp_sites_dir, f"{user_id}.json")
            if os.path.exists(wp_sites_file):
                with open(wp_sites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            return []

    def add_wp_site(self, user_id: str, site_data: Dict[str, Any]):
        """Add a WordPress site for a user"""
        try:
            sites = self.get_wp_sites(user_id)
            sites.append(site_data)

            wp_sites_dir = os.path.join(settings.data_dir, "wp_sites")
            os.makedirs(wp_sites_dir, exist_ok=True)

            wp_sites_file = os.path.join(wp_sites_dir, f"{user_id}.json")
            with open(wp_sites_file, 'w', encoding='utf-8') as f:
                json.dump(sites, f, indent=2)

            return True
        except Exception as e:
            return False

    def delete_wp_site(self, user_id: str, site_id: str):
        """Delete a WordPress site for a user"""
        try:
            sites = self.get_wp_sites(user_id)
            sites = [site for site in sites if site.get("id") != site_id]

            wp_sites_dir = os.path.join(settings.data_dir, "wp_sites")
            os.makedirs(wp_sites_dir, exist_ok=True)

            wp_sites_file = os.path.join(wp_sites_dir, f"{user_id}.json")
            with open(wp_sites_file, 'w', encoding='utf-8') as f:
                json.dump(sites, f, indent=2)

            return True
        except Exception as e:
            return False

    # === WORDPRESS AUTHENTICATION ===

    def get_wp_auth(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get WordPress authentication data for a user"""
        try:
            wp_auth_dir = os.path.join(settings.data_dir, "wp_auth")
            wp_auth_file = os.path.join(wp_auth_dir, f"{user_id}.json")
            if os.path.exists(wp_auth_file):
                with open(wp_auth_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            return None

    def save_wp_auth(self, user_id: str, auth_data: Dict[str, Any]):
        """Save WordPress authentication data for a user"""
        try:
            wp_auth_dir = os.path.join(settings.data_dir, "wp_auth")
            os.makedirs(wp_auth_dir, exist_ok=True)

            wp_auth_file = os.path.join(wp_auth_dir, f"{user_id}.json")
            with open(wp_auth_file, 'w', encoding='utf-8') as f:
                json.dump(auth_data, f, indent=2)

            return True
        except Exception as e:
            return False

    def delete_wp_auth(self, user_id: str):
        """Delete WordPress authentication data for a user"""
        try:
            wp_auth_dir = os.path.join(settings.data_dir, "wp_auth")
            wp_auth_file = os.path.join(wp_auth_dir, f"{user_id}.json")
            if os.path.exists(wp_auth_file):
                os.remove(wp_auth_file)
            return True
        except Exception as e:
            return False


# Global storage service instance
storage_service = StorageService()
