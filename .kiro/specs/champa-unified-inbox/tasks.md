# Implementation Plan

- [x] 1. Set up project structure and development environment





  - Create backend directory with FastAPI project structure
  - Create frontend directory with React + TypeScript + Vite setup
  - Configure Python virtual environment and install core dependencies (FastAPI, SQLAlchemy, LangChain, LangGraph)
  - Configure Node.js project and install core dependencies (React, RetroUI, Axios)
  - Set up environment variable management (.env files)
  - Create docker-compose.yml for PostgreSQL and Qdrant local development
  - _Requirements: All_

- [x] 2. Implement database schema and models




  - [x] 2.1 Create PostgreSQL database schema


    - Write Alembic migration for users table
    - Write Alembic migration for platform_connections table
    - Write Alembic migration for messages table with indexes
    - Write Alembic migration for message_analysis table
    - Write Alembic migration for actionable_items table
    - Write Alembic migration for smart_replies table
    - Write Alembic migration for user_persona table
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [x] 2.2 Create SQLAlchemy ORM models


    - Implement User model with relationships
    - Implement PlatformConnection model
    - Implement Message model with thread relationships
    - Implement MessageAnalysis model
    - Implement ActionableItem model
    - Implement SmartReply model
    - Implement UserPersona model
    - _Requirements: 12.1, 12.2, 12.3_
  

  - [x] 2.3 Create Pydantic schemas for API validation

    - Define NormalizedMessage schema
    - Define MessageAnalysis schema
    - Define SmartReply schema
    - Define UserPersona schema
    - Define API request/response schemas
    - _Requirements: 4.5_
  
  - [x] 2.4 Write property test for message normalization


    - **Property 12: All messages are normalized**
    - **Property 13: Normalization preserves platform identifier**
    - **Property 14: Normalization extracts common fields**
    - **Property 15: Normalization preserves metadata**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [x] 3. Implement authentication system




  - [x] 3.1 Set up Auth0 integration


    - Configure Auth0 tenant and application
    - Implement Auth0 token verification middleware
    - Create authentication endpoints (login, logout, token refresh)
    - Implement session management
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [x] 3.2 Implement protected route middleware


    - Create JWT token verification decorator
    - Implement user context extraction from token
    - Add authentication to all protected endpoints
    - _Requirements: 1.4_
  
  - [x] 3.3 Write property tests for authentication


    - **Property 1: Valid credentials create sessions**
    - **Property 2: Invalid credentials are rejected**
    - **Property 3: Protected routes require valid tokens**
    - **Property 4: Logout invalidates sessions**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**
-

- [x] 4. Implement platform integration layer with abstraction



  - [x] 4.1 Define platform interface abstractions


    - Create PlatformInterface abstract base class
    - Define methods for connect, disconnect, fetch_messages, send_message
    - Create platform-specific data models
    - _Requirements: 14.1, 14.3_
  
  - [x] 4.2 Implement direct API adapters


    - Create GoogleGmailAdapter implementing PlatformInterface using Google SDK
    - Create SlackAdapter implementing PlatformInterface using Slack SDK
    - Create GoogleCalendarAdapter implementing PlatformInterface using Google SDK
    - Implement OAuth flow handling with official SDKs
    - _Requirements: 2.2, 2.3, 14.2, 14.3_
  
  - [x] 4.3 Implement platform connection management


    - Create endpoints for initiating platform connections
    - Create endpoints for disconnecting platforms
    - Implement OAuth callback handling
    - Store and manage access tokens securely
    - _Requirements: 2.1, 2.3, 2.4_
  
  - [x] 4.4 Write property tests for platform integration


    - **Property 5: OAuth success stores credentials**
    - **Property 6: Disconnect removes credentials**
    - **Property 7: Connection failures show errors**
    - **Property 54: Platform calls use abstraction**
    - **Validates: Requirements 2.3, 2.4, 2.5, 14.3**

- [x] 5. Implement message fetching and normalization





  - [x] 5.1 Create message fetching service


    - Implement polling mechanism for connected platforms
    - Create fetch_messages method for each platform adapter
    - Handle pagination for large message volumes
    - _Requirements: 3.1, 3.2_
  
  - [x] 5.2 Implement message normalization

    - Create normalize_message function for Gmail messages
    - Create normalize_message function for Slack messages
    - Create normalize_message function for Calendar events
    - Implement validation for normalized messages
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 5.3 Implement message storage



    - Create store_message method in MessageService
    - Implement thread relationship tracking
    - Handle duplicate message detection
    - _Requirements: 12.1, 12.2, 12.3_
  

- [ ] 6. Checkpoint - Ensure all tests pass




  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement AI Pipeline with LangChain and LangGraph





  - [x] 7.1 Set up LangChain components


    - Configure LLM client (OpenAI or alternative)
    - Set up embedding model for vector generation
    - Create prompt templates for message analysis
    - _Requirements: 15.1_
  
  - [x] 7.2 Implement message analysis agent


    - Create summarization chain
    - Create intent classification chain
    - Create task extraction chain
    - Create deadline detection chain
    - Create priority scoring chain
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  
  - [x] 7.3 Integrate Qdrant for vector storage

    - Set up Qdrant client and collection
    - Implement embedding generation and storage
    - Implement semantic search functionality
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [x] 7.4 Create AI service orchestration


    - Implement analyze_message method that calls all analysis chains
    - Store analysis results in database
    - Store embeddings in Qdrant
    - Link embeddings to message IDs
    - _Requirements: 5.1, 13.1, 13.2, 13.3_
  

- [-] 8. Implement Deep Agent with LangGraph for smart replies


  - [x] 8.1 Set up LangGraph deep agent


    - Create deep agent using create_deep_agent
    - Configure planning middleware
    - Configure filesystem middleware for context storage
    - Configure subagent middleware
    - _Requirements: 15.2, 15.3_
  
  - [x] 8.2 Implement user persona memory system


    - Set up LangGraph Store for long-term memory
    - Create methods to store observations
    - Create methods to retrieve style patterns
    - Create methods to retrieve contact relationships
    - Create methods to retrieve preferences
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 15.4_
  
  - [x] 8.3 Implement smart reply generation workflow


    - Create fetch_thread_context method
    - Create retrieve_persona method
    - Create reply planning agent
    - Create draft generation agent
    - Implement platform-specific formatting
    - _Requirements: 7.1, 7.2, 7.4_
  
  - [x] 8.4 Implement human-in-the-loop for reply approval



    - Set up LangGraph interrupt mechanism
    - Create approval workflow with approve/edit/reject options
    - Implement draft storage with pending status
    - Implement email sending on approval
    - _Requirements: 7.5, 8.1, 8.3, 8.4, 8.5, 15.5_
  

- [x] 9. Implement chat assistant with Deep Agent




  - [x] 9.1 Create chat processing agent


    - Implement query processing with AI Pipeline
    - Implement message history access
    - Implement persona data access
    - Create response generation chain
    - _Requirements: 11.2, 11.3_
  
  - [x] 9.2 Implement action execution


    - Create action parser for user requests
    - Implement action execution handlers
    - Implement confirmation responses
    - _Requirements: 11.5_
  

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement error handling and resilience




  - [x] 11.1 Implement retry logic with exponential backoff


    - Create retry decorator for platform API calls
    - Implement exponential backoff calculation
    - Add logging for retry attempts
    - _Requirements: 16.1_
  
  - [x] 11.2 Implement error notification system


    - Create user notification service
    - Implement error logging
    - Create error notification endpoints
    - _Requirements: 16.2_
  
  - [x] 11.3 Implement AI Pipeline fallback


    - Create basic text processing fallback
    - Detect AI Pipeline errors
    - Switch to fallback on error
    - _Requirements: 16.3_
  
  - [x] 11.4 Implement database transaction handling


    - Add transaction rollback on errors
    - Implement data consistency checks
    - Add transaction logging
    - _Requirements: 16.4_
  
  - [x] 11.5 Implement OAuth token refresh


    - Detect token expiration
    - Implement automatic token refresh
    - Prompt user for re-authentication when refresh fails
    - _Requirements: 16.5_
  

- [x] 12. Implement backend API endpoints





  - [x] 12.1 Create authentication endpoints

    - POST /api/auth/login
    - POST /api/auth/logout
    - POST /api/auth/refresh
    - GET /api/auth/me
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [x] 12.2 Create platform connection endpoints

    - GET /api/platforms
    - POST /api/platforms/{platform}/connect
    - DELETE /api/platforms/{platform}/disconnect
    - GET /api/platforms/{platform}/callback
    - _Requirements: 2.1, 2.3, 2.4_
  
  - [x] 12.3 Create message endpoints


    - GET /api/messages
    - GET /api/messages/{id}
    - GET /api/messages/{id}/thread
    - POST /api/messages/search
    - _Requirements: 9.1, 12.5_
  
  - [x] 12.4 Create smart reply endpoints

    - POST /api/messages/{id}/reply
    - GET /api/replies/pending
    - PUT /api/replies/{id}/approve
    - PUT /api/replies/{id}/edit
    - PUT /api/replies/{id}/reject
    - _Requirements: 7.5, 8.1, 8.3, 8.4, 8.5_
  
  - [x] 12.5 Create statistics endpoints


    - GET /api/stats/overview
    - GET /api/stats/actionables
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [x] 12.6 Create chat endpoints

    - POST /api/chat/message
    - GET /api/chat/history
    - _Requirements: 11.1, 11.2, 11.4_
  
  - [x] 12.7 Write integration tests for API endpoints


    - Test authentication flow end-to-end
    - Test platform connection flow
    - Test message fetching and display
    - Test smart reply workflow
    - Test chat interaction
- [x] 13. Implement frontend with React and RetroUI



- [ ] 13. Implement frontend with React and RetroUI

  - [x] 13.1 Set up routing and layout


    - Configure React Router
    - Create main layout component with RetroUI
    - Create navigation component
    - Implement protected route wrapper
    - _Requirements: 17.1_
  
  - [x] 13.2 Implement authentication pages


    - Create login page with Auth0 integration
    - Create signup page
    - Implement authentication context
    - Add form validation
    - _Requirements: 1.1, 17.2_
  
  - [x] 13.3 Implement home dashboard


    - Create statistics cards component
    - Create message feed component
    - Create message card component with platform indicator, summary, priority
    - Create actionable items list component
    - Create draft approval queue component
    - Implement filtering and sorting
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.5, 17.3_
  
  - [x] 13.4 Implement profile page


    - Create user profile display component
    - Create platform connections list
    - Create connection card with connect/disconnect buttons
    - Implement OAuth flow handling
    - _Requirements: 2.1, 17.4_
  
  - [x] 13.5 Implement chat assistant page


    - Create full-page chat interface
    - Create message bubble component
    - Create input bar component
    - Implement typing indicator
    - Add WebSocket for real-time updates
    - _Requirements: 11.1, 17.5_
  
  - [x] 13.6 Implement smart reply approval interface


    - Create draft review modal
    - Add approve/edit/reject buttons
    - Implement draft editing
    - Show confirmation on send
    - _Requirements: 8.1, 8.2_
  
  - [x] 13.7 Write frontend component tests


    - Test authentication flow
    - Test message feed rendering
    - Test platform connection UI
    - Test chat interface
    - Test smart reply approval workflow

- [ ] 14. Implement real-time updates and WebSocket
  - [ ] 14.1 Set up WebSocket server
    - Configure WebSocket endpoint in FastAPI
    - Implement connection management
    - Create message broadcasting system
    - _Requirements: 10.4_
  
  - [ ] 14.2 Implement frontend WebSocket client
    - Create WebSocket connection hook
    - Handle real-time message updates
    - Update statistics in real-time
    - Handle connection errors and reconnection
    - _Requirements: 10.4_

- [ ] 15. Implement data persistence and storage tests
  - [ ] 15.1 Write property tests for database operations
    - **Property 45: Messages are stored in PostgreSQL**
    - **Property 46: Storage includes all fields**
    - **Property 47: Thread relationships are maintained**
    - **Property 48: Interactions are recorded**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4**
  
  - [ ] 15.2 Write property tests for vector storage
    - **Property 52: Semantic search queries Qdrant**
    - **Property 53: Search results retrieve full messages**
    - **Validates: Requirements 13.4, 13.5**

- [ ] 16. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Create deployment configuration
  - Create Dockerfile for backend
  - Create Dockerfile for frontend
  - Create docker-compose for full stack
  - Write deployment documentation
  - Configure environment variables for production
  - _Requirements: All_
