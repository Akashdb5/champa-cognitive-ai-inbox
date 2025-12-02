# Project Structure

## Repository Organization

```
champa/
├── .docs/                     # Archived documentation (gitignored)
├── .kiro/                     # Kiro configuration
│   ├── hooks/                 # Agent hooks
│   ├── specs/                 # Feature specifications
│   └── steering/              # Project guidelines
├── backend/                   # FastAPI backend application
│   ├── alembic/               # Database migrations
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── platforms.py   # Platform connection endpoints
│   │   │   ├── messages.py    # Message endpoints
│   │   │   ├── replies.py     # Smart reply endpoints
│   │   │   ├── stats.py       # Statistics endpoints
│   │   │   ├── chat.py        # Chat assistant endpoints
│   │   │   └── dependencies.py # Shared dependencies
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings and environment
│   │   │   ├── security.py    # Auth0 and JWT handling
│   │   │   └── database.py    # Database connection
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── message.py
│   │   │   └── platform.py
│   │   ├── schemas/           # Pydantic validation schemas
│   │   │   ├── message.py     # NormalizedMessage, MessageAnalysis
│   │   │   ├── reply.py       # SmartReply
│   │   │   ├── user.py        # User, UserPersona
│   │   │   └── chat.py        # Chat schemas
│   │   ├── services/          # Business logic
│   │   │   ├── auth.py        # Authentication service
│   │   │   ├── message.py     # Message fetching and normalization
│   │   │   ├── ai.py          # AI Pipeline orchestration
│   │   │   ├── platform.py    # Platform integration management
│   │   │   └── reply.py       # Smart reply service
│   │   ├── integrations/      # Platform integration layer
│   │   │   ├── interfaces.py  # Abstract platform interfaces
│   │   │   ├── google/        # Google API adapters
│   │   │   │   ├── gmail.py   # Direct Gmail API integration
│   │   │   │   ├── calendar_adapter.py # Calendar integration
│   │   │   │   └── calendar_tools.py   # Calendar tools
│   │   │   └── slack/         # Slack API adapters
│   │   │       ├── slack_adapter.py # Direct Slack API integration
│   │   │       └── slack_tools.py   # Slack tools
│   │   ├── ai/                # AI Pipeline components
│   │   │   ├── agents/        # LangGraph agents
│   │   │   │   ├── deep_agent.py # Deep agent orchestrator
│   │   │   │   ├── analyzer.py   # Message analysis agent
│   │   │   │   └── chat.py       # Chat assistant agent
│   │   │   ├── chains/        # LangChain chains
│   │   │   │   ├── summarize.py
│   │   │   │   ├── classify.py
│   │   │   │   ├── extract.py
│   │   │   │   ├── prioritize.py
│   │   │   │   ├── smart_reply.py
│   │   │   │   └── spam_detection.py
│   │   │   ├── memory/        # User persona and memory
│   │   │   │   └── persona_store.py
│   │   │   ├── embeddings/    # Vector generation
│   │   │   │   └── qdrant_client.py
│   │   │   ├── config.py      # AI configuration
│   │   │   └── fallback.py    # Fallback processing
│   │   └── utils/             # Utilities
│   │       ├── retry.py       # Exponential backoff
│   │       ├── errors.py      # Error handling
│   │       ├── database.py    # Database utilities
│   │       └── token_refresh.py # OAuth token refresh
│   ├── tests/                 # Backend tests (pytest)
│   │   ├── test_auth_properties.py
│   │   ├── test_message_normalization_properties.py
│   │   ├── test_platform_integration_properties.py
│   │   ├── test_api_integration.py
│   │   ├── test_chat_agent.py
│   │   └── test_deep_agent_integration.py
│   ├── main.py                # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── pytest.ini             # Pytest configuration
│   └── alembic.ini            # Alembic configuration
│
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── MessageWithReplies.tsx
│   │   │   └── (other components)
│   │   ├── pages/             # Page components
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   └── OAuthRedirectPage.tsx
│   │   ├── contexts/          # React contexts
│   │   │   └── AuthContext.tsx
│   │   ├── hooks/             # Custom hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useMessages.ts
│   │   │   ├── useReplies.ts
│   │   │   ├── useStats.ts
│   │   │   └── usePlatforms.ts
│   │   ├── services/          # API client services
│   │   │   ├── auth.ts        # Auth API calls
│   │   │   ├── messages.ts    # Message API calls
│   │   │   ├── platforms.ts   # Platform API calls
│   │   │   ├── replies.ts     # Reply API calls
│   │   │   └── stats.ts       # Stats API calls
│   │   ├── App.tsx            # Root component
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/                   # Development scripts (gitignored)
│   └── tests/                 # Ad-hoc test scripts
├── docker-compose.yml         # Local development services
├── .gitignore                 # Git ignore rules
├── CHANGELOG.md               # Version history
├── CLEANUP_SUMMARY.md         # Repository cleanup documentation
└── README.md                  # Project documentation
```

## Key Architectural Patterns

### Backend

- **Layered Architecture**: API → Services → Models → Database
- **Interface-Based Integration**: Abstract platform interfaces with Composio adapters
- **Service Layer**: Business logic isolated from API endpoints
- **Repository Pattern**: Database access through SQLAlchemy models

### Frontend

- **Component-Based**: Reusable RetroUI components
- **Context API**: Global state for auth and WebSocket
- **Custom Hooks**: Encapsulate API calls and state logic
- **Protected Routes**: Authentication wrapper for secure pages

### AI Pipeline

- **Agent Orchestration**: LangGraph deep agents with planning and subagents
- **Chain Composition**: LangChain chains for specific analysis tasks
- **Memory Management**: LangGraph Store for user persona long-term memory
- **Human-in-the-Loop**: LangGraph interrupt mechanism for reply approval

## File Naming Conventions

- **Python**: snake_case for files and functions
- **TypeScript/React**: PascalCase for components, camelCase for utilities
- **Tests**: `test_*.py` for Python, `*.test.tsx` for React
- **Property Tests**: Tag with `# Feature: champa-unified-inbox, Property {number}: {description}`

## Database Conventions

- **Table Names**: Plural snake_case (e.g., `users`, `platform_connections`)
- **Primary Keys**: UUID with `gen_random_uuid()`
- **Timestamps**: Include `created_at` and `updated_at` where applicable
- **Foreign Keys**: Use `ON DELETE CASCADE` for dependent data
- **Indexes**: Add indexes on frequently queried fields (user_id, timestamp, thread_id)
