# Product Overview

Champa is an intelligent unified inbox system that aggregates communications from multiple platforms (Gmail, Slack, Calendar) into a single interface. The system uses AI-powered agents to understand, summarize, prioritize, extract actionable items, and generate smart replies.

**Current Status**: Core features implemented with direct platform integrations (no third-party dependencies). Repository recently cleaned and organized for maintainability.

## Core Features

- **Unified Communication Hub**: Consolidates Gmail, Slack, and Calendar into one interface
- **AI-Powered Analysis**: Automatically summarizes messages, classifies intent, extracts tasks/deadlines, and assigns priority scores
- **Smart Reply Generation**: Creates context-aware draft responses using deep agents with user persona memory
- **Human-in-the-Loop**: All AI-generated replies require user approval before sending
- **Chat Assistant**: Interactive AI assistant for querying messages and executing actions
- **Real-time Updates**: WebSocket-based live feed updates and statistics

## Key User Workflows

1. **Authentication**: Users log in via Auth0 or username/password
2. **Platform Connection**: Users connect Gmail, Slack, and Calendar via OAuth (Composio)
3. **Message Aggregation**: System automatically fetches and normalizes messages from all platforms
4. **AI Processing**: Messages are analyzed, summarized, and enriched with actionable items
5. **Unified Dashboard**: Users view all communications in a single feed with AI insights
6. **Smart Replies**: Users request AI-generated drafts, review, edit, and approve before sending
7. **Chat Interaction**: Users query their messages and request actions via chat assistant
