<div align="center">

# 🌺 Champa

### Your Intelligent Communication Assistant

**Take back control of your inbox with AI-powered intelligence**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-orange.svg)](https://www.langchain.com/)

[Features](#key-features) • [Quick Start](#quick-start) • [Documentation](#detailed-setup-guides) • [Demo](#) • [Contributing](#contributing)

</div>

---

## Overview

Champa is an intelligent unified inbox that brings together **Gmail**, **Slack**, and **Google Calendar** into a single, AI-powered interface. Using advanced LangGraph agents and LangChain orchestration, Champa automatically analyzes every message, extracts actionable insights, and helps you respond faster - all while keeping you in control.

**Built with cutting-edge AI technology, designed for modern professionals.**

## Why Champa?

Modern professionals are drowning in communications. The average person:
- Checks email **15 times per day**
- Switches between **3-5 communication platforms** constantly
- Spends **28% of their workday** managing emails
- Misses important messages buried under spam and newsletters

**Champa solves this.** One unified interface. AI-powered intelligence. Human-in-the-loop control.

---

## What Makes Champa Different?

### 🎯 Unified Intelligence
Unlike traditional email clients that just display messages, Champa **understands** them. Every message is automatically analyzed for:
- **Summary**: Get the gist in seconds
- **Priority**: High, medium, or low - know what needs attention
- **Intent**: Is it a question? Request? FYI? Update?
- **Action Items**: Automatic extraction of tasks and deadlines
- **Spam Detection**: Intelligent filtering with one-click unsubscribe

### 🤖 AI That Sounds Like You
Champa's smart reply system uses **LangGraph deep agents** with user persona memory to generate responses that match your communication style. Not generic templates - contextual, personalized replies that sound human.

### 🛡️ Human-in-the-Loop by Design
AI is powerful, but you're in charge. Every AI-generated reply requires your review and approval before sending. Edit, refine, or regenerate - you decide what goes out.

### 🔌 Direct Platform Integration
No third-party middleware. Champa connects directly to Gmail, Slack, and Google Calendar using official APIs and OAuth 2.0. Your data stays between you and your platforms.

### 💬 Conversational Interface
Ask your inbox questions: "What meetings do I have tomorrow?" "Show me urgent emails from this week." "Summarize my unread Slack messages." Your AI assistant knows your communications.

---

## Key Features

### Unified Communication Hub
Connect multiple platforms with secure OAuth authentication:
- **Gmail**: Full email access with read, send, and modify permissions
- **Slack**: Workspace messages, channels, and direct messages
- **Google Calendar**: Events, meetings, and scheduling

All your communications in one clean, organized interface.

### AI-Powered Message Analysis
Every message is automatically processed through an intelligent pipeline:

**Summarization**: Long emails condensed into key points
**Classification**: 7 intent categories (question, request, information, meeting, task, feedback, other)
**Priority Scoring**: ML-based priority assignment (high/medium/low)
**Entity Extraction**: Automatic detection of tasks, deadlines, and action items
**Spam Detection**: 4 spam types with confidence scoring and unsubscribe link extraction

### Smart Reply Generation
Context-aware response drafts powered by advanced AI:
- **Deep Agent Architecture**: LangGraph orchestration with planning and execution
- **Persona Memory**: Learns your communication style over time
- **Context Understanding**: Analyzes message history and thread context
- **Multi-Platform Support**: Generate replies for email and Slack
- **Approval Workflow**: Review, edit, and approve before sending

### Interactive Chat Assistant
Natural language interface to your communications:
- Query messages across all platforms
- Get summaries and insights
- Execute actions (mark as read, archive, etc.)
- Ask about upcoming events and deadlines
- Powered by LangGraph agents with tool calling

### Visual Dashboard
Beautiful, information-dense interface with:
- Priority distribution charts
- Spam analytics and trends
- Upcoming deadlines widget
- Platform connection status
- Real-time statistics
- RetroUI brutalist design

---

## How It Works

### 1. Connect Your Platforms
Secure OAuth 2.0 authentication with Gmail, Slack, and Google Calendar. One-click setup, no passwords stored.

### 2. Automatic Synchronization
Champa fetches and normalizes messages from all connected platforms. Messages are stored locally with full metadata.

### 3. AI Analysis Pipeline
Every message flows through the AI pipeline:
```
Message → Summarization → Classification → Priority Scoring → Entity Extraction → Spam Detection → Storage
```

### 4. Unified Interface
View all communications in a single feed with:
- Filters by platform, priority, and spam status
- Search across all messages
- Thread grouping
- Rich message previews

### 5. Smart Interactions
- Generate AI replies with one click
- Chat with your inbox
- One-click unsubscribe from spam
- Mark messages by priority
- Archive and organize

---

## Technology Stack

Champa is built with modern, production-ready technologies:

### Backend Architecture
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Relational database for messages and user data
- **Qdrant**: Vector database for semantic search and embeddings
- **Auth0**: Enterprise-grade authentication with JWT tokens
- **SQLAlchemy**: ORM with Alembic migrations
- **Pydantic**: Data validation and serialization

### AI & Machine Learning
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM chain composition and tool calling
- **OpenAI GPT-4**: Large language model for analysis and generation
- **Sentence Transformers**: Message embeddings for semantic search
- **Deep Agent Architecture**: Multi-step reasoning with planning

### Frontend Stack
- **React 18**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **RetroUI**: Brutalist design component library
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **Recharts**: Data visualization

### Platform Integrations
- **Gmail API**: Direct Google OAuth integration
- **Slack SDK**: Official Slack API client
- **Google Calendar API**: Calendar and event management
- **No Third-Party Dependencies**: All integrations use official SDKs

### Development & Testing
- **pytest**: Backend testing with Hypothesis for property-based tests
- **Jest**: Frontend testing with React Testing Library
- **Docker Compose**: Local development environment
- **Alembic**: Database migration management

---

## Features in Detail

### Message Analysis Deep Dive

**Summarization Engine**
- Extracts key points from long messages
- Preserves important context and details
- Handles multi-paragraph emails and threads
- Optimized for quick scanning

**Intent Classification**
Uses machine learning to categorize messages into 7 types:
1. **Question**: Requires a response with information
2. **Request**: Asks for action or favor
3. **Information**: FYI, updates, announcements
4. **Meeting**: Scheduling, invites, calendar-related
5. **Task**: Assignments, to-dos, deliverables
6. **Feedback**: Reviews, comments, opinions
7. **Other**: Miscellaneous communications

**Priority Scoring**
Multi-factor analysis determines message urgency:
- Sender importance and relationship
- Keywords and phrases indicating urgency
- Deadline proximity
- Thread history and context
- User interaction patterns

**Spam Detection**
Advanced filtering with 4 spam categories:
- **Promotional**: Marketing, sales, offers
- **Newsletter**: Subscriptions, digests, updates
- **Marketing**: Advertising, campaigns
- **Phishing**: Suspicious, potentially malicious

Features:
- Confidence scoring (0-100%)
- Automatic unsubscribe link extraction (RFC 2369 + content parsing)
- One-click unsubscribe action
- Spam analytics and trends

**Entity Extraction**
Automatically identifies:
- **Tasks**: Action items, to-dos, assignments
- **Deadlines**: Due dates, time-sensitive items
- **People**: Names, contacts, mentions
- **Events**: Meetings, appointments, schedules

### Smart Reply System Architecture

Champa's reply generation uses a sophisticated multi-agent system:

**1. Deep Agent Orchestrator**
- Plans response strategy based on message context
- Coordinates multiple specialized sub-agents
- Ensures coherent, contextual replies

**2. User Persona Memory**
- Learns your communication style over time
- Stores preferences, tone, and patterns
- Adapts replies to match your voice
- Uses LangGraph Store for long-term memory

**3. Context Analysis**
- Analyzes message thread history
- Understands conversation flow
- Identifies key points to address
- Maintains context across platforms

**4. Reply Generation**
- Creates natural, human-like responses
- Matches your tone and style
- Addresses all points in original message
- Suggests appropriate length and formality

**5. Human Approval Workflow**
- Review generated draft
- Edit and refine as needed
- Regenerate with different parameters
- Approve and send when ready

### Chat Assistant Capabilities

The AI chat assistant provides natural language access to your communications:

**Query Examples:**
- "Show me all high-priority emails from this week"
- "What meetings do I have tomorrow?"
- "Summarize my unread Slack messages"
- "Find emails about the project deadline"
- "What tasks are due this week?"

**Actions:**
- Mark messages as read/unread
- Archive or delete messages
- Change priority levels
- Generate replies
- Search across platforms

**Powered by LangGraph:**
- Tool calling for platform actions
- Memory for conversation context
- Multi-step reasoning
- Error handling and fallbacks

---

## Security & Privacy

### Authentication
- **Auth0 Integration**: Enterprise-grade authentication
- **JWT Tokens**: Secure, stateless authentication
- **OAuth 2.0**: Industry-standard platform authorization
- **Social Login**: Google, Facebook, Twitter support
- **MFA Support**: Optional multi-factor authentication

### Data Protection
- **Encrypted Storage**: All data encrypted at rest
- **Secure Transmission**: HTTPS/TLS for all communications
- **Token Refresh**: Automatic OAuth token renewal
- **No Third-Party Access**: Direct platform integrations only
- **User Control**: Delete your data anytime

### Privacy Principles
- **Your Data, Your Control**: We don't sell or share your data
- **Transparent Processing**: Clear AI analysis pipeline
- **Human Oversight**: You approve all AI actions
- **Minimal Storage**: Only store what's necessary
- **Open Source**: Full code transparency

---

## Performance & Scalability

### Optimizations
- **Async Processing**: Non-blocking I/O for all operations
- **Vector Search**: Fast semantic search with Qdrant
- **Database Indexing**: Optimized queries on frequently accessed fields
- **Caching**: Redis-ready architecture for response caching
- **Batch Processing**: Efficient bulk message synchronization

### Scalability
- **Horizontal Scaling**: Stateless backend design
- **Database Pooling**: Connection management for high concurrency
- **Queue System**: Background job processing (Celery-ready)
- **CDN Support**: Static asset delivery optimization
- **Docker Deployment**: Container orchestration ready

---

## Use Cases

### For Busy Professionals
- Triage hundreds of emails in minutes
- Never miss important messages
- Respond faster with AI-generated drafts
- Stay organized across platforms

### For Team Leaders
- Monitor team communications
- Track action items and deadlines
- Prioritize urgent requests
- Maintain communication consistency

### For Customer Support
- Quickly understand customer issues
- Generate professional responses
- Track support tickets across platforms
- Identify urgent cases automatically

### For Freelancers
- Manage multiple client communications
- Track project deadlines
- Professional response generation
- Unified view of all work communications

---

## Roadmap

### Coming Soon
- [ ] Microsoft Outlook integration
- [ ] WhatsApp Business integration
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Mobile applications (iOS/Android)
- [ ] Browser extension
- [ ] Email scheduling
- [ ] Template library
- [ ] Multi-language support
- [ ] Voice interface

### Future Vision
- **Proactive Assistance**: AI suggests actions before you ask
- **Meeting Preparation**: Auto-generate meeting briefs
- **Follow-up Tracking**: Never forget to follow up
- **Sentiment Analysis**: Understand emotional tone
- **Relationship Intelligence**: Track communication patterns
- **Integration Marketplace**: Connect any platform

---

## Quick Start

Get Champa running in under 10 minutes.

### Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend development
- **Docker & Docker Compose** - Database services
- **Auth0 Account** - Free tier at [auth0.com](https://auth0.com)
- **Google Cloud Project** - For Gmail & Calendar APIs
- **OpenAI API Key** - For AI features
- **Slack App** (Optional) - For Slack integration

### Installation Steps

#### 1. Clone and Setup Databases

```bash
# Clone repository
git clone <repository-url>
cd champa

# Start PostgreSQL and Qdrant
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. Configure Auth0

Create a free Auth0 account and set up:

**Single Page Application:**
- Name: `Champa Frontend`
- Type: Single Page Web Application
- Callback URL: `http://localhost:5173/callback`
- Logout URL: `http://localhost:5173/login`
- Web Origins: `http://localhost:5173`

**API:**
- Name: `Champa API`
- Identifier: `https://champa-api`
- Enable offline access

Save your credentials:
- Domain (e.g., `your-tenant.auth0.com`)
- Client ID
- Client Secret
- API Audience (e.g., `https://champa-api`)

📖 **Detailed guide:** See [Auth0 Setup Guide](#auth0-setup-guide) below

#### 3. Configure Google OAuth

Set up Google Cloud project for Gmail and Calendar:

1. Create project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable Gmail API and Google Calendar API
3. Configure OAuth consent screen
4. Create OAuth credentials (Web application)
5. Add redirect URI: `http://localhost:8000/api/platforms/gmail/callback`

Save your credentials:
- Client ID
- Client Secret

📖 **Detailed guide:** See [Google OAuth Setup](#google-oauth-setup-gmail--calendar) below

#### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see below)

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

**Backend runs at:** `http://localhost:8000`

#### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Auth0 credentials (see below)

# Start development server
npm run dev
```

**Frontend runs at:** `http://localhost:5173`

#### 6. First Login

1. Open `http://localhost:5173`
2. Click "Login"
3. Authenticate via Auth0
4. Connect Gmail, Slack, or Calendar
5. Start managing your communications!

---

## Configuration

### Backend Environment Variables

Create `backend/.env` with these settings:

```bash
# Database
DATABASE_URL=postgresql://champa:champa_password@localhost:5432/champa

# Auth0 Authentication
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://champa-api
AUTH0_CLIENT_ID=your-backend-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional for local development

# Google OAuth (Gmail & Calendar)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/platforms/gmail/callback

# Slack OAuth (Optional)
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
SLACK_REDIRECT_URI=http://localhost:8000/api/platforms/slack/callback

# Application Settings
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

### Frontend Environment Variables

Create `frontend/.env` with these settings:

```bash
# Backend API
VITE_API_BASE_URL=http://localhost:8000

# Auth0 Configuration
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-frontend-client-id
VITE_AUTH0_AUDIENCE=https://champa-api
VITE_AUTH0_REDIRECT_URI=http://localhost:5173/callback
```

⚠️ **Security Note:** Never commit `.env` files to version control. Use `.env.example` as a template.

---

## API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Key API Endpoints

**Authentication**
```
GET    /api/auth/me              Get current user profile
POST   /api/auth/logout          Logout and revoke tokens
PATCH  /api/auth/profile         Update user profile
```

**Messages**
```
GET    /api/messages             List messages with filters
GET    /api/messages/{id}        Get message details
GET    /api/messages/{id}/analysis   Get AI analysis
POST   /api/messages/sync        Trigger message synchronization
```

**Statistics**
```
GET    /api/stats/overview       Dashboard overview statistics
GET    /api/stats/spam           Spam detection analytics
GET    /api/stats/priority-distribution   Priority breakdown
GET    /api/stats/actionables    Actionable items summary
```

**Smart Replies**
```
POST   /api/replies/generate     Generate AI reply draft
GET    /api/replies/{id}         Get reply details
PATCH  /api/replies/{id}         Edit reply draft
POST   /api/replies/{id}/approve Approve and send reply
```

**Platform Connections**
```
GET    /api/platforms            List connected platforms
GET    /api/platforms/{platform}/auth-url   Get OAuth URL
GET    /api/platforms/{platform}/callback   OAuth callback handler
DELETE /api/platforms/{platform} Disconnect platform
```

**Chat Assistant**
```
POST   /api/chat                 Send message to AI assistant
GET    /api/chat/history         Get conversation history
```

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + RetroUI + Auth0 React SDK             │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/REST API
┌─────────────────────▼───────────────────────────────────────┐
│                      Backend API                             │
│         FastAPI + Auth0 JWT + SQLAlchemy                     │
├──────────────────────────────────────────────────────────────┤
│                   Service Layer                              │
│  Auth │ Messages │ Platforms │ AI │ Replies                 │
├──────────────────────────────────────────────────────────────┤
│                 AI Pipeline                                  │
│  LangGraph Agents │ LangChain Chains │ OpenAI GPT-4         │
└─────────┬────────────────────┬────────────────┬─────────────┘
          │                    │                │
┌─────────▼─────────┐ ┌───────▼──────┐ ┌──────▼──────────────┐
│   PostgreSQL      │ │   Qdrant     │ │  Platform APIs      │
│  (Messages, Users)│ │  (Vectors)   │ │ Gmail│Slack│Calendar│
└───────────────────┘ └──────────────┘ └─────────────────────┘
```

### Project Structure

```
champa/
├── backend/                  # FastAPI Backend Application
│   ├── alembic/              # Database migrations
│   │   └── versions/         # Migration scripts
│   ├── app/
│   │   ├── api/              # API Endpoints
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── messages.py   # Message CRUD operations
│   │   │   ├── platforms.py  # Platform connection management
│   │   │   ├── replies.py    # Smart reply generation
│   │   │   ├── stats.py      # Statistics and analytics
│   │   │   ├── chat.py       # Chat assistant interface
│   │   │   └── dependencies.py # Shared dependencies
│   │   ├── core/             # Core Configuration
│   │   │   ├── config.py     # Settings and environment
│   │   │   ├── security.py   # Auth0 JWT validation
│   │   │   └── database.py   # Database connection
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   │   ├── user.py       # User and persona models
│   │   │   ├── message.py    # Message and analysis models
│   │   │   └── platform.py   # Platform connection models
│   │   ├── schemas/          # Pydantic Schemas
│   │   │   ├── message.py    # Message validation schemas
│   │   │   ├── reply.py      # Reply schemas
│   │   │   ├── user.py       # User schemas
│   │   │   └── chat.py       # Chat schemas
│   │   ├── services/         # Business Logic Layer
│   │   │   ├── auth.py       # Authentication service
│   │   │   ├── message.py    # Message fetching and normalization
│   │   │   ├── platform.py   # Platform integration management
│   │   │   ├── ai.py         # AI pipeline orchestration
│   │   │   └── reply.py      # Smart reply service
│   │   ├── integrations/     # Platform Integration Layer
│   │   │   ├── interfaces.py # Abstract platform interfaces
│   │   │   ├── google/       # Google API Adapters
│   │   │   │   ├── gmail.py  # Direct Gmail API integration
│   │   │   │   ├── calendar_adapter.py # Calendar integration
│   │   │   │   └── calendar_tools.py   # Calendar tools
│   │   │   └── slack/        # Slack API Adapters
│   │   │       ├── slack_adapter.py # Direct Slack API
│   │   │       └── slack_tools.py   # Slack tools
│   │   ├── ai/               # AI Pipeline Components
│   │   │   ├── agents/       # LangGraph Agents
│   │   │   │   ├── deep_agent.py # Deep agent orchestrator
│   │   │   │   ├── analyzer.py   # Message analysis agent
│   │   │   │   └── chat.py       # Chat assistant agent
│   │   │   ├── chains/       # LangChain Chains
│   │   │   │   ├── summarize.py      # Summarization
│   │   │   │   ├── classify.py       # Intent classification
│   │   │   │   ├── extract.py        # Entity extraction
│   │   │   │   ├── prioritize.py     # Priority scoring
│   │   │   │   ├── smart_reply.py    # Reply generation
│   │   │   │   └── spam_detection.py # Spam filtering
│   │   │   ├── memory/       # User Persona and Memory
│   │   │   │   └── persona_store.py  # LangGraph Store
│   │   │   ├── embeddings/   # Vector Generation
│   │   │   │   └── qdrant_client.py  # Qdrant integration
│   │   │   ├── config.py     # AI configuration
│   │   │   └── fallback.py   # Fallback processing
│   │   └── utils/            # Utilities
│   │       ├── retry.py      # Exponential backoff
│   │       ├── errors.py     # Error handling
│   │       ├── database.py   # Database utilities
│   │       └── token_refresh.py # OAuth token refresh
│   ├── tests/                # Backend Tests
│   │   ├── test_auth_properties.py
│   │   ├── test_message_normalization_properties.py
│   │   ├── test_platform_integration_properties.py
│   │   ├── test_api_integration.py
│   │   ├── test_chat_agent.py
│   │   └── test_deep_agent_integration.py
│   ├── main.py               # FastAPI application entry
│   ├── requirements.txt      # Python dependencies
│   ├── pytest.ini            # Pytest configuration
│   └── alembic.ini           # Alembic configuration
│
├── frontend/                 # React Frontend Application
│   ├── src/
│   │   ├── components/       # React Components
│   │   │   ├── MessageWithReplies.tsx
│   │   │   ├── Icons.tsx
│   │   │   └── (RetroUI components)
│   │   ├── pages/            # Page Components
│   │   │   ├── LandingPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   └── OAuthRedirectPage.tsx
│   │   ├── contexts/         # React Contexts
│   │   │   └── AuthContext.tsx # Auth0 context
│   │   ├── hooks/            # Custom Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useMessages.ts
│   │   │   ├── useReplies.ts
│   │   │   ├── useStats.ts
│   │   │   └── usePlatforms.ts
│   │   ├── services/         # API Client Services
│   │   │   ├── auth.ts       # Auth API calls
│   │   │   ├── messages.ts   # Message API calls
│   │   │   ├── platforms.ts  # Platform API calls
│   │   │   ├── replies.ts    # Reply API calls
│   │   │   └── stats.ts      # Stats API calls
│   │   ├── App.tsx           # Root component
│   │   ├── main.tsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── package.json
│   └── vite.config.ts
│
├── .kiro/                    # Kiro AI Configuration
│   ├── specs/                # Feature specifications
│   └── steering/             # Project guidelines
├── docker-compose.yml        # Production Docker Compose
├── docker-compose.dev.yml    # Development Docker Compose
├── LICENSE                   # MIT License
└── README.md                 # This file
```

### Design Patterns

**Backend Architecture:**
- **Layered Architecture**: API → Services → Models → Database
- **Interface-Based Integration**: Abstract platform interfaces with direct API adapters
- **Service Layer Pattern**: Business logic isolated from API endpoints
- **Repository Pattern**: Database access through SQLAlchemy models
- **Dependency Injection**: FastAPI dependencies for auth and database

**Frontend Architecture:**
- **Component-Based**: Reusable RetroUI components
- **Context API**: Global state for authentication
- **Custom Hooks**: Encapsulate API calls and state logic
- **Protected Routes**: Authentication wrapper for secure pages
- **Service Layer**: Centralized API communication

**AI Pipeline:**
- **Agent Orchestration**: LangGraph deep agents with planning
- **Chain Composition**: LangChain chains for specific tasks
- **Memory Management**: LangGraph Store for user persona
- **Human-in-the-Loop**: Interrupt mechanism for reply approval

---

## Development Guide

### Backend Development

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run property-based tests (100+ iterations)
pytest -m property

# Run specific test file
pytest tests/test_spam_detection.py -v

# Run integration tests
pytest tests/test_api_integration.py -v

# Database migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head                               # Apply migrations
alembic downgrade -1                               # Rollback one migration
alembic current                                    # Show current version
alembic history                                    # Show migration history

# Code quality
black app/                                         # Format code
flake8 app/                                        # Lint code
mypy app/                                          # Type checking
```

### Frontend Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm run test:coverage

# Lint and format
npm run lint
npm run format

# Type checking
npm run type-check
```

### Docker Development

```bash
# Start databases only (recommended for development)
docker-compose -f docker-compose.dev.yml up -d

# Start all services (full stack)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f qdrant

# Rebuild containers after dependency changes
docker-compose up --build

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Scale backend instances
docker-compose up -d --scale backend=3

# Execute commands in running containers
docker-compose exec backend alembic upgrade head
docker-compose exec postgres psql -U champa -d champa
```

### Common Development Tasks

**Add a new API endpoint:**
1. Create endpoint in `backend/app/api/`
2. Add business logic in `backend/app/services/`
3. Create Pydantic schemas in `backend/app/schemas/`
4. Add tests in `backend/tests/`
5. Update API documentation

**Add a new platform integration:**
1. Implement interface in `backend/app/integrations/interfaces.py`
2. Create adapter in `backend/app/integrations/{platform}/`
3. Add OAuth flow in `backend/app/api/platforms.py`
4. Create tools for LangGraph agents
5. Add property-based tests

**Add a new AI chain:**
1. Create chain in `backend/app/ai/chains/`
2. Integrate into pipeline in `backend/app/services/ai.py`
3. Add to agent tools if needed
4. Test with various message types
5. Monitor token usage and costs

**Add a new frontend page:**
1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.tsx`
3. Create API service in `frontend/src/services/`
4. Create custom hook in `frontend/src/hooks/`
5. Use RetroUI components for consistency

---

## Troubleshooting

### Common Issues and Solutions

#### Authentication Problems

**"Could not validate credentials"**
```bash
# Check Auth0 configuration
✓ Verify AUTH0_DOMAIN matches in frontend and backend .env
✓ Ensure AUTH0_API_AUDIENCE is identical in both
✓ Confirm token is sent in Authorization: Bearer <token> header
✓ Check Auth0 API settings in dashboard
```

**Redirect loop on login**
```bash
# Fix redirect configuration
✓ Verify callback URL: http://localhost:5173/callback
✓ Clear browser cache and localStorage
✓ Check Auth0 application settings
✓ Ensure VITE_AUTH0_REDIRECT_URI is correct
```

**"Auth0 configuration is missing"**
```bash
# Verify environment variables
✓ Check all VITE_AUTH0_* variables in frontend/.env
✓ Restart development server: npm run dev
✓ Verify .env file is in frontend/ directory
```

#### Platform Connection Issues

**Gmail/Calendar OAuth fails**
```bash
# Verify Google Cloud setup
✓ Check OAuth credentials in Google Cloud Console
✓ Confirm redirect URI: http://localhost:8000/api/platforms/gmail/callback
✓ Ensure Gmail API and Calendar API are enabled
✓ Verify OAuth consent screen scopes
✓ Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env
```

**Slack connection fails**
```bash
# Verify Slack app setup
✓ Check Slack app credentials
✓ Confirm redirect URI in Slack app settings
✓ Ensure required bot scopes are added
✓ Verify SLACK_CLIENT_ID and SLACK_CLIENT_SECRET
```

**Token refresh errors**
```bash
# Fix OAuth token issues
✓ Reconnect platform from dashboard
✓ Check token_refresh.py logs
✓ Verify refresh token is stored in database
✓ Ensure platform API hasn't revoked access
```

#### Database Issues

**"relation does not exist" error**
```bash
# Run database migrations
cd backend
alembic upgrade head
alembic current  # Verify migrations applied
```

**Migration fails**
```bash
# Troubleshoot migrations
✓ Check DATABASE_URL in backend/.env
✓ Verify PostgreSQL is running: docker-compose ps
✓ Try rollback: alembic downgrade -1
✓ Check migration file for syntax errors
✓ Ensure database user has proper permissions
```

**Connection refused**
```bash
# Fix database connection
✓ Start PostgreSQL: docker-compose -f docker-compose.dev.yml up -d
✓ Check port 5432 is not in use
✓ Verify DATABASE_URL format: postgresql://user:pass@host:port/db
```

#### AI Pipeline Issues

**"OpenAI API key not found"**
```bash
# Configure OpenAI
✓ Set OPENAI_API_KEY in backend/.env
✓ Restart backend server
✓ Verify API key is valid at platform.openai.com
```

**AI analysis not running**
```bash
# Debug AI pipeline
✓ Check backend logs for errors
✓ Verify OpenAI API quota
✓ Test with: pytest tests/test_api_integration.py -v
✓ Check message analysis in database
```

**Qdrant connection fails**
```bash
# Fix vector database
✓ Start Qdrant: docker-compose -f docker-compose.dev.yml up -d
✓ Check QDRANT_URL in backend/.env
✓ Verify port 6333 is accessible
✓ For Qdrant Cloud, check QDRANT_API_KEY
```

**Spam detection not working**
```bash
# Verify spam detection
✓ Check messages have been analyzed
✓ Run: pytest tests/test_spam_detection.py -v
✓ Verify spam_detection.py chain is working
✓ Check OpenAI API logs
```

#### Development Issues

**Port already in use**
```bash
# Kill processes on ports
# Mac/Linux:
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Module not found errors**
```bash
# Reinstall dependencies
# Backend:
cd backend
pip install -r requirements.txt

# Frontend:
cd frontend
npm install
```

**CORS errors**
```bash
# Fix CORS configuration
✓ Check FRONTEND_URL in backend/.env
✓ Verify CORS settings in backend/main.py
✓ Ensure frontend is running on correct port
✓ Clear browser cache
```

**Docker issues**
```bash
# Reset Docker environment
docker-compose down -v          # Remove volumes
docker-compose up --build -d    # Rebuild and start
docker-compose logs -f          # Check logs
```

#### Performance Issues

**Slow message synchronization**
```bash
# Optimize sync performance
✓ Check platform API rate limits
✓ Reduce batch size in message.py
✓ Monitor database query performance
✓ Check network latency to platform APIs
```

**High memory usage**
```bash
# Reduce memory footprint
✓ Limit message fetch count
✓ Clear old embeddings from Qdrant
✓ Optimize database queries
✓ Check for memory leaks in logs
```

### Getting Help

- **Documentation**: Check `.docs/` folder for detailed guides
- **API Docs**: Visit `http://localhost:8000/docs` for API reference
- **Logs**: Check backend logs for detailed error messages
- **Tests**: Run tests to verify system functionality
- **Issues**: Open a GitHub issue with error logs and steps to reproduce

---

## License

Champa is open source software licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 Champa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

**Built With:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [LangChain](https://www.langchain.com/) - LLM application framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent orchestration
- [Auth0](https://auth0.com/) - Authentication platform
- [OpenAI](https://openai.com/) - AI models
- [Qdrant](https://qdrant.tech/) - Vector database
- [PostgreSQL](https://www.postgresql.org/) - Relational database

**Inspired By:**
- Modern unified inbox solutions
- AI-powered communication assistants
- Human-in-the-loop AI systems

**Special Thanks:**
- The open source community
- All contributors and testers
- Platform API providers (Google, Slack)

---

## Support

**Questions or Issues?**
- 📖 Check the [documentation](#quick-start)
- 🐛 Report bugs via GitHub Issues
- 💬 Join discussions in GitHub Discussions
- 📧 Contact: [your-email@example.com]

**Stay Updated:**
- ⭐ Star the repository
- 👀 Watch for updates
- 🔔 Follow releases

---

## Detailed Setup Guides

### Auth0 Setup Guide

### Step 1: Create Auth0 Account
1. Go to https://auth0.com and sign up (free tier available)
2. Create a new tenant (e.g., `champa-dev`)

### Step 2: Create Single Page Application
1. Go to **Applications** → **Create Application**
2. Name: `Champa Frontend`
3. Type: **Single Page Web Applications**
4. Click **Create**

### Step 3: Configure Application Settings
In your application settings:

**Application URIs:**
```
Allowed Callback URLs: http://localhost:5173/callback
Allowed Logout URLs: http://localhost:5173/login
Allowed Web Origins: http://localhost:5173
```

**Note your credentials:**
- Domain: `your-tenant.auth0.com`
- Client ID: (copy this for frontend)

### Step 4: Create API
1. Go to **Applications** → **APIs** → **Create API**
2. Name: `Champa API`
3. Identifier: `https://champa-api` (this is your audience)
4. Signing Algorithm: `RS256`
5. Enable **Offline Access** (for refresh tokens)

**Note your API credentials:**
- API Identifier: `https://champa-api` (your audience)

### Step 5: Get Client Secret (Backend)
1. Go back to your application
2. Go to **Settings** tab
3. Copy the **Client Secret** (for backend only)

### Step 6: Enable Authentication Methods

**Username/Password:**
1. Go to **Authentication** → **Database**
2. Enable **Username-Password-Authentication**
3. Configure password policy as needed

**Social Login (Optional):**
1. Go to **Authentication** → **Social**
2. Enable desired providers:
   - Google: Requires Google OAuth credentials
   - Facebook: Requires Facebook App credentials
   - Twitter: Requires Twitter App credentials
3. Configure each provider with their credentials

### Step 7: Test Configuration
1. Update your `.env` files with Auth0 credentials
2. Start the application
3. Click "Login" - you should be redirected to Auth0 Universal Login
4. Create an account or log in
5. You should be redirected back to the dashboard

## Google OAuth Setup (Gmail & Calendar)

### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create a new project (e.g., `Champa`)

### Step 2: Enable APIs
1. Go to **APIs & Services** → **Library**
2. Search and enable:
   - **Gmail API**
   - **Google Calendar API**

### Step 3: Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. User Type: **External** (for testing)
3. Fill in required fields:
   - App name: `Champa`
   - User support email: your email
   - Developer contact: your email
4. Scopes: Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`
5. Test users: Add your email for testing

### Step 4: Create OAuth Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `Champa Backend`
5. Authorized redirect URIs:
   ```
   http://localhost:8000/api/platforms/gmail/callback
   http://localhost:8000/api/platforms/calendar/callback
   ```
6. Click **Create**
7. Copy **Client ID** and **Client Secret**

### Step 5: Update Backend .env
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/platforms/gmail/callback
```

## Slack OAuth Setup

### Step 1: Create Slack App
1. Go to https://api.slack.com/apps
2. Click **Create New App** → **From scratch**
3. App Name: `Champa`
4. Workspace: Select your workspace

### Step 2: Configure OAuth & Permissions
1. Go to **OAuth & Permissions**
2. Add **Redirect URLs**:
   ```
   http://localhost:8000/api/platforms/slack/callback
   ```
3. Add **Bot Token Scopes**:
   - `channels:history` - View messages in public channels
   - `channels:read` - View basic channel info
   - `chat:write` - Send messages
   - `users:read` - View users
   - `im:history` - View direct messages
   - `im:read` - View direct message info

### Step 3: Get Credentials
1. Go to **Basic Information**
2. Copy **Client ID** and **Client Secret**

### Step 4: Update Backend .env
```bash
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
SLACK_REDIRECT_URI=http://localhost:8000/api/platforms/slack/callback
```

### Step 5: Install App to Workspace
1. Go to **Install App**
2. Click **Install to Workspace**
3. Authorize the app

## Testing

Champa includes comprehensive test coverage with property-based and integration tests.

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with detailed output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
# View coverage: open htmlcov/index.html

# Run property-based tests (100+ iterations)
pytest -m property

# Run specific test categories
pytest tests/test_auth_properties.py -v
pytest tests/test_message_normalization_properties.py -v
pytest tests/test_platform_integration_properties.py -v
pytest tests/test_api_integration.py -v
pytest tests/test_chat_agent.py -v
pytest tests/test_deep_agent_integration.py -v

# Run tests matching pattern
pytest -k "spam" -v

# Run with print statements visible
pytest -s
```

**Test Categories:**
- **Property-Based Tests**: Use Hypothesis for 100+ iterations testing edge cases
- **Integration Tests**: Test full API workflows end-to-end
- **Unit Tests**: Test individual components in isolation
- **Agent Tests**: Test LangGraph agent behavior and tool calling

### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (for development)
npm test -- --watch

# Run specific test file
npm test -- MessageWithReplies.test.tsx

# Update snapshots
npm test -- -u
```

### Manual Testing Checklist

**Authentication Flow:**
- [ ] Login with Auth0
- [ ] Social login (Google, Facebook, Twitter)
- [ ] Logout and token revocation
- [ ] Profile update
- [ ] Token refresh on expiry

**Platform Connections:**
- [ ] Connect Gmail via OAuth
- [ ] Connect Slack via OAuth
- [ ] Connect Google Calendar via OAuth
- [ ] Disconnect platforms
- [ ] Token refresh for platforms

**Message Management:**
- [ ] Fetch messages from all platforms
- [ ] View message details
- [ ] Filter by platform, priority, spam
- [ ] Search messages
- [ ] Mark as read/unread

**AI Features:**
- [ ] Message summarization
- [ ] Intent classification
- [ ] Priority scoring
- [ ] Spam detection
- [ ] Entity extraction (tasks, deadlines)
- [ ] Smart reply generation
- [ ] Reply editing and approval

**Chat Assistant:**
- [ ] Ask questions about messages
- [ ] Execute actions via chat
- [ ] View chat history
- [ ] Tool calling functionality

**Dashboard:**
- [ ] View statistics
- [ ] Priority distribution chart
- [ ] Spam analytics
- [ ] Upcoming deadlines
- [ ] Real-time updates

---

## Deployment

### Docker Deployment (Recommended)

**Development Setup:**
```bash
# Start databases only
docker-compose -f docker-compose.dev.yml up -d

# Run backend and frontend locally for hot-reload
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

**Production Setup:**
```bash
# Configure production environment variables
# Update backend/.env and frontend/.env

# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Scale backend instances
docker-compose up -d --scale backend=3

# Stop services
docker-compose down
```

### Cloud Deployment

**Database Setup:**

**PostgreSQL (Supabase):**
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Get connection string from Settings → Database
4. Update `DATABASE_URL` in backend `.env`

**Qdrant (Vector Database):**
1. Create account at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create cluster
3. Get cluster URL and API key
4. Update `QDRANT_URL` and `QDRANT_API_KEY`

**Backend Deployment Options:**
- **Railway**: Easy deployment with automatic HTTPS
- **Render**: Free tier available, auto-deploy from Git
- **Fly.io**: Global edge deployment
- **AWS ECS**: Container orchestration
- **Google Cloud Run**: Serverless containers
- **DigitalOcean App Platform**: Managed containers

**Frontend Deployment Options:**
- **Vercel**: Optimized for React, automatic deployments
- **Netlify**: Free tier with continuous deployment
- **Cloudflare Pages**: Fast global CDN
- **AWS S3 + CloudFront**: Static hosting with CDN
- **GitHub Pages**: Free static hosting

### Production Environment Variables

**Backend (`backend/.env`):**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@production-host:5432/champa
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-production-api-key
FRONTEND_URL=https://champa.yourdomain.com
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://champa-api
OPENAI_API_KEY=sk-proj-...
# Update OAuth redirect URIs to production URLs
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/api/platforms/gmail/callback
SLACK_REDIRECT_URI=https://api.yourdomain.com/api/platforms/slack/callback
```

**Frontend (`frontend/.env`):**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-production-client-id
VITE_AUTH0_AUDIENCE=https://champa-api
VITE_AUTH0_REDIRECT_URI=https://champa.yourdomain.com/callback
```

### SSL/TLS Configuration

Use a reverse proxy for HTTPS:

**Nginx Example:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Caddy Example (Automatic HTTPS):**
```
api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

### Monitoring and Logging

**Application Monitoring:**
- Use Sentry for error tracking
- Set up health check endpoints
- Monitor API response times
- Track OpenAI API usage and costs

**Infrastructure Monitoring:**
- Database connection pool metrics
- Qdrant query performance
- Memory and CPU usage
- Request rate and latency

---

## Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/champa.git
   cd champa
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd frontend && npm test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Contribution Guidelines

**Code Style:**
- Python: Follow PEP 8, use Black for formatting
- TypeScript: Follow Airbnb style guide, use Prettier
- Write descriptive commit messages
- Add comments for complex logic

**Testing Requirements:**
- Add tests for all new features
- Maintain or improve code coverage
- Property-based tests for data transformations
- Integration tests for API endpoints

**Documentation:**
- Update README for new features
- Add docstrings to functions and classes
- Update API documentation
- Include usage examples

**Pull Request Process:**
1. Ensure all tests pass
2. Update documentation
3. Add description of changes
4. Link related issues
5. Request review from maintainers

### Areas for Contribution

**High Priority:**
- [ ] Additional platform integrations (Outlook, WhatsApp)
- [ ] Mobile applications (React Native)
- [ ] Advanced analytics dashboard
- [ ] Performance optimizations
- [ ] Internationalization (i18n)

**Good First Issues:**
- [ ] UI/UX improvements
- [ ] Documentation enhancements
- [ ] Test coverage improvements
- [ ] Bug fixes
- [ ] Code refactoring

---
