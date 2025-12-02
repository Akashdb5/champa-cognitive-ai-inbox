# Frontend API Services

This directory contains all API service modules for communicating with the Champa backend.

## Services

### `api.ts`
Base Axios configuration with:
- Automatic JWT token injection
- Token refresh on 401 errors
- Request/response interceptors

### `auth.ts`
Authentication services:
- `login()` - User login
- `signup()` - User registration
- `logout()` - User logout
- `getCurrentUser()` - Get current user info
- `refreshToken()` - Refresh access token

### `messages.ts`
Message management:
- `getMessages()` - Fetch messages with filters
- `getMessage()` - Get single message
- `getMessageThread()` - Get thread context
- `searchMessages()` - Semantic search

### `platforms.ts`
Platform connection management:
- `getPlatformStatus()` - Check connection status
- `connectPlatform()` - Connect Gmail/Slack/Calendar
- `disconnectPlatform()` - Disconnect platform
- `refreshPlatformToken()` - Refresh OAuth token

### `replies.ts`
Smart reply management:
- `generateSmartReply()` - Generate AI draft
- `getPendingReplies()` - Get pending drafts
- `approveReply()` - Approve and send draft
- `editReply()` - Edit draft content
- `rejectReply()` - Reject draft

### `chat.ts`
Chat assistant:
- `sendMessage()` - Send chat message
- `getChatHistory()` - Get conversation history
- `clearChatHistory()` - Clear history

### `stats.ts`
Statistics and analytics:
- `getOverviewStats()` - Dashboard overview
- `getActionableStats()` - Actionable items stats
- `getPlatformStats()` - Per-platform stats

## Usage

```typescript
import { authService } from './services/auth';
import { messageService } from './services/messages';

// Login
await authService.login({ username: 'user', password: 'pass' });

// Fetch messages
const messages = await messageService.getMessages({ limit: 50 });
```

## Hooks

Use the corresponding hooks in `src/hooks/` for React components:
- `useAuth()` - Authentication state
- `useMessages()` - Message fetching
- `usePlatforms()` - Platform connections
- `useReplies()` - Smart replies
- `useChat()` - Chat assistant
- `useStats()` - Statistics

## Environment Variables

Set `VITE_API_BASE_URL` in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```
