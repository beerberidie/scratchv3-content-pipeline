# WordPress Posting Fix

## Problem Identified
Tasks were executing successfully and generating content, but WordPress posting was failing silently. The tasks showed:
- `"wordpress_posted": false`
- `"wordpress_post_id": null`
- `"wordpress_edit_link": null`

## Root Cause
The application has **two different systems** for storing WordPress credentials:

1. **New encrypted system**: Stores credentials in `data/wp_auth/{email}.json` with encrypted values
2. **Legacy system**: Stores credentials in `user_settings` as plain text

The content generator was only looking for credentials in the legacy `user_settings` system:
```python
username = user_settings.get("wordpress_app_username")
password = user_settings.get("wordpress_app_password")
```

But the credentials were actually stored in the new encrypted system, so they weren't found, causing WordPress posting to be skipped with the error "WordPress credentials not configured".

## Solution Implemented

### 1. Updated Credential Retrieval
Modified `_post_to_wordpress()` method in `app/services/content_generator.py` to:
- Use the existing `get_decrypted_wp_auth()` helper function
- Check the new encrypted system first
- Fall back to legacy system if needed
- Properly handle user email lookup for credential retrieval

### 2. Enhanced Logging
Added logging to track:
- Which credential system is being used
- WordPress posting attempts and results
- Better error tracking

### 3. Key Changes Made

**Before (broken):**
```python
# Only checked legacy user_settings
username = user_settings.get("wordpress_app_username")
password = user_settings.get("wordpress_app_password")
```

**After (fixed):**
```python
# Check new encrypted system first, then fall back to legacy
from app.api.wp import get_decrypted_wp_auth

user_data = auth_service.get_user(task["user_id"])
user_email = user_data.get("email") if user_data else task["user_id"]

wp_credentials = get_decrypted_wp_auth(user_email)

if wp_credentials:
    username = wp_credentials["username"]
    password = wp_credentials["password"]
else:
    # Fallback to legacy system
    username = user_settings.get("wordpress_app_username")
    password = user_settings.get("wordpress_app_password")
```

## Test Results
The fix ensures that:
✅ WordPress credentials are properly retrieved from the encrypted storage
✅ Tasks with WordPress URLs will attempt to post to WordPress
✅ Proper error handling and logging for debugging
✅ Backward compatibility with legacy credential storage

## Files Modified
- `app/services/content_generator.py` - Fixed credential retrieval logic

The WordPress posting should now work correctly for scheduled tasks! 🎉
