"""
Smart Reply Generation Chain
Generates intelligent reply suggestions for messages using LangChain.
"""
from typing import List, Dict, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.ai.config import get_ai_config, PromptTemplates


def create_smart_reply_chain() -> Runnable:
    """
    Create a chain for generating smart reply suggestions
    
    Returns:
        Runnable: LangChain chain that takes message data and returns reply suggestions
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_smart_reply_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


async def generate_smart_replies(
    platform: str,
    sender: str,
    subject: str,
    content: str
) -> List[Dict[str, Any]]:
    """
    Generate smart reply suggestions for a message
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject
        content: Message content
    
    Returns:
        List of reply suggestions with text, confidence, and type
    """
    chain = create_smart_reply_chain()
    
    result = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject,
        "content": content[:1500]  # Limit content length
    })
    
    # Parse the response
    # Expected format:
    # REPLY_1: [TYPE] Reply text here
    # REPLY_2: [TYPE] Another reply text
    # REPLY_3: [TYPE] Third reply option
    
    replies = []
    lines = result.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if line.startswith("REPLY_"):
            try:
                # Extract reply number and content
                parts = line.split(":", 1)
                if len(parts) == 2:
                    reply_content = parts[1].strip()
                    
                    # Extract type if present [TYPE]
                    reply_type = "general"
                    if reply_content.startswith("[") and "]" in reply_content:
                        type_end = reply_content.find("]")
                        reply_type = reply_content[1:type_end].lower()
                        reply_content = reply_content[type_end + 1:].strip()
                    
                    # Determine confidence based on reply type and length
                    confidence = 0.8
                    if reply_type in ["acknowledgment", "thanks"]:
                        confidence = 0.9
                    elif len(reply_content) < 20:
                        confidence = 0.7
                    
                    replies.append({
                        "text": reply_content,
                        "type": reply_type,
                        "confidence": confidence
                    })
            except Exception as e:
                print(f"Error parsing reply line '{line}': {e}")
                continue
    
    # If no replies were parsed, provide fallback
    if not replies:
        replies = [
            {"text": "Thank you for your message.", "type": "acknowledgment", "confidence": 0.6},
            {"text": "I'll get back to you soon.", "type": "defer", "confidence": 0.6},
            {"text": "Thanks for reaching out!", "type": "thanks", "confidence": 0.6}
        ]
    
    return replies[:3]  # Return max 3 suggestions
