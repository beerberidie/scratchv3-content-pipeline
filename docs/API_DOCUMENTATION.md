# 📚 ScratchV3 API Documentation

Complete API reference for the Scratch Automation App with examples and response formats.

## 🔐 Authentication

All API endpoints (except login) require authentication via session cookies.

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin"
  }
}
```

### Logout
```http
POST /api/auth/logout
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

## 📋 Task Management

### Get All Tasks
```http
GET /api/tasks/
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "task_123",
      "topic": "AI in Healthcare",
      "rules": "casual tone, include statistics",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "scheduled_time": "2024-01-15T11:00:00Z",
      "completed_at": "2024-01-15T11:05:00Z",
      "wordpress_site": "https://myblog.com",
      "chat_refs": ["conversation1.txt", "research_notes.txt"]
    }
  ]
}
```

### Schedule New Task
```http
POST /api/tasks/schedule
Content-Type: application/json

{
  "topic": "Future of Remote Work",
  "rules": "professional tone, 800-1000 words, include examples",
  "scheduled_time": "2024-01-16T14:00:00Z",
  "wordpress_site": "https://myblog.com",
  "chat_refs": ["remote_work_discussion.txt"]
}
```

**Response:**
```json
{
  "message": "Task scheduled successfully",
  "task_id": "task_124",
  "scheduled_time": "2024-01-16T14:00:00Z"
}
```

### Get Task Details
```http
GET /api/tasks/{task_id}
```

**Response:**
```json
{
  "id": "task_123",
  "topic": "AI in Healthcare",
  "rules": "casual tone, include statistics",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "scheduled_time": "2024-01-15T11:00:00Z",
  "completed_at": "2024-01-15T11:05:00Z",
  "wordpress_site": "https://myblog.com",
  "chat_refs": ["conversation1.txt"],
  "generated_content": {
    "title": "How AI is Revolutionizing Healthcare",
    "content": "Article content here...",
    "word_count": 850
  }
}
```

### Delete Task
```http
DELETE /api/tasks/{task_id}
```

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

## 🤖 Content Generation

### Generate Content Immediately
```http
POST /api/content/generate
Content-Type: application/json

{
  "topic": "Benefits of Meditation",
  "rules": "beginner-friendly, include practical tips",
  "chat_refs": ["meditation_research.txt"]
}
```

**Response:**
```json
{
  "title": "The Life-Changing Benefits of Daily Meditation",
  "content": "Meditation has become increasingly popular...",
  "word_count": 750,
  "generated_at": "2024-01-15T12:00:00Z"
}
```

### Get Content History
```http
GET /api/content/history?page=1&limit=10
```

**Response:**
```json
{
  "history": [
    {
      "id": "content_456",
      "title": "The Life-Changing Benefits of Daily Meditation",
      "topic": "Benefits of Meditation",
      "generated_at": "2024-01-15T12:00:00Z",
      "word_count": 750,
      "status": "published"
    }
  ],
  "total": 25,
  "page": 1,
  "pages": 3
}
```

## 🔑 API Key Management

### Get API Key Status
```http
GET /api/keys/status
```

**Response:**
```json
{
  "openai": {
    "configured": true,
    "valid": true,
    "last_checked": "2024-01-15T10:00:00Z"
  },
  "openrouter": {
    "configured": false,
    "valid": false,
    "last_checked": null
  },
  "pexels": {
    "configured": true,
    "valid": true,
    "last_checked": "2024-01-15T10:00:00Z"
  }
}
```

### Save/Update API Key
```http
POST /api/keys
Content-Type: application/json

{
  "provider": "openai",
  "key": "sk-your-api-key-here"
}
```

**Response:**
```json
{
  "message": "API key saved successfully",
  "provider": "openai",
  "status": {
    "configured": true,
    "valid": true
  }
}
```

## 🌐 WordPress Integration

### Get WordPress Sites
```http
GET /api/wp/sites
```

**Response:**
```json
{
  "sites": [
    {
      "id": 1,
      "url": "https://myblog.com",
      "name": "My Personal Blog",
      "added_at": "2024-01-10T09:00:00Z"
    },
    {
      "id": 2,
      "url": "https://company.com",
      "name": "Company Blog",
      "added_at": "2024-01-12T14:30:00Z"
    }
  ]
}
```

### Add WordPress Site
```http
POST /api/wp/sites
Content-Type: application/json

{
  "url": "https://newblog.com",
  "name": "New Blog Site"
}
```

**Response:**
```json
{
  "message": "WordPress site added successfully",
  "site": {
    "id": 3,
    "url": "https://newblog.com",
    "name": "New Blog Site",
    "added_at": "2024-01-15T15:00:00Z"
  }
}
```

### Remove WordPress Site
```http
DELETE /api/wp/sites/{site_id}
```

**Response:**
```json
{
  "message": "WordPress site removed successfully"
}
```

### Get WordPress Credentials
```http
GET /api/wp/auth
```

**Response:**
```json
{
  "username": "wp_user",
  "password_set": true,
  "last_updated": "2024-01-10T09:00:00Z"
}
```

### Save WordPress Credentials
```http
POST /api/wp/auth
Content-Type: application/json

{
  "username": "wp_username",
  "password": "wp_password"
}
```

**Response:**
```json
{
  "message": "WordPress credentials saved successfully",
  "username": "wp_username"
}
```

## 📊 System Health

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "scheduler": "running"
  }
}
```

## ❌ Error Responses

All endpoints return consistent error formats:

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "topic": ["This field is required"],
    "scheduled_time": ["Invalid datetime format"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Please log in to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "Task with ID 'task_999' not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "request_id": "req_123456"
}
```

## 📝 Request/Response Notes

### Date Formats
- All timestamps use ISO 8601 format: `2024-01-15T12:00:00Z`
- Timezone is always UTC

### Pagination
- Default page size: 10 items
- Maximum page size: 100 items
- Use `page` and `limit` query parameters

### Content Length Limits
- Topic: 200 characters max
- Rules: 1000 characters max
- Generated content: No limit

### File Upload Limits
- Chat reference files: 10MB max per file
- Supported formats: .txt, .md

### Rate Limiting
- 100 requests per minute per user
- 1000 requests per hour per user
- Burst limit: 20 requests per 10 seconds
