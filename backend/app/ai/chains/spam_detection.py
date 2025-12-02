"""
Spam Detection Chain
Detects spam/promotional emails and extracts unsubscribe links using LangChain.
"""
from typing import Dict, Any, Optional
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
import re

from app.ai.config import get_ai_config, PromptTemplates


def create_spam_detection_chain() -> Runnable:
    """
    Create a chain for detecting spam/promotional messages
    
    Returns:
        Runnable: LangChain chain that takes message data and returns spam analysis
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_spam_detection_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


def extract_unsubscribe_link(content: str, metadata: Dict[str, Any]) -> Optional[str]:
    """
    Extract unsubscribe link from email content or headers
    
    Args:
        content: Email content
        metadata: Email metadata (may contain List-Unsubscribe header)
    
    Returns:
        Optional[str]: Unsubscribe URL if found
    """
    # Check List-Unsubscribe header first (RFC 2369)
    if metadata and "list_unsubscribe" in metadata:
        list_unsub = metadata["list_unsubscribe"]
        # Extract URL from <http://...> format
        url_match = re.search(r'<(https?://[^>]+)>', list_unsub)
        if url_match:
            return url_match.group(1)
    
    # Look for common unsubscribe patterns in content
    unsubscribe_patterns = [
        r'<a[^>]+href=["\']([^"\']*unsubscribe[^"\']*)["\']',
        r'<a[^>]+href=["\']([^"\']*opt-out[^"\']*)["\']',
        r'<a[^>]+href=["\']([^"\']*remove[^"\']*)["\']',
        r'(https?://[^\s<>"]+unsubscribe[^\s<>"]*)',
        r'(https?://[^\s<>"]+opt-out[^\s<>"]*)',
    ]
    
    for pattern in unsubscribe_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


async def detect_spam(
    platform: str,
    sender: str,
    subject: str,
    content: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Detect if a message is spam/promotional and extract unsubscribe info
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject (can be empty)
        content: Message content
        metadata: Optional metadata (for unsubscribe headers)
    
    Returns:
        Dict with:
            - is_spam: bool
            - spam_score: float (0.0-1.0)
            - spam_type: str (promotional, newsletter, marketing, phishing, none)
            - unsubscribe_link: Optional[str]
            - reason: str (explanation)
    """
    chain = create_spam_detection_chain()
    
    result = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject or "No subject",
        "content": content[:2000]  # Limit content length for analysis
    })
    
    # Parse the response
    # Expected format:
    # IS_SPAM: true/false
    # SPAM_SCORE: 0.0-1.0
    # SPAM_TYPE: promotional/newsletter/marketing/phishing/none
    # REASON: explanation
    
    lines = result.strip().split("\n")
    is_spam = False
    spam_score = 0.0
    spam_type = "none"
    reason = "Not spam"
    
    for line in lines:
        line = line.strip()
        if line.startswith("IS_SPAM:"):
            is_spam = line.split(":", 1)[1].strip().lower() == "true"
        elif line.startswith("SPAM_SCORE:"):
            try:
                spam_score = float(line.split(":", 1)[1].strip())
                spam_score = max(0.0, min(1.0, spam_score))
            except ValueError:
                spam_score = 0.5 if is_spam else 0.0
        elif line.startswith("SPAM_TYPE:"):
            spam_type = line.split(":", 1)[1].strip().lower()
        elif line.startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()
    
    # Extract unsubscribe link if it's promotional spam
    unsubscribe_link = None
    if is_spam and spam_type in ["promotional", "newsletter", "marketing"]:
        unsubscribe_link = extract_unsubscribe_link(content, metadata or {})
    
    return {
        "is_spam": is_spam,
        "spam_score": spam_score,
        "spam_type": spam_type,
        "unsubscribe_link": unsubscribe_link,
        "reason": reason
    }
