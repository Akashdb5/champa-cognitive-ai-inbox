"""
Property-based tests for message normalization

Feature: champa-unified-inbox
Tests Properties 12-15 from design document
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timezone
from uuid import uuid4

from app.services.message import normalize_message
from app.schemas.message import NormalizedMessage


# Custom strategies for generating test data
@st.composite
def gmail_message(draw):
    """Generate a valid Gmail message"""
    return {
        "id": draw(st.text(min_size=1, max_size=100)),
        "from": draw(st.emails()),
        "body": draw(st.text(min_size=0, max_size=5000)),
        "subject": draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        "timestamp": draw(st.datetimes(min_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
        "thread_id": draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        "metadata": draw(st.dictionaries(st.text(min_size=1, max_size=50), st.text(max_size=200), max_size=10))
    }


@st.composite
def slack_message(draw):
    """Generate a valid Slack message"""
    return {
        "ts": draw(st.text(min_size=1, max_size=100)),
        "user": draw(st.text(min_size=1, max_size=100)),
        "text": draw(st.text(min_size=0, max_size=5000)),
        "timestamp": draw(st.datetimes(min_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
        "thread_ts": draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        "metadata": draw(st.dictionaries(st.text(min_size=1, max_size=50), st.text(max_size=200), max_size=10))
    }


@st.composite
def calendar_event(draw):
    """Generate a valid Calendar event"""
    return {
        "id": draw(st.text(min_size=1, max_size=100)),
        "organizer": draw(st.emails()),
        "description": draw(st.text(min_size=0, max_size=5000)),
        "title": draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        "start_time": draw(st.datetimes(min_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
        "metadata": draw(st.dictionaries(st.text(min_size=1, max_size=50), st.text(max_size=200), max_size=10))
    }


@st.composite
def user_id_strategy(draw):
    """Generate a valid UUID"""
    return uuid4()


# Property 12: All messages are normalized
@settings(max_examples=100)
@given(
    platform=st.sampled_from(["gmail", "slack", "calendar"]),
    user_id=user_id_strategy()
)
@pytest.mark.property
def test_property_12_all_messages_normalized(platform, user_id):
    """
    Feature: champa-unified-inbox, Property 12: All messages are normalized
    Validates: Requirements 4.1
    
    For any message fetched from any platform, the system should convert it 
    to a normalized message format.
    """
    # Generate appropriate message based on platform
    if platform == "gmail":
        raw_message = gmail_message().example()
    elif platform == "slack":
        raw_message = slack_message().example()
    else:  # calendar
        raw_message = calendar_event().example()
    
    # Normalize the message
    result = normalize_message(raw_message, user_id, platform)
    
    # Verify result is a NormalizedMessage
    assert isinstance(result, NormalizedMessage)
    assert result.user_id == user_id
    assert result.platform == platform


# Property 13: Normalization preserves platform identifier
@settings(max_examples=100)
@given(
    platform=st.sampled_from(["gmail", "slack", "calendar"]),
    user_id=user_id_strategy()
)
@pytest.mark.property
def test_property_13_normalization_preserves_platform(platform, user_id):
    """
    Feature: champa-unified-inbox, Property 13: Normalization preserves platform identifier
    Validates: Requirements 4.2
    
    For any message being normalized, the source platform identifier should be 
    preserved in the normalized message.
    """
    # Generate appropriate message based on platform
    if platform == "gmail":
        raw_message = gmail_message().example()
    elif platform == "slack":
        raw_message = slack_message().example()
    else:  # calendar
        raw_message = calendar_event().example()
    
    # Normalize the message
    result = normalize_message(raw_message, user_id, platform)
    
    # Verify platform is preserved
    assert result.platform == platform


# Property 14: Normalization extracts common fields
@settings(max_examples=100)
@given(
    platform=st.sampled_from(["gmail", "slack", "calendar"]),
    user_id=user_id_strategy()
)
@pytest.mark.property
def test_property_14_normalization_extracts_common_fields(platform, user_id):
    """
    Feature: champa-unified-inbox, Property 14: Normalization extracts common fields
    Validates: Requirements 4.3
    
    For any message being normalized, the result should contain sender, content, 
    timestamp, and unique identifier fields.
    """
    # Generate appropriate message based on platform
    if platform == "gmail":
        raw_message = gmail_message().example()
    elif platform == "slack":
        raw_message = slack_message().example()
    else:  # calendar
        raw_message = calendar_event().example()
    
    # Normalize the message
    result = normalize_message(raw_message, user_id, platform)
    
    # Verify all common fields are present and non-empty
    assert result.sender is not None
    assert result.sender != ""
    assert result.content is not None
    assert result.timestamp is not None
    assert isinstance(result.timestamp, datetime)
    assert result.platform_message_id is not None
    assert result.platform_message_id != ""


# Property 15: Normalization preserves metadata
@settings(max_examples=100)
@given(
    platform=st.sampled_from(["gmail", "slack", "calendar"]),
    user_id=user_id_strategy()
)
@pytest.mark.property
def test_property_15_normalization_preserves_metadata(platform, user_id):
    """
    Feature: champa-unified-inbox, Property 15: Normalization preserves metadata
    Validates: Requirements 4.4
    
    For any message with platform-specific metadata, the normalized message should 
    contain that metadata in a structured format.
    """
    # Generate appropriate message based on platform with metadata
    if platform == "gmail":
        raw_message = gmail_message().example()
    elif platform == "slack":
        raw_message = slack_message().example()
    else:  # calendar
        raw_message = calendar_event().example()
    
    # Normalize the message
    result = normalize_message(raw_message, user_id, platform)
    
    # Verify metadata is preserved
    assert result.metadata is not None
    assert isinstance(result.metadata, dict)
    
    # If original had metadata, it should be preserved
    if "metadata" in raw_message and raw_message["metadata"]:
        assert result.metadata == raw_message["metadata"]
