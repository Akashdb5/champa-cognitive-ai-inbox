"""
Property-based tests for platform integration

Feature: champa-unified-inbox
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from uuid import uuid4

from app.services.platform import PlatformService
from app.models.platform import PlatformConnection
from app.models.user import User
from app.integrations.interfaces import Connection


# Strategies for generating test data
@st.composite
def user_id_strategy(draw):
    """Generate valid user IDs"""
    return str(uuid4())


@st.composite
def platform_strategy(draw):
    """Generate valid platform names"""
    return draw(st.sampled_from(["gmail", "slack", "calendar"]))


@st.composite
def auth_config_id_strategy(draw):
    """Generate valid auth config IDs"""
    return f"ac_{draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=10, max_size=20))}"


@st.composite
def connection_strategy(draw):
    """Generate Connection objects"""
    platform = draw(platform_strategy())
    user_id = draw(user_id_strategy())
    return Connection(
        platform=platform,
        user_id=user_id,
        access_token=f"token_{draw(st.text(min_size=20, max_size=40))}",
        refresh_token=None,
        token_expires_at=None
    )


class TestPlatformIntegrationProperties:
    """Property-based tests for platform integration"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.commit = Mock()
        db.rollback = Mock()
        db.add = Mock()
        db.refresh = Mock()
        db.delete = Mock()
        return db
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = Mock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        return user
    
    # Feature: champa-unified-inbox, Property 5: OAuth success stores credentials
    # Validates: Requirements 2.3
    @given(
        user_id=user_id_strategy(),
        platform=platform_strategy(),
        auth_config_id=auth_config_id_strategy(),
        connection=connection_strategy()
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_oauth_success_stores_credentials(
        self, mock_db, user_id, platform, auth_config_id, connection
    ):
        """
        Property 5: OAuth success stores credentials
        
        For any successful OAuth flow, the system should store the access token,
        refresh token, and expiration time in the database and mark the platform as connected.
        """
        # Setup mock user
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Setup mock adapter
        with patch('app.services.platform.ComposioGmailAdapter') as MockGmail, \
             patch('app.services.platform.ComposioSlackAdapter') as MockSlack, \
             patch('app.services.platform.ComposioCalendarAdapter') as MockCalendar:
            
            # Create mock adapter that returns our connection
            mock_adapter = AsyncMock()
            mock_adapter.connect = AsyncMock(return_value=connection)
            
            # Set the appropriate mock based on platform
            if platform == "gmail":
                MockGmail.return_value = mock_adapter
            elif platform == "slack":
                MockSlack.return_value = mock_adapter
            else:
                MockCalendar.return_value = mock_adapter
            
            # Create service and initiate connection
            service = PlatformService(mock_db)
            
            # Mock the query to return no existing connection
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                mock_user,  # First call for user lookup
                None  # Second call for existing connection check
            ]
            
            result = await service.initiate_connection(user_id, platform, auth_config_id)
            
            # Verify connection was stored
            assert mock_db.add.called, "Connection should be added to database"
            assert mock_db.commit.called, "Changes should be committed"
            assert result["status"] == "connected"
            assert result["platform"] == platform
    
    # Feature: champa-unified-inbox, Property 6: Disconnect removes credentials
    # Validates: Requirements 2.4
    @given(
        user_id=user_id_strategy(),
        platform=platform_strategy()
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_disconnect_removes_credentials(self, mock_db, user_id, platform):
        """
        Property 6: Disconnect removes credentials
        
        For any connected platform, disconnecting should remove all stored tokens
        from the database and mark the platform as disconnected.
        """
        # Setup mock connection
        mock_connection = Mock(spec=PlatformConnection)
        mock_connection.user_id = user_id
        mock_connection.platform = platform
        mock_connection.access_token = "test_token"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_connection
        
        # Setup mock adapter
        with patch('app.services.platform.ComposioGmailAdapter') as MockGmail, \
             patch('app.services.platform.ComposioSlackAdapter') as MockSlack, \
             patch('app.services.platform.ComposioCalendarAdapter') as MockCalendar:
            
            mock_adapter = AsyncMock()
            mock_adapter.disconnect = AsyncMock()
            
            if platform == "gmail":
                MockGmail.return_value = mock_adapter
            elif platform == "slack":
                MockSlack.return_value = mock_adapter
            else:
                MockCalendar.return_value = mock_adapter
            
            # Create service and disconnect
            service = PlatformService(mock_db)
            result = await service.disconnect_platform(user_id, platform)
            
            # Verify connection was removed
            assert mock_db.delete.called, "Connection should be deleted from database"
            assert mock_db.commit.called, "Changes should be committed"
            assert result["status"] == "disconnected"
            assert result["platform"] == platform
    
    # Feature: champa-unified-inbox, Property 7: Connection failures show errors
    # Validates: Requirements 2.5
    @given(
        user_id=user_id_strategy(),
        platform=platform_strategy(),
        auth_config_id=auth_config_id_strategy(),
        error_message=st.text(min_size=10, max_size=100)
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_connection_failures_show_errors(
        self, mock_db, user_id, platform, auth_config_id, error_message
    ):
        """
        Property 7: Connection failures show errors
        
        For any platform connection attempt that fails, the system should display
        an error message to the user without storing partial credentials.
        """
        # Setup mock user
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        # Setup mock adapter that raises an exception
        with patch('app.services.platform.ComposioGmailAdapter') as MockGmail, \
             patch('app.services.platform.ComposioSlackAdapter') as MockSlack, \
             patch('app.services.platform.ComposioCalendarAdapter') as MockCalendar:
            
            mock_adapter = AsyncMock()
            mock_adapter.connect = AsyncMock(side_effect=Exception(error_message))
            
            if platform == "gmail":
                MockGmail.return_value = mock_adapter
            elif platform == "slack":
                MockSlack.return_value = mock_adapter
            else:
                MockCalendar.return_value = mock_adapter
            
            # Create service
            service = PlatformService(mock_db)
            
            # Mock the query to return user and no existing connection
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                mock_user,  # First call for user lookup
                None  # Second call for existing connection check
            ]
            
            # Attempt connection and expect failure
            with pytest.raises(Exception) as exc_info:
                await service.initiate_connection(user_id, platform, auth_config_id)
            
            # Verify error is raised and rollback is called
            assert mock_db.rollback.called, "Transaction should be rolled back on error"
            assert not mock_db.commit.called, "Changes should not be committed on error"
            assert error_message in str(exc_info.value) or "Failed to connect" in str(exc_info.value)
    
    # Feature: champa-unified-inbox, Property 54: Platform calls use abstraction
    # Validates: Requirements 14.3
    @given(
        user_id=user_id_strategy(),
        platform=platform_strategy(),
        auth_config_id=auth_config_id_strategy()
    )
    @settings(max_examples=100)
    @pytest.mark.asyncio
    async def test_platform_calls_use_abstraction(
        self, mock_db, user_id, platform, auth_config_id
    ):
        """
        Property 54: Platform calls use abstraction
        
        For any platform interface call, the system should route through the
        abstraction layer rather than calling Composio directly.
        """
        # Setup mock user
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        
        # Track whether the adapter interface was used
        adapter_called = False
        
        def track_adapter_call(*args, **kwargs):
            nonlocal adapter_called
            adapter_called = True
            return Connection(
                platform=platform,
                user_id=user_id,
                access_token="test_token",
                refresh_token=None,
                token_expires_at=None
            )
        
        # Setup mock adapter
        with patch('app.services.platform.ComposioGmailAdapter') as MockGmail, \
             patch('app.services.platform.ComposioSlackAdapter') as MockSlack, \
             patch('app.services.platform.ComposioCalendarAdapter') as MockCalendar:
            
            mock_adapter = AsyncMock()
            mock_adapter.connect = AsyncMock(side_effect=track_adapter_call)
            
            if platform == "gmail":
                MockGmail.return_value = mock_adapter
            elif platform == "slack":
                MockSlack.return_value = mock_adapter
            else:
                MockCalendar.return_value = mock_adapter
            
            # Create service
            service = PlatformService(mock_db)
            
            # Mock the query to return user and no existing connection
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                mock_user,  # First call for user lookup
                None  # Second call for existing connection check
            ]
            
            # Make a platform call
            await service.initiate_connection(user_id, platform, auth_config_id)
            
            # Verify the adapter interface was used
            assert adapter_called, "Platform calls should go through the abstraction layer"
            assert mock_adapter.connect.called, "Adapter's connect method should be called"
