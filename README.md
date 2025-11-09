# 🎯 Scratch Automation App

**AI-powered content generation and automation platform** for blogs, articles, news, and social media posts with advanced scheduling, chat-reference integration, and WordPress publishing.

## ✨ Key Features

- 🤖 **AI Content Generation** - OpenAI & OpenRouter integration with dynamic prompting
- 📝 **Chat Reference System** - Ingest and reference multiple chat conversations
- 🎯 **Dynamic Rule Parsing** - Free-form content rules with intelligent parsing
- 📅 **Advanced Scheduling** - Redis-backed task queue with failure handling
- 🌐 **WordPress Integration** - Direct publishing to WordPress sites as drafts
- 🔐 **Secure API Key Management** - Encrypted storage with status monitoring
- 🌙 **Modern Dark Theme UI** - Professional interface with custom icons
- 🛡️ **Content QA Filtering** - Automated quality assurance and formatting
- 📊 **Real-time Dashboard** - Live task monitoring and history tracking

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Redis Server** (for background task processing)
- **API Keys**: OpenAI/OpenRouter, Pexels (optional)

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd ScratchV3
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Redis** (required for task scheduling)
```bash
# Ubuntu/Debian
sudo systemctl start redis-server

# macOS with Homebrew
brew services start redis

# Windows (with Redis installed)
redis-server
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings (see Configuration section)
```

6. **Initialize database**
```bash
# Run database migrations
alembic upgrade head
```

7. **Start the application**
```bash
python run.py
```

The app will be available at `http://localhost:8000`

### Default Login
- **Username**: `admin`
- **Password**: `admin123`

## 📋 Complete Feature Set

### 🤖 AI & Content Generation
- **Multi-Provider AI Support** - OpenAI GPT-4 and OpenRouter integration
- **Dynamic Prompt Building** - Intelligent prompt construction with context
- **Chat Reference Integration** - Load and reference multiple chat conversations
- **Content QA Filtering** - Automated bullet point, emoji, and spelling checks
- **Free-form Rule Parsing** - Natural language content rules and constraints

### 📅 Task Management & Scheduling
- **Advanced Scheduler** - APScheduler with Redis backend for reliability
- **Failure Handling** - Automatic retry logic and failure state management
- **Redis Locking** - Prevents duplicate task execution
- **Real-time Status** - Live updates on task progress and completion
- **History Tracking** - Complete audit trail of all generated content

### 🌐 WordPress Integration
- **Direct Publishing** - Publish content as WordPress drafts
- **Multi-site Support** - Manage multiple WordPress installations
- **Secure Authentication** - Encrypted credential storage
- **Payload Validation** - Ensures proper title, content, and metadata

### 🔐 Security & API Management
- **Encrypted Key Storage** - Secure API key management with encryption
- **Key Status Monitoring** - Real-time validation of API key connectivity
- **User Authentication** - Session-based login system
- **Input Validation** - Comprehensive request validation and sanitization

### 🎨 Modern UI/UX
- **Dark Theme Design** - Professional dark mode interface
- **Custom Icon System** - Clean symbols instead of emojis
- **Responsive Layout** - Works on desktop and mobile devices
- **Real-time Updates** - Live dashboard with status indicators
- **Intuitive Navigation** - Clean, organized interface design

## 🏗️ Architecture & Usage

### Project Structure
```
app/
├── api/                    # API endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── tasks.py           # Task management & scheduling
│   ├── content.py         # Content generation
│   ├── keys.py            # API key management
│   └── wordpress.py       # WordPress integration
├── models/                # Pydantic data models
├── middleware/            # Custom middleware
├── services/              # Core business logic
│   ├── content_generator.py  # AI content generation
│   ├── scheduler.py          # Task scheduling
│   ├── prompt_builder.py     # Dynamic prompt construction
│   ├── rules.py             # Rule parsing engine
│   ├── wordpress.py         # WordPress API client
│   └── ai_services.py       # AI provider integrations
├── utils/                 # Utility functions
└── main.py               # FastAPI application

static/
├── css/                   # Stylesheets with theme system
├── js/                    # Frontend JavaScript
└── uploads/               # File upload storage

data/
├── chats/                 # Chat reference files
├── history/               # Generated content history
├── tasks/                 # Task data storage
└── users/                 # User data and settings

tests/                     # Comprehensive test suite
├── unit/                  # Unit tests
├── integration/           # Integration tests
└── e2e/                   # End-to-end Playwright tests
```

### Core API Endpoints

#### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - User logout

#### Task Management
- `GET /api/tasks/` - Get user tasks with status
- `POST /api/tasks/schedule` - Schedule new content generation task
- `GET /api/tasks/{task_id}` - Get specific task details
- `DELETE /api/tasks/{task_id}` - Cancel/delete task

#### Content Generation
- `POST /api/content/generate` - Generate content with AI
- `GET /api/content/history` - Get content generation history

#### API Key Management
- `GET /api/keys/status` - Check API key connectivity status
- `POST /api/keys` - Save/update API keys

#### WordPress Integration
- `GET /api/wp/sites` - List configured WordPress sites
- `POST /api/wp/sites` - Add new WordPress site
- `DELETE /api/wp/sites/{site_id}` - Remove WordPress site
- `GET /api/wp/auth` - Get WordPress credentials
- `POST /api/wp/auth` - Save WordPress credentials

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=sqlite:///./data/app.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Service API Keys
OPENAI_API_KEY=sk-your-openai-key
OPENROUTER_API_KEY=sk-or-your-openrouter-key

# Image Generation (Optional)
PEXELS_API_KEY=your-pexels-key

# Security
ENCRYPTION_KEY=your-32-byte-encryption-key
```

### API Key Setup

1. **OpenAI API Key**
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create a new API key
   - Add to `.env` as `OPENAI_API_KEY`

2. **OpenRouter API Key** (Alternative to OpenAI)
   - Visit [OpenRouter](https://openrouter.ai/keys)
   - Create account and generate API key
   - Add to `.env` as `OPENROUTER_API_KEY`

3. **Pexels API Key** (Optional - for image generation)
   - Visit [Pexels API](https://www.pexels.com/api/)
   - Create account and get API key
   - Add to `.env` as `PEXELS_API_KEY`

### WordPress Configuration

WordPress sites and credentials are managed through the Settings page in the web interface:

1. Navigate to Settings → WordPress
2. Add your WordPress site URLs
3. Configure username and password (stored encrypted)
4. Test connection to ensure proper setup

## 🎯 Usage Guide

### 1. Creating Content Tasks

1. **Access Dashboard** - Login and navigate to the main dashboard
2. **Add New Topic** - Click "Add New Topic" button
3. **Configure Task**:
   - **Topic**: Describe what content you want generated
   - **Rules**: Add free-form rules like "no bullet points", "include statistics", "casual tone"
   - **Chat References**: Select chat files to reference for context
   - **Schedule**: Choose immediate execution or schedule for later
   - **WordPress**: Select target WordPress site (optional)

### 2. Chat Reference System

1. **Prepare Chat Files** - Export chat conversations as `.txt` files
2. **Upload to `data/chats/`** - Place files in the chats directory
3. **Reference in Tasks** - Select relevant chats when creating content tasks
4. **AI Integration** - The system automatically summarizes and references chat content

### 3. Rule System Examples

The rule parser understands natural language instructions:

```
# Content Style Rules
"Write in a casual, conversational tone"
"Include 3-5 statistics or data points"
"No bullet points or numbered lists"
"Keep paragraphs under 3 sentences"

# SEO and Structure Rules
"Include relevant keywords naturally"
"Add a compelling introduction and conclusion"
"Use subheadings for better readability"
"Target 800-1200 words"

# Content Guidelines
"Avoid technical jargon"
"Include real-world examples"
"Write for a beginner audience"
"Focus on actionable advice"
```

### 4. Monitoring and Management

- **Dashboard Overview** - View all active and completed tasks
- **Real-time Status** - Monitor task progress with live updates
- **History Tracking** - Review all generated content in the History section
- **Error Handling** - Failed tasks are clearly marked with error details

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests

# Run with coverage
pytest --cov=app tests/
```

### Manual Testing Checklist
- [ ] Login functionality works
- [ ] Task creation and scheduling
- [ ] AI content generation
- [ ] WordPress publishing
- [ ] API key management
- [ ] Chat reference loading
- [ ] Rule parsing and application

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment
   ENVIRONMENT=production
   DEBUG=false

   # Use production database
   DATABASE_URL=postgresql://user:pass@localhost/scratchv3

   # Configure Redis
   REDIS_URL=redis://localhost:6379/0
   ```

2. **Security Hardening**
   - Generate strong `SECRET_KEY` and `ENCRYPTION_KEY`
   - Use HTTPS in production
   - Configure proper firewall rules
   - Regular security updates

3. **Process Management**
   ```bash
   # Using systemd (recommended)
   sudo systemctl enable scratchv3
   sudo systemctl start scratchv3

   # Or using PM2
   pm2 start run.py --name scratchv3
   pm2 save
   pm2 startup
   ```

4. **Monitoring**
   - Monitor Redis connectivity
   - Check API key validity
   - Monitor task queue health
   - Set up log rotation

## 🤝 Contributing

This is a private application. When contributing:

1. **Follow Patterns** - Maintain consistency with existing code
2. **Write Tests** - All new features require test coverage
3. **Update Documentation** - Keep README and API docs current
4. **Code Quality** - Run linting and formatting before commits

## 📄 License

Private - All rights reserved.
