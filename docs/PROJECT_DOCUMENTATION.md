# ScratchV3 - AI-Powered Content Generation Platform

## Project Overview

**ScratchV3** is a comprehensive AI-powered content generation and automation platform designed for creating blogs, articles, news, and social media posts. The application provides automated content creation with WordPress integration, image sourcing, and task scheduling capabilities.

### Core Purpose
- **Content Generation**: AI-powered creation of various content types (blogs, articles, news, social posts)
- **Automation**: Scheduled content generation and delivery
- **WordPress Integration**: Direct posting to WordPress sites as drafts
- **Image Integration**: Automatic image sourcing from Pexels API
- **Task Management**: Comprehensive task scheduling and execution system

## Technology Stack & Architecture

### Backend Framework
- **FastAPI**: Modern, high-performance Python web framework
- **Python 3.8+**: Core programming language
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### AI & External Services
- **OpenAI API**: GPT models for content generation
- **OpenRouter API**: Alternative AI provider with multiple model access
- **Pexels API**: High-quality stock image sourcing
- **WordPress REST API**: Direct integration for content publishing

### Data & Storage
- **JSON-based Storage**: File-based data persistence
- **Redis**: Background task queue and caching
- **APScheduler**: Advanced task scheduling system
- **Celery**: Distributed task processing

### Frontend & UI
- **HTML5/CSS3**: Modern web interface
- **Vanilla JavaScript**: Client-side functionality
- **CSS Custom Properties**: Design system with theming
- **Responsive Design**: Mobile-first approach

## Project Structure

```
ScratchV3/
├── app/                          # Main application package
│   ├── api/                      # API endpoint modules
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── content.py           # Content generation endpoints
│   │   ├── tasks.py             # Task management endpoints
│   │   ├── wordpress.py         # WordPress integration endpoints
│   │   ├── images.py            # Image search endpoints
│   │   ├── email.py             # Email delivery endpoints
│   │   ├── settings.py          # User settings endpoints
│   │   ├── history.py           # Content history endpoints
│   │   └── scheduler.py         # Task scheduling endpoints
│   ├── models/                   # Data models and schemas
│   │   └── base.py              # Core Pydantic models
│   ├── services/                 # Business logic layer
│   │   ├── ai.py                # AI service integration
│   │   ├── content_generator.py # Content generation engine
│   │   ├── wordpress.py         # WordPress service
│   │   ├── images.py            # Image search service
│   │   ├── email.py             # Email delivery service
│   │   ├── auth.py              # Authentication service
│   │   ├── storage.py           # Data storage service
│   │   └── scheduler.py         # Task scheduling service
│   ├── middleware/               # Custom middleware
│   │   ├── rate_limit.py        # Rate limiting middleware
│   │   └── error_handler.py     # Global error handling
│   ├── config.py                # Application configuration
│   ├── dependencies.py          # FastAPI dependencies
│   └── main.py                  # FastAPI application entry point
├── static/                       # Static web assets
│   ├── css/                     # Stylesheets
│   │   └── dashboard.css        # Main dashboard styles
│   └── js/                      # JavaScript files
│       └── utils.js             # Utility functions
├── data/                         # JSON data storage
│   ├── users/                   # User data files
│   ├── tasks/                   # Task data files
│   ├── history/                 # Content history files
│   └── chats/                   # Chat file storage
├── uploads/                      # File upload directory
├── Dashboard.html               # Main dashboard interface
├── login.html                   # Login page
├── requirements.txt             # Python dependencies
├── run.py                       # Application launcher
└── test_*.py                    # Test suite files
```

## Key Components & Features

### 1. Content Generation Engine (`app/services/content_generator.py`)
**Purpose**: Orchestrates AI content generation with image integration and WordPress publishing

**Key Features**:
- Multi-provider AI integration (OpenAI, OpenRouter)
- Content type specialization (blog, article, news, social media)
- Automatic image sourcing and attribution
- WordPress draft posting
- Comprehensive error handling and logging

**Core Methods**:
- `process_task()`: Main task processing pipeline
- `_generate_content()`: AI content generation
- `_get_images()`: Image search and selection
- `_post_to_wordpress()`: WordPress publishing

### 2. WordPress Integration (`app/services/wordpress.py`)
**Purpose**: Complete WordPress REST API integration for content publishing

**Key Features**:
- WordPress site connection testing
- Draft post creation with metadata
- URL preset management
- Authentication via WordPress App Passwords
- Site information retrieval

**API Endpoints**:
- `POST /api/wordpress/test-connection`: Test WordPress credentials
- `POST /api/wordpress/create-draft`: Create draft posts
- `GET/POST/DELETE /api/wordpress/url-presets`: Manage URL presets

### 3. Task Scheduling System (`app/services/scheduler.py`)
**Purpose**: Advanced task scheduling and background processing

**Key Features**:
- APScheduler integration for precise timing
- Automatic task rescheduling
- Batch task execution
- Real-time status monitoring
- Error recovery and retry logic

### 4. AI Service Integration (`app/services/ai.py`)
**Purpose**: Unified interface for multiple AI providers

**Supported Providers**:
- **OpenAI**: GPT-3.5, GPT-4 models
- **OpenRouter**: Access to multiple AI models (Claude, Llama, etc.)

**Features**:
- Provider-agnostic content generation
- Token usage tracking
- Model selection per user
- Error handling and fallback logic

### 5. Data Models (`app/models/base.py`)
**Core Models**:
- `User`: User account and settings management
- `Task`: Content generation task definition
- `GeneratedContent`: Generated content with metadata
- `UserSettings`: User preferences and API configurations

**Enums**:
- `TaskStatus`: PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED
- `AIProvider`: OPENAI, OPENROUTER
- `ContentType`: BLOG, ARTICLE, NEWS, SOCIAL_POST, RESHARE

### 6. Authentication System (`app/services/auth.py`)
**Features**:
- Static user list authentication
- JWT token-based sessions
- User settings management
- Session persistence

## API Endpoints Overview

### Authentication (`/api/auth`)
- `POST /login`: User authentication with JWT tokens
- `GET /me`: Get current user information
- `POST /logout`: Session termination

### Task Management (`/api/tasks`)
- `GET /`: List user tasks with filtering
- `POST /`: Create new content generation task
- `GET /{task_id}`: Get specific task details
- `PUT /{task_id}`: Update task configuration
- `DELETE /{task_id}`: Delete task
- `POST /{task_id}/execute`: Manual task execution
- `POST /execute-all`: Batch execute all pending tasks

### Content Generation (`/api/content`)
- `POST /generate`: Direct content generation
- `GET /types`: Available content types
- `POST /preview`: Preview content before generation

### WordPress Integration (`/api/wordpress`)
- `POST /test-connection`: Test WordPress site connectivity
- `POST /create-draft`: Create draft post
- `GET /url-presets`: Get saved WordPress URLs
- `POST /url-presets`: Add WordPress URL preset
- `DELETE /url-presets/{url}`: Remove URL preset
- `GET /site-info`: Get WordPress site information

### Image Management (`/api/images`)
- `GET /search`: Search Pexels for images
- `GET /featured`: Get featured/trending images
- `GET /{image_id}`: Get specific image details

### Content History (`/api/history`)
- `GET /`: List generated content history
- `GET /{content_id}`: Get specific content
- `GET /{content_id}/download`: Download content as file
- `POST /{content_id}/share`: Generate shareable link
- `DELETE /{content_id}`: Delete content

### User Settings (`/api/settings`)
- `GET /`: Get user settings
- `PUT /`: Update user settings
- `POST /api-keys`: Update API keys
- `GET /chat-files`: List uploaded chat files
- `POST /chat-files`: Upload chat file
- `DELETE /chat-files/{filename}`: Delete chat file

### Task Scheduling (`/api/scheduler`)
- `GET /status`: Get scheduler status
- `GET /jobs`: List scheduled jobs
- `GET /pending-tasks`: Get pending tasks
- `POST /reschedule`: Reschedule all pending tasks
- `POST /start`: Start scheduler
- `POST /stop`: Stop scheduler

## Dependencies & Setup

### Core Dependencies (`requirements.txt`)
```python
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI Integration
openai==1.3.7
httpx==0.25.2

# Task Processing
celery==5.3.4
redis==5.0.1
apscheduler==3.10.4

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Configuration
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# File Handling
aiofiles==23.2.1
pillow==10.1.0

# Email (Legacy - being replaced by WordPress)
aiosmtplib==3.0.1
email-validator==2.1.0
jinja2==3.1.2

# Development & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
```

### Environment Configuration
**Required Environment Variables**:
```bash
# AI API Keys
OPENAI_API_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key
PEXELS_API_KEY=your_pexels_key

# Application Security
SECRET_KEY=your_secret_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
MAX_REQUESTS_PER_HOUR=200
MAX_REQUESTS_PER_DAY=2000

# AI Provider Defaults
DEFAULT_AI_PROVIDER=openrouter
DEFAULT_OPENAI_MODEL=gpt-4
DEFAULT_OPENROUTER_MODEL=openrouter/auto
```

### Installation & Setup
1. **Prerequisites**: Python 3.8+, Redis server
2. **Virtual Environment**: `python -m venv venv && source venv/bin/activate`
3. **Dependencies**: `pip install -r requirements.txt`
4. **Configuration**: Copy `.env.example` to `.env` and configure
5. **Launch**: `python run.py` or `uvicorn app.main:app --reload`

## Code Patterns & Conventions

### Architecture Patterns
- **Service Layer Pattern**: Business logic separated into service modules
- **Repository Pattern**: Data access abstracted through storage service
- **Dependency Injection**: FastAPI's dependency system for clean separation
- **Middleware Pattern**: Cross-cutting concerns handled via middleware

### File Naming Conventions
- **Snake Case**: All Python files use snake_case naming
- **Descriptive Names**: Files named after their primary responsibility
- **Module Organization**: Related functionality grouped in packages

### Error Handling Approach
- **Global Error Handler**: Centralized error handling middleware
- **Structured Responses**: Consistent error response format
- **Logging**: Comprehensive logging for debugging and monitoring
- **Graceful Degradation**: Fallback mechanisms for external service failures

### Import/Export Patterns
- **Absolute Imports**: All imports use absolute paths from app root
- **Service Instances**: Global service instances for dependency injection
- **Model Exports**: Centralized model exports from `__init__.py` files

## Integration Points

### WordPress Integration
**Authentication**: WordPress Application Passwords
**API Endpoints**: WordPress REST API v2
**Content Flow**: Generated content → WordPress draft posts
**URL Management**: User-configurable WordPress site presets
**Features**: Connection testing, site info retrieval, draft creation

### AI Service Integration
**Providers**: OpenAI (GPT models), OpenRouter (multi-model access)
**Content Types**: Specialized prompts for blogs, articles, news, social media
**Token Management**: Usage tracking and cost monitoring
**Model Selection**: User-configurable model preferences

### Image Service Integration
**Provider**: Pexels API for high-quality stock photos
**Search**: Keyword-based image discovery
**Attribution**: Automatic photographer attribution
**Integration**: Images embedded in generated content

### Data Storage Integration
**Pattern**: JSON file-based storage system
**Structure**: User-segregated data organization
**Backup**: File-based backup and recovery
**Performance**: In-memory caching with Redis

## Recent Changes & Context

### WordPress Integration Enhancement
- **Replacement Strategy**: WordPress integration replacing email functionality
- **User Preferences**: URL presets and credential management
- **Draft Publishing**: Content posted as drafts for review
- **Authentication**: WordPress App Password integration

### Modern UI/UX Implementation
- **Design System**: CSS custom properties for consistent theming
- **Professional Styling**: Clean, modern interface without emojis
- **Responsive Design**: Mobile-first responsive layout
- **Accessibility**: Proper contrast ratios and readable typography

### Testing Infrastructure
- **Integration Tests**: Comprehensive API endpoint testing
- **Content Engine Tests**: End-to-end content generation testing
- **Scheduler Tests**: Task scheduling and execution validation
- **Authentication Tests**: User authentication flow testing

## Development Guidelines

### Code Quality Standards
- **Type Hints**: All functions use Python type hints
- **Docstrings**: Comprehensive documentation for all modules
- **Error Handling**: Explicit error handling with meaningful messages
- **Testing**: Test coverage for critical functionality

### Security Considerations
- **API Key Management**: Environment-based configuration
- **Authentication**: JWT-based session management
- **Rate Limiting**: Request throttling to prevent abuse
- **Input Validation**: Pydantic models for data validation

### Performance Optimization
- **Async/Await**: Asynchronous programming throughout
- **Connection Pooling**: Efficient HTTP client management
- **Caching**: Redis-based caching for frequently accessed data
- **Background Processing**: Celery for long-running tasks

## Future Enhancement Plans

### Planned Features
- **Enhanced AI Models**: Integration with additional AI providers
- **Advanced Scheduling**: More sophisticated scheduling options
- **Content Templates**: Reusable content templates
- **Analytics Dashboard**: Content performance tracking
- **Multi-user Support**: Enhanced user management system

### Technical Debt
- **Email System Migration**: Complete transition to WordPress-only publishing
- **Database Migration**: Potential migration from JSON to SQL database
- **API Versioning**: Implementation of API versioning strategy
- **Monitoring**: Enhanced application monitoring and alerting

---

## Quick Reference for AI Assistants

### Key Entry Points
- **Main Application**: `app/main.py` - FastAPI app configuration
- **Content Engine**: `app/services/content_generator.py` - Core content generation
- **WordPress Service**: `app/services/wordpress.py` - WordPress integration
- **Task Scheduler**: `app/services/scheduler.py` - Background task processing

### Common Operations
- **Add New Endpoint**: Create in appropriate `app/api/` module
- **Modify Content Generation**: Update `app/services/content_generator.py`
- **Change Data Models**: Update `app/models/base.py`
- **Add New Service**: Create in `app/services/` with dependency injection

### Testing Commands
- **Run Server**: `python run.py`
- **Health Check**: `curl http://localhost:8000/health`
- **Integration Tests**: `python test_content_engine.py`
- **API Tests**: `python test_api_fix.py`

This documentation provides a comprehensive overview of the ScratchV3 codebase, enabling any AI assistant to quickly understand the project structure, functionality, and development patterns.
