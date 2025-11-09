# 🎯 ScratchV3 Application Overview

## 1. Primary Purpose

**ScratchV3** is a comprehensive AI-powered content generation and automation platform designed for **automated content creation at scale**. The application serves as a centralized hub for generating blogs, articles, news posts, and social media content with intelligent scheduling, WordPress integration, and chat-reference capabilities.

**Core Value Proposition**: Transform content creation from manual writing to automated, AI-driven workflows that can reference existing conversations, follow custom rules, and publish directly to WordPress sites as drafts.

## 2. Core Features

### 🤖 **Multi-Provider AI Integration**
- **OpenAI**: GPT-3.5, GPT-4 models for high-quality content
- **OpenRouter**: Access to multiple AI models (Claude, Llama, Gemini)
- **LM Studio**: Local AI model execution for privacy and cost savings
- Dynamic model selection per user with fallback logic

### 📝 **Advanced Content Generation**
- **Content Types**: Blog posts, articles, news, social media posts
- **Chat Reference System**: Ingest and reference multiple chat conversations for context
- **Dynamic Rule Parsing**: Free-form content rules (e.g., "no bullet points", "casual tone", "include statistics")
- **Quality Assurance**: Automated content filtering and formatting

### 🌐 **WordPress Integration**
- Direct publishing to WordPress sites as drafts
- WordPress App Password authentication
- URL preset management for multiple sites
- Connection testing and site information retrieval

### 📅 **Advanced Task Scheduling**
- Redis-backed task queue with APScheduler
- Immediate execution or scheduled content generation
- Batch task processing with concurrent limits
- Automatic retry logic and failure handling

### 🔐 **Security & Management**
- Encrypted API key storage with AES encryption
- Session-based authentication with configurable timeouts
- Real-time API key status monitoring
- User settings management with secure storage

## 3. User Workflow

### **Initial Setup & Configuration**

1. **Login & Access**
   - Navigate to application URL
   - Login with credentials (default: admin/admin123)
   - Access main dashboard interface

2. **API Provider Configuration**
   ```
   Dashboard → Settings → AI Provider Settings
   - Select provider: OpenAI, OpenRouter, or LM Studio
   - Enter API keys (encrypted automatically)
   - Choose default models
   - Test connection with "Test API Key" button
   ```

3. **WordPress Setup** (Optional)
   ```
   Dashboard → Settings → WordPress
   - Add WordPress site URLs
   - Configure App Password credentials
   - Test connection to verify access
   - Save as URL presets for quick selection
   ```

### **Content Generation Workflow**

1. **Create New Task**
   ```
   Dashboard → "Add New Topic" button
   ```

2. **Configure Content Parameters**
   - **Topic**: "Benefits of Remote Work for Productivity"
   - **Rules**: "professional tone, include 3-5 statistics, no bullet points, UK English"
   - **Chat References**: Select relevant chat files from `data/chats/`
   - **Content Type**: Blog, Article, News, or Social Media
   - **WordPress Site**: Choose from configured presets

3. **Scheduling Options**
   - **Immediate**: Execute task now
   - **Scheduled**: Set specific date/time for execution
   - **Recurring**: Set up repeated content generation

4. **Task Execution & Monitoring**
   ```
   Dashboard → Task Status Panel
   - Real-time status updates (Pending → Running → Completed)
   - Progress indicators and error reporting
   - Live task queue monitoring
   ```

5. **Review Generated Content**
   ```
   Dashboard → Content History
   - View generated articles with metadata
   - Check WordPress draft status
   - Download or copy content
   - Review AI provider and token usage
   ```

### **Chat Reference Integration**

1. **Prepare Chat Files**
   - Export conversations as `.txt` files
   - Upload to `data/chats/` directory

2. **Reference in Tasks**
   - Select relevant chats during task creation
   - System automatically summarizes and integrates context
   - AI generates content based on chat insights

## 4. Technical Architecture

### **Core Service Layer**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Service    │    │ Content Engine  │    │ Task Scheduler  │
│                 │    │                 │    │                 │
│ • OpenAI        │◄──►│ • Rule Parsing  │◄──►│ • APScheduler   │
│ • OpenRouter    │    │ • Chat Refs     │    │ • Redis Queue   │
│ • LM Studio     │    │ • Prompt Build  │    │ • Retry Logic   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │ WordPress API   │    │ Storage Service │    │ Security Layer  │
         │                 │    │                 │    │                 │
         │ • Draft Posts   │    │ • File Storage  │    │ • Encryption    │
         │ • Site Testing  │    │ • User Data     │    │ • Auth Sessions │
         │ • URL Presets   │    │ • Task History  │    │ • API Keys      │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Flow Example**
1. **User creates task** → Stored in Redis queue
2. **Scheduler picks up task** → Loads user settings and chat references
3. **Rule parser processes** → Converts free-form rules to structured instructions
4. **Prompt builder creates** → Context-aware prompts with chat content
5. **AI service generates** → Content using selected provider/model
6. **WordPress service publishes** → Draft post to configured site
7. **Storage service saves** → Generated content and metadata
8. **Dashboard updates** → Real-time status and history

## 5. Target Users

### **Content Creators & Bloggers**
- **Use Case**: Automated blog post generation with consistent style
- **Workflow**: Schedule daily/weekly posts, reference previous conversations for continuity
- **Example**: Travel blogger generating destination guides based on chat research

### **Digital Marketing Agencies**
- **Use Case**: Scale content production for multiple clients
- **Workflow**: Batch generate social media posts, articles with client-specific rules
- **Example**: Agency creating 50 LinkedIn posts per week across 10 client accounts

### **News & Media Organizations**
- **Use Case**: Rapid content generation for breaking news and analysis
- **Workflow**: Reference chat discussions with experts, generate articles with specific editorial guidelines
- **Example**: Tech news site generating analysis pieces based on developer interviews

### **Small Business Owners**
- **Use Case**: Consistent content marketing without dedicated writers
- **Workflow**: Weekly blog posts, social media content with brand voice consistency
- **Example**: SaaS startup generating educational content about their industry

### **Content Strategists**
- **Use Case**: Research-driven content creation with chat reference integration
- **Workflow**: Convert strategy discussions into actionable content pieces
- **Example**: Converting client strategy sessions into comprehensive content calendars

### **Typical User Scenarios**

1. **Daily Content Automation**
   ```
   Morning: Schedule 5 social media posts for the week
   Afternoon: Generate 2 blog articles based on customer chat logs
   Evening: Review WordPress drafts and publish
   ```

2. **Campaign Content Creation**
   ```
   Week 1: Upload campaign strategy chats
   Week 2: Generate 20 pieces of campaign content
   Week 3: Schedule publication across multiple WordPress sites
   Week 4: Monitor performance and iterate
   ```

3. **Research-to-Content Pipeline**
   ```
   Research Phase: Collect expert interviews as chat files
   Processing: Reference chats in content generation tasks
   Production: Generate comprehensive articles with expert insights
   Distribution: Auto-publish to WordPress for editorial review
   ```

The platform excels at **transforming conversations into content**, making it particularly valuable for teams that generate insights through discussions and need to scale that knowledge into published content efficiently.
