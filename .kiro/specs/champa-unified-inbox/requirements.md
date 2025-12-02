# Requirements Document

## Introduction

Champa is an intelligent unified inbox system that aggregates communication from multiple platforms (Gmail, Slack, Calendar) into a single interface. The system uses AI-powered agents to understand, summarize, prioritize, extract actionable items, and generate smart replies. It provides users with a centralized dashboard to manage all their communications efficiently, reducing context switching and information overload.

## Glossary

- **Champa System**: The complete unified inbox application including frontend, backend, and AI processing pipeline
- **Message**: Any communication item from Gmail, Slack, or Calendar (email, chat message, or calendar event)
- **Normalized Message**: A message converted to a unified internal format regardless of source platform
- **AI Pipeline**: The LangChain-based processing system that analyzes messages
- **Deep Agent**: A LangGraph-based agent with planning, memory, and subagent capabilities
- **User Persona**: Long-term memory profile containing user preferences, communication style, and patterns
- **Smart Reply**: An AI-generated draft response based on message context and user persona
- **Actionable Item**: A task or deadline extracted from messages
- **Platform Connection**: OAuth-authenticated integration with Gmail, Slack, or Calendar using official platform SDKs
- **Thread Context**: Full conversation history for a message or discussion
- **Human-in-the-Loop**: Workflow requiring user approval before executing sensitive actions

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate securely with the system, so that I can access my unified inbox with proper authorization.

#### Acceptance Criteria

1. WHEN a user visits the login page THEN the Champa System SHALL display authentication options including username/password and Auth0
2. WHEN a user provides valid credentials THEN the Champa System SHALL authenticate the user and create a session
3. WHEN a user provides invalid credentials THEN the Champa System SHALL reject authentication and display an error message
4. WHEN an authenticated user accesses protected routes THEN the Champa System SHALL verify the session token before granting access
5. WHEN a user logs out THEN the Champa System SHALL invalidate the session and redirect to the login page

### Requirement 2

**User Story:** As a user, I want to connect my Gmail, Slack, and Calendar accounts, so that Champa can aggregate my communications from these platforms.

#### Acceptance Criteria

1. WHEN a user navigates to the profile page THEN the Champa System SHALL display available platform connections with their current status
2. WHEN a user initiates a platform connection THEN the Champa System SHALL handle OAuth authentication securely using the platform's official SDK
3. WHEN OAuth authentication succeeds THEN the Champa System SHALL store the connection credentials and mark the platform as connected
4. WHEN a user disconnects a platform THEN the Champa System SHALL revoke access tokens and remove stored credentials
5. WHEN a platform connection fails THEN the Champa System SHALL display an error message with troubleshooting guidance

### Requirement 3

**User Story:** As a user, I want the system to automatically fetch messages from my connected platforms, so that I have a unified view of all communications.

#### Acceptance Criteria

1. WHEN a platform connection is active THEN the Champa System SHALL poll for new messages at regular intervals
2. WHEN new messages are detected THEN the Champa System SHALL fetch the complete message content including metadata
3. WHEN fetching messages from Gmail THEN the Champa System SHALL retrieve email subject, body, sender, recipients, and timestamp
4. WHEN fetching messages from Slack THEN the Champa System SHALL retrieve message text, channel, sender, and timestamp
5. WHEN fetching calendar events THEN the Champa System SHALL retrieve event title, description, participants, start time, and end time

### Requirement 4

**User Story:** As a developer, I want all messages normalized to a unified format, so that downstream processing is consistent regardless of source platform.

#### Acceptance Criteria

1. WHEN a message is fetched from any platform THEN the Champa System SHALL convert it to a normalized message format
2. WHEN normalizing a message THEN the Champa System SHALL preserve the source platform identifier
3. WHEN normalizing a message THEN the Champa System SHALL extract common fields including sender, content, timestamp, and unique identifier
4. WHEN normalizing a message THEN the Champa System SHALL store platform-specific metadata in a structured format
5. WHEN a normalized message is created THEN the Champa System SHALL validate the format before storage

### Requirement 5

**User Story:** As a user, I want the system to automatically analyze my messages using AI, so that I can quickly understand what's important without reading everything.

#### Acceptance Criteria

1. WHEN a normalized message is stored THEN the Champa System SHALL pass it through the AI Pipeline for analysis
2. WHEN the AI Pipeline processes a message THEN the Champa System SHALL generate a concise summary
3. WHEN the AI Pipeline processes a message THEN the Champa System SHALL classify the message intent
4. WHEN the AI Pipeline processes a message THEN the Champa System SHALL extract actionable items including tasks and deadlines
5. WHEN the AI Pipeline processes a message THEN the Champa System SHALL assign a priority score based on content and context

### Requirement 6

**User Story:** As a user, I want the system to remember my communication preferences and patterns, so that AI-generated responses match my style.

#### Acceptance Criteria

1. WHEN a user interacts with the Champa System THEN the Deep Agent SHALL store observations in the User Persona
2. WHEN storing User Persona data THEN the Champa System SHALL capture communication style patterns
3. WHEN storing User Persona data THEN the Champa System SHALL identify recurring contacts and their relationships
4. WHEN storing User Persona data THEN the Champa System SHALL record user preferences for message handling
5. WHEN generating responses THEN the Deep Agent SHALL retrieve relevant User Persona data to inform the output

### Requirement 7

**User Story:** As a user, I want the system to generate draft replies for my emails, so that I can respond quickly without starting from scratch.

#### Acceptance Criteria

1. WHEN a user requests a smart reply for an email THEN the Champa System SHALL fetch the complete thread context
2. WHEN generating a smart reply THEN the Deep Agent SHALL retrieve relevant User Persona data
3. WHEN generating a smart reply THEN the Deep Agent SHALL create a step-by-step plan using LangGraph
4. WHEN generating a smart reply THEN the Deep Agent SHALL produce a context-aware draft response
5. WHEN a smart reply is generated THEN the Champa System SHALL present it to the user for approval before sending

### Requirement 8

**User Story:** As a user, I want to review and approve AI-generated email drafts before they are sent, so that I maintain control over my communications.

#### Acceptance Criteria

1. WHEN a smart reply is generated THEN the Champa System SHALL display it in the approval interface
2. WHEN reviewing a draft THEN the user SHALL be able to approve, edit, or reject the response
3. WHEN a user approves a draft THEN the Champa System SHALL send the email via the connected Gmail account
4. WHEN a user edits a draft THEN the Champa System SHALL update the content and present it for final approval
5. WHEN a user rejects a draft THEN the Champa System SHALL discard it and allow the user to request a new draft

### Requirement 9

**User Story:** As a user, I want to see all my messages in a unified feed on the home page, so that I can quickly scan what's new across all platforms.

#### Acceptance Criteria

1. WHEN a user navigates to the home page THEN the Champa System SHALL display a unified feed of messages
2. WHEN displaying messages THEN the Champa System SHALL show the source platform indicator for each message
3. WHEN displaying messages THEN the Champa System SHALL show the AI-generated summary
4. WHEN displaying messages THEN the Champa System SHALL show the priority level
5. WHEN displaying messages THEN the Champa System SHALL show extracted actionable items with deadline indicators

### Requirement 10

**User Story:** As a user, I want to see statistics about my communications on the home page, so that I can understand my message volume and pending actions.

#### Acceptance Criteria

1. WHEN a user navigates to the home page THEN the Champa System SHALL display the count of new messages received
2. WHEN displaying statistics THEN the Champa System SHALL show the number of pending draft approvals
3. WHEN displaying statistics THEN the Champa System SHALL show the count of actionable items with deadlines today
4. WHEN displaying statistics THEN the Champa System SHALL update counts in real-time as messages are processed
5. WHEN a user clicks on a statistic THEN the Champa System SHALL filter the message feed to show relevant items

### Requirement 11

**User Story:** As a user, I want to interact with an AI assistant via chat, so that I can ask questions about my messages or request actions.

#### Acceptance Criteria

1. WHEN a user navigates to the chat page THEN the Champa System SHALL display a full-page chat interface
2. WHEN a user sends a message to the assistant THEN the Deep Agent SHALL process the query using the AI Pipeline
3. WHEN the assistant processes a query THEN the Deep Agent SHALL access message history and User Persona data
4. WHEN the assistant responds THEN the Champa System SHALL display the response in the chat interface
5. WHEN a user requests an action THEN the Deep Agent SHALL execute it and confirm completion

### Requirement 12

**User Story:** As a developer, I want all message data and metadata stored in PostgreSQL, so that we have reliable relational data persistence.

#### Acceptance Criteria

1. WHEN a normalized message is created THEN the Champa System SHALL store it in the PostgreSQL database
2. WHEN storing message data THEN the Champa System SHALL include all normalized fields and platform-specific metadata
3. WHEN storing thread context THEN the Champa System SHALL maintain relationships between related messages
4. WHEN storing user interactions THEN the Champa System SHALL record actions taken on messages
5. WHEN querying message data THEN the Champa System SHALL use indexed fields for efficient retrieval

### Requirement 13

**User Story:** As a developer, I want message embeddings stored in Qdrant, so that we can perform semantic search over message content.

#### Acceptance Criteria

1. WHEN a message is analyzed by the AI Pipeline THEN the Champa System SHALL generate embeddings for the content
2. WHEN embeddings are generated THEN the Champa System SHALL store them in the Qdrant vector database
3. WHEN storing embeddings THEN the Champa System SHALL associate them with the corresponding message identifier
4. WHEN performing semantic search THEN the Champa System SHALL query Qdrant using query embeddings
5. WHEN semantic search results are returned THEN the Champa System SHALL retrieve full message data from PostgreSQL

### Requirement 14

**User Story:** As a developer, I want the system architecture to use interface-based design for platform integrations, so that we can easily add new platforms or switch implementations.

#### Acceptance Criteria

1. WHEN implementing platform integrations THEN the Champa System SHALL define abstract interfaces for each platform type
2. WHEN integrating a platform THEN the Champa System SHALL implement the interfaces using direct API adapters with official SDKs
3. WHEN a platform interface is called THEN the Champa System SHALL route through the abstraction layer
4. WHEN switching implementations THEN the developer SHALL only need to implement new adapters without changing core logic
5. WHEN adding a new platform THEN the developer SHALL implement the platform interface without modifying existing code

### Requirement 15

**User Story:** As a developer, I want the AI Pipeline built using LangChain and LangGraph, so that we leverage proven frameworks for agent orchestration.

#### Acceptance Criteria

1. WHEN processing messages THEN the Champa System SHALL use LangChain components for model interactions
2. WHEN orchestrating agent workflows THEN the Champa System SHALL use LangGraph for state management
3. WHEN implementing deep agents THEN the Champa System SHALL use LangGraph's planning and subagent capabilities
4. WHEN managing long-term memory THEN the Champa System SHALL use LangGraph's store abstraction
5. WHEN implementing human-in-the-loop workflows THEN the Champa System SHALL use LangGraph's interrupt mechanism

### Requirement 16

**User Story:** As a user, I want the system to handle errors gracefully, so that temporary failures don't disrupt my experience.

#### Acceptance Criteria

1. WHEN a platform API call fails THEN the Champa System SHALL retry with exponential backoff
2. WHEN retries are exhausted THEN the Champa System SHALL log the error and notify the user
3. WHEN an AI Pipeline error occurs THEN the Champa System SHALL fall back to basic processing without AI enhancements
4. WHEN a database operation fails THEN the Champa System SHALL roll back transactions and preserve data consistency
5. WHEN an OAuth token expires THEN the Champa System SHALL prompt the user to re-authenticate

### Requirement 17

**User Story:** As a user, I want the frontend built with RetroUI components, so that I have a visually distinctive and cohesive interface.

#### Acceptance Criteria

1. WHEN rendering any page THEN the Champa System SHALL use RetroUI components for all UI elements
2. WHEN displaying the login page THEN the Champa System SHALL use RetroUI form components
3. WHEN displaying the home page THEN the Champa System SHALL use RetroUI card and list components
4. WHEN displaying the profile page THEN the Champa System SHALL use RetroUI button and toggle components
5. WHEN displaying the chat page THEN the Champa System SHALL use RetroUI chat interface components
