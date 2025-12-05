"""
Champa Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, platforms, replies, chat, messages, stats

app = FastAPI(
    title="Champa API",
    description="Intelligent unified inbox system",
    version="0.1.0"
)

# Configure CORS
from app.core.config import settings

allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
    "http://localhost",       # Docker frontend (port 80)
    "http://localhost:80",    # Docker frontend (explicit port)
    "https://champa-cognitive-ai-inbox-frontend.vercel.app",  # Production frontend
]

# Add frontend URL from settings if it's not localhost
if settings.FRONTEND_URL and "localhost" not in settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (they already have /api prefix in their definitions)
app.include_router(auth.router)
app.include_router(platforms.router)
app.include_router(messages.router)
app.include_router(replies.router)
app.include_router(stats.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Champa API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
