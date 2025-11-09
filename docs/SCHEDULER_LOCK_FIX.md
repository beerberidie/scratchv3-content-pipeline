# Scheduler Lock Fix

## Problem Identified
The scheduler was throwing the error:
```
ERROR:app.services.scheduler:Error releasing lock task-22491a53-4a27-4ac5-928c-add36f5f73c0: Cannot release an unlocked lock
```

## Root Cause
The issue was in the `redis_lock` context manager in `app/services/scheduler.py`. When a Redis lock could not be acquired (because another instance was already processing the task), the code would:

1. Do a `return` without yielding (line 100)
2. The `finally` block would still execute
3. Try to release a lock that was never actually acquired
4. Cause the "Cannot release an unlocked lock" error

## Solution Implemented

### 1. Fixed Context Manager Logic
Updated the `redis_lock` context manager to:
- Always yield a value (True/False) to indicate lock acquisition status
- Only attempt to release locks that were actually acquired
- Track acquisition status with a variable

### 2. Updated Task Execution
Modified `_execute_scheduled_task` to:
- Check the lock acquisition status
- Skip task execution if lock couldn't be acquired (prevents duplicate processing)
- Log appropriate messages for different scenarios

### 3. Key Changes Made

**Before (problematic):**
```python
if not acquired:
    logger.warning(f"Could not acquire lock {lock_key}, task may already be running")
    return  # ← This caused the issue

# In finally block:
if lock:
    await lock.release()  # ← Tried to release unlocked lock
```

**After (fixed):**
```python
if not acquired:
    logger.warning(f"Could not acquire lock {lock_key}, task may already be running")
    yield False  # ← Properly yield to make context manager work
    return

# In finally block:
if lock and acquired:  # ← Only release if actually acquired
    await lock.release()
```

## Test Results

✅ **Lock acquisition failure**: Handled gracefully, no error thrown
✅ **Successful lock acquisition**: Works as expected, lock properly released  
✅ **Redis unavailable**: Falls back gracefully without locking
✅ **No more "Cannot release an unlocked lock" errors**

## Files Modified
- `app/services/scheduler.py` - Fixed Redis lock context manager
- `tests/test_scheduler_failure.py` - Updated test expectations

The scheduler lock error should now be completely resolved! 🎉
