# Champa - Intelligent Unified Inbox

Champa is an intelligent unified inbox system that aggregates communications from multiple platforms (Gmail, Slack, Calendar) into a single interface with AI-powered analysis and response generation.

## Features

- **Unified Communication Hub**: Consolidates Gmail, Slack, and Calendar into one interface
- **AI-Powered Analysis**: Automatically summarizes messages, classifies intent, extracts tasks/deadlines, and assigns priority scores
- **Spam Detection**: Intelligent spam filtering with automatic unsubscribe link extraction
- **Priority Intelligence**: Smart priority scoring (high/medium/low) for message triage
- **Smart Reply Generation**: Creates context-aware draft responses using deep agents with user persona memory
- **Human-in-the-Loop**: All AI-generated replies require user approval before sending
- **Chat Assistant**: Interactive AI assistant for querying messages and executing actions
- **Enhanced Dashboard**: Visual statistics with priority distribution, spam analytics, and actionable items
- **Real-time Updates**: WebSocket-based live feed updates and statistics

## Technology Stack

### Backend
- FastAPI (Python 3.11+)
- **Auth0 for authentication** (JWT tokens, social login, Universal Login)
- SQLAlchemy + PostgreSQL
- LangChain + LangGraph for AI agents
- OpenAI GPT-4 for AI analysis
- Qdrant for vector storage
- Direct platform integrations (Google APIs, Slack SDK)

### Frontend
- React 18+ with TypeScript
- **Auth0 React SDK** (`@auth0/auth0-react`)
- RetroUI component library (brutalist design)
- React Router for navigation
- Axios for API calls
- Recharts for data visualization

## Recent Updates

### December 2024 - Major Enhancements

**🔐 Auth0 Exclusive Authentication**
- Migrated to Auth0-only authentication (removed custom username/password)
- Universal Login with social providers (Google, Facebook, Twitter)
- Enhanced security with MFA support
- Automatic user sync between Auth0 and database

**🛡️ AI Analysis Pipeline**
- Intelligent spam detection with 4 spam types (promotional, newsletter, marketing, phishing)
- Automatic unsubscribe link extraction (RFC 2369 + content parsing)
- Priority scoring system (high/medium/low)
- Intent classification (7 categories)
- Task and deadline extraction

**📊 Enhanced Dashboard**
- Visual statistics with priority distribution pie chart
- Spam analytics with type breakdown
- Upcoming deadlines widget
- One-click unsubscribe from spam
- RetroUI design throughout

**🔌 Direct Platform Integrations**
- Removed Composio dependency
- Direct Google OAuth for Gmail and Calendar
- Direct Slack OAuth integration
- Official platform SDKs only

**🧪 Testing & Quality**
- Property-based testing with Hypothesis
- Integration tests for all major features
- 100+ test iterations for property tests
- Comprehensive API test coverage

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- **Auth0 account** (free tier available at https://auth0.com)
- Google Cloud project with Gmail API and Calendar API enabled
- Slack app credentials (for Slack integration)
- OpenAI API key (for AI features)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd champa
   ```

2. **Start databases with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   
   Note: Docker Compose uses `backend/.env` and `frontend/.env` for environment variables.

3. **Configure Auth0** (see detailed Auth0 Setup Guide section below)
   
   Quick checklist:
   - ✅ Create Auth0 account at https://auth0.com
   - ✅ Create a Single Page Application
   - ✅ Create an API (identifier will be your audience)
   - ✅ Configure callback URLs: `http://localhost:5173/callback`
   - ✅ Configure logout URLs: `http://localhost:5173/login`
   - ✅ Configure web origins: `http://localhost:5173`
   - ✅ Enable Username-Password-Authentication database
   - ✅ (Optional) Enable social connections (Google, Facebook, etc.)
   - ✅ Note your Domain, Client ID, Client Secret, and API Audience

4. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your credentials (see Environment Variables section below)
   
   # Run database migrations
   alembic upgrade head
   
   # Start the backend server
   uvicorn main:app --reload
   ```

5. **Set up Google OAuth** (for Gmail & Calendar - see detailed Google OAuth Setup section below)
   
   Quick checklist:
   - ✅ Create Google Cloud project
   - ✅ Enable Gmail API and Calendar API
   - ✅ Configure OAuth consent screen
   - ✅ Create OAuth credentials (Web application)
   - ✅ Add redirect URI: `http://localhost:8000/api/platforms/gmail/callback`
   - ✅ Copy Client ID and Client Secret to `backend/.env`

6. **Set up frontend**
   ```bash
   cd frontend
   npm install
   
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your Auth0 credentials (see Environment Variables section below)
   
   # Start the development server
   npm run dev
   ```

## Environment Variables

### Backend (`backend/.env`)

```bash
# Database
DATABASE_URL=postgresql://champa:champa_password@localhost:5432/champa

# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://champa-api
AUTH0_CLIENT_ID=your-backend-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional for local, required for Qdrant Cloud

# Google OAuth (Gmail & Calendar)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/platforms/gmail/callback

# Slack OAuth
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
SLACK_REDIRECT_URI=http://localhost:8000/api/platforms/slack/callback

# Application
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

### Frontend (`frontend/.env`)

```bash
# API
VITE_API_BASE_URL=http://localhost:8000

# Auth0
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-frontend-client-id
VITE_AUTH0_AUDIENCE=https://champa-api
VITE_AUTH0_REDIRECT_URI=http://localhost:5173/callback
```

**Note**: Never commit `.env` files to version control. Use `.env.example` as a template.

7. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   
   **First time login**: Click "Login with Email" or a social provider button to authenticate via Auth0 Universal Login.

## Key API Endpoints

### Authentication
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - Logout and revoke tokens
- `PATCH /api/auth/profile` - Update user profile

### Messages
- `GET /api/messages` - List messages with filters (platform, priority, spam)
- `GET /api/messages/{id}` - Get message details
- `GET /api/messages/{id}/analysis` - Get AI analysis
- `POST /api/messages/sync` - Trigger message sync

### Statistics
- `GET /api/stats/overview` - Dashboard overview stats
- `GET /api/stats/spam` - Spam detection statistics
- `GET /api/stats/priority-distribution` - Priority breakdown
- `GET /api/stats/actionables` - Actionable items stats

### Smart Replies
- `POST /api/replies/generate` - Generate smart reply draft
- `GET /api/replies/{id}` - Get reply details
- `PATCH /api/replies/{id}` - Edit reply draft
- `POST /api/replies/{id}/approve` - Approve and send reply

### Platform Connections
- `GET /api/platforms` - List connected platforms
- `GET /api/platforms/{platform}/auth-url` - Get OAuth URL
- `GET /api/platforms/{platform}/callback` - OAuth callback
- `DELETE /api/platforms/{platform}` - Disconnect platform

### Chat Assistant
- `POST /api/chat` - Send message to AI assistant
- `GET /api/chat/history` - Get chat history

See full API documentation at http://localhost:8000/docs

## Project Structure

```
champa/
├── .docs/                    # Documentation (gitignored)
├── .kiro/                    # Kiro AI configuration
│   ├── specs/                # Feature specifications
│   └── steering/             # Project guidelines
├── backend/                  # FastAPI backend
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/              # API endpoints (auth, messages, platforms, etc.)
│   │   ├── core/             # Configuration and security (Auth0)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic layer
│   │   ├── integrations/     # Platform adapters (Gmail, Slack, Calendar)
│   │   ├── ai/               # AI Pipeline
│   │   │   ├── agents/       # LangGraph agents (deep agent, chat, analyzer)
│   │   │   ├── chains/       # LangChain chains (spam, priority, etc.)
│   │   │   ├── memory/       # User persona store
│   │   │   └── embeddings/   # Qdrant vector client
│   │   └── utils/            # Utilities (retry, errors, token refresh)
│   ├── tests/                # Pytest tests (property-based + integration)
│   ├── main.py               # FastAPI app entry point
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components (RetroUI)
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts (Auth0)
│   │   ├── hooks/            # Custom hooks (useMessages, useStats, etc.)
│   │   ├── services/         # API client services
│   │   └── lib/              # Utilities
│   ├── package.json
│   └── vite.config.ts
├── scripts/                  # Development scripts (gitignored)
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose (local DBs)
└── README.md
```

## Development

### Backend Commands

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run development server
uvicorn main:app --reload

# Run tests
pytest

# Run property-based tests
pytest -m property

# Run specific test file
pytest tests/test_spam_detection.py -v

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Commands

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint
```

### Docker Commands

```bash
# Start all services (production)
docker-compose up -d

# Start only databases (development)
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild containers
docker-compose up --build

# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v
```

## Troubleshooting

### Auth0 Issues

**"Could not validate credentials"**
- Verify `AUTH0_DOMAIN` and `AUTH0_API_AUDIENCE` match in frontend and backend
- Check that token is being sent in `Authorization: Bearer <token>` header
- Ensure Auth0 API audience is configured correctly

**Redirect loop on login**
- Check callback URL in Auth0 dashboard matches `VITE_AUTH0_REDIRECT_URI`
- Clear browser cache and localStorage
- Verify Auth0 application settings

**"Auth0 configuration is missing"**
- Ensure all `VITE_AUTH0_*` variables are set in `frontend/.env`
- Restart development server after changing `.env`

### Platform Connection Issues

**Gmail/Calendar connection fails**
- Verify Google OAuth credentials in Google Cloud Console
- Check redirect URI matches: `http://localhost:8000/api/platforms/gmail/callback`
- Ensure Gmail API and Calendar API are enabled
- Check that scopes are correct in OAuth consent screen

**Slack connection fails**
- Verify Slack app credentials
- Check redirect URI in Slack app settings
- Ensure required scopes are added to Slack app

### Database Issues

**Migration fails**
- Check database connection string in `backend/.env`
- Ensure PostgreSQL is running: `docker-compose ps`
- Try rolling back: `alembic downgrade -1`
- Check migration file for errors

**"relation does not exist" error**
- Run migrations: `alembic upgrade head`
- Check that all migrations are applied: `alembic current`

### AI Pipeline Issues

**"OpenAI API key not found"**
- Set `OPENAI_API_KEY` in `backend/.env`
- Restart backend server

**Spam detection not working**
- Check that messages have been analyzed
- Verify AI analysis is running: check logs
- Test with: `pytest tests/test_spam_detection.py -v`

**Qdrant connection fails**
- Ensure Qdrant is running: `docker-compose ps`
- Check `QDRANT_URL` in `backend/.env`
- Verify Qdrant API key if using Qdrant Cloud

### General Issues

**Port already in use**
- Backend (8000): `lsof -ti:8000 | xargs kill -9` (Mac/Linux)
- Frontend (5173): `lsof -ti:5173 | xargs kill -9` (Mac/Linux)
- On Windows: Use Task Manager to kill process

**Module not found errors**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

**CORS errors**
- Check `FRONTEND_URL` in `backend/.env`
- Verify CORS settings in `backend/main.py`

For more help, check the documentation in `.docs/` or open an issue.

## Auth0 Setup Guide

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

## Docker Deployment

### Using Docker Compose (Recommended)

**For Development (Local Databases):**
```bash
# Start PostgreSQL and Qdrant locally
docker-compose -f docker-compose.dev.yml up -d

# Run backend and frontend locally
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

**For Production (Cloud Databases):**
```bash
# Update .env with cloud database URLs
# - Supabase for PostgreSQL
# - Qdrant Cloud for vector storage

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Database Setup

**Supabase (PostgreSQL):**
1. Go to https://supabase.com
2. Create a new project
3. Copy connection string from Settings → Database
4. Update `DATABASE_URL` in backend `.env`

**Qdrant Cloud:**
1. Go to https://cloud.qdrant.io
2. Create a cluster
3. Copy cluster URL and API key
4. Update `QDRANT_URL` and `QDRANT_API_KEY` in backend `.env`

## Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run property-based tests
pytest -m property

# Run specific test file
pytest tests/test_spam_detection.py -v

# Run integration tests
pytest tests/test_api_integration.py -v
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch
```

## Production Deployment

### Environment Variables for Production

**Backend:**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/db
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
FRONTEND_URL=https://your-domain.com
AUTH0_DOMAIN=your-tenant.auth0.com
# ... other variables
```

**Frontend:**
```bash
VITE_API_BASE_URL=https://api.your-domain.com
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_REDIRECT_URI=https://your-domain.com/callback
# ... other variables
```

### SSL/TLS Setup
Use a reverse proxy (nginx, Caddy, or Traefik) with Let's Encrypt for SSL certificates.

### Scaling
```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest` and `npm test`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check the Troubleshooting section above
- Review environment variables configuration
- Verify all services are running: `docker-compose ps`
- Check logs: `docker-compose logs -f backend`


git remote add origin https://github.com/Akashdb5/champa-cognitive-ai-inbox.git
git branch -M main
git push -u origin main