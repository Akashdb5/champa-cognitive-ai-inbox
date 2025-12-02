"""
Priority Scoring Chain
Assigns priority scores to messages using LangChain.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.ai.config import get_ai_config, PromptTemplates


def create_priority_scoring_chain() -> Runnable:
    """
    Create a chain for scoring message priority
    
    Returns:
        Runnable: LangChain chain that takes message data and returns a priority score
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_priority_scoring_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


async def calculate_priority(
    platform: str,
    sender: str,
    subject: str,
    content: str
) -> float:
    """
    Calculate the priority score for a message
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject (can be empty)
        content: Message content
    
    Returns:
        float: Priority score between 0.0 and 1.0
    """
    chain = create_priority_scoring_chain()
    
    result = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject or "No subject",
        "content": content
    })
    
    # Parse the priority score from the response
    try:
        score = float(result.strip())
        # Ensure score is within valid range
        score = max(0.0, min(1.0, score))
    except ValueError:
        # Default to medium priority if parsing fails
        score = 0.5
    
    return score
