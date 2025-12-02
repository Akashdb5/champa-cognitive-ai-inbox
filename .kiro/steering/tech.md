# Technology Stack

## Backend

- **Framework**: FastAPI (Python 3.11+)
- **Authentication**: Auth0 with JWT tokens
- **ORM**: SQLAlchemy with Alembic migrations
- **Validation**: Pydantic models
- **AI/ML**: 
  - LangChain for LLM orchestration
  - LangGraph for agent workflows and deep agents
  - OpenAI GPT-4 (or configurable LLM)
  - Sentence Transformers for embeddings

## Frontend

- **Framework**: React 18+ with TypeScript
- **UI Library**: RetroUI components (all UI elements must use RetroUI)
- **Routing**: React Router
- **HTTP Client**: Axios
- **Real-time**: WebSocket for live updates

## Data Storage

- **Relational Database**: PostgreSQL 15+ (messages, users, analysis, personas)
- **Vector Database**: Qdrant (message embeddings for semantic search)

## Platform Integrations

- **Gmail Integration**: Direct Google OAuth 2.0 with Gmail API
- **Slack Integration**: Direct Slack OAuth 2.0 with Slack SDK
- **Calendar Integration**: Direct Google OAuth 2.0 with Google Calendar API
- **Architecture**: Interface-based design with abstract platform interfaces and direct API adapters
- **No Third-Party Dependencies**: All integrations use official platform SDKs directly

## Development Tools

- **Backend Testing**: pytest with Hypothesis for property-based testing
- **Frontend Testing**: Jest with React Testing Library
- **Containerization**: Docker and docker-compose for local development

## Common Commands

### Backend

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run development server
uvicorn main:app --reload

# Run tests
pytest

# Run property-based tests
pytest -m property
```

### Frontend

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

### Docker

```bash
# Start all services (PostgreSQL, Qdrant, backend, frontend)
docker-compose up

# Start only databases
docker-compose up postgres qdrant

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up --build
```

## Key Technical Constraints

- All UI components must use RetroUI library
- Platform integrations must go through abstract interfaces (not direct Composio calls)
- All AI-generated email replies require human approval before sending
- Property-based tests must run minimum 100 iterations
- Message embeddings must be stored in Qdrant with PostgreSQL message IDs
