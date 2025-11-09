#!/usr/bin/env python3
"""
Data Migration Script for ScratchV3 Task Data
Fixes wordpress_post_id integer values to strings for Pydantic compatibility
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

def migrate_task_file(file_path: Path) -> bool:
    """
    Migrate a single task file to fix wordpress_post_id integer values
    Returns True if changes were made, False otherwise
    """
    try:
        # Read the current file
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        if not isinstance(tasks, list):
            print(f"Warning: {file_path} does not contain a list of tasks")
            return False
        
        changes_made = False
        
        # Fix each task
        for task in tasks:
            if isinstance(task, dict) and "wordpress_post_id" in task:
                if task["wordpress_post_id"] is not None and isinstance(task["wordpress_post_id"], int):
                    old_value = task["wordpress_post_id"]
                    task["wordpress_post_id"] = str(old_value)
                    print(f"  Fixed wordpress_post_id: {old_value} -> '{task['wordpress_post_id']}'")
                    changes_made = True
        
        # Save back if changes were made
        if changes_made:
            # Create backup first
            backup_path = file_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            print(f"  Created backup: {backup_path}")
            
            # Save the fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            print(f"  Updated: {file_path}")
        
        return changes_made
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def migrate_all_task_files():
    """
    Migrate all task files in the data/tasks directory
    """
    data_dir = Path("data")
    tasks_dir = data_dir / "tasks"
    
    if not tasks_dir.exists():
        print(f"Tasks directory not found: {tasks_dir}")
        return
    
    print("🔧 Starting task data migration...")
    print(f"📁 Scanning directory: {tasks_dir}")
    
    total_files = 0
    migrated_files = 0
    
    # Process all JSON files in the tasks directory
    for file_path in tasks_dir.glob("*.json"):
        total_files += 1
        print(f"\n📄 Processing: {file_path.name}")
        
        if migrate_task_file(file_path):
            migrated_files += 1
            print(f"✅ Migrated: {file_path.name}")
        else:
            print(f"ℹ️  No changes needed: {file_path.name}")
    
    print(f"\n🎯 Migration Summary:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files migrated: {migrated_files}")
    print(f"   Files unchanged: {total_files - migrated_files}")
    
    if migrated_files > 0:
        print(f"\n✅ Migration completed successfully!")
        print(f"💾 Backup files created with .backup extension")
    else:
        print(f"\nℹ️  No migration needed - all files are already compatible")

if __name__ == "__main__":
    migrate_all_task_files()
