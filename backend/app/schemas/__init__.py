"""
Pydantic validation schemas
"""
from app.schemas.message import (
    NormalizedMessage,
    MessageAnalysis,
    MessageResponse,
    MessageFilters,
    ThreadContext,
    MessageSearchRequest,
    MessageSearchResponse,
)
from app.schemas.reply import (
    SmartReply,
    SmartReplyRequest,
    SmartReplyApproval,
    SmartReplyEdit,
    SmartReplyRejection,
    SmartReplyResponse,
)
from app.schemas.user import (
    User,
    UserCreate,
    UserPersona,
    StylePatterns,
    Contact,
    Preferences,
    UserPersonaData,
)
from app.schemas.platform import (
    PlatformConnectionResponse,
    PlatformStatus,
)
from app.schemas.auth import (
    AuthResponse,
)
from app.schemas.stats import (
    OverviewStats,
    ActionableStats,
    PlatformStats,
)
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatHistory,
)

__all__ = [
    # Message schemas
    "NormalizedMessage",
    "MessageAnalysis",
    "MessageResponse",
    "MessageFilters",
    "ThreadContext",
    "MessageSearchRequest",
    "MessageSearchResponse",
    # Reply schemas
    "SmartReply",
    "SmartReplyRequest",
    "SmartReplyApproval",
    "SmartReplyEdit",
    "SmartReplyRejection",
    "SmartReplyResponse",
    # User schemas
    "User",
    "UserCreate",
    "UserPersona",
    "StylePatterns",
    "Contact",
    "Preferences",
    "UserPersonaData",
    # Platform schemas
    "PlatformConnectionResponse",
    "PlatformStatus",
    # Auth schemas
    "AuthResponse",
    # Stats schemas
    "OverviewStats",
    "ActionableStats",
    "PlatformStats",
    # Chat schemas
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatHistory",
]
