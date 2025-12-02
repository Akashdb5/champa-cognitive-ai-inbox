"""
Summarization Chain
Generates concise summaries of messages using LangChain.
"""
from typing import Dict, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.ai.config import get_ai_config, PromptTemplates


def create_summarization_chain() -> Runnable:
    """
    Create a chain for summarizing messages
    
    Returns:
        Runnable: LangChain chain that takes message data and returns a summary
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_summarization_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


async def summarize_message(
    platform: str,
    sender: str,
    subject: str,
    content: str
) -> str:
    """
    Summarize a message using the summarization chain
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject (can be empty)
        content: Message content
    
    Returns:
        str: Concise summary of the message
    """
    chain = create_summarization_chain()
    
    summary = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject or "No subject",
        "content": content
    })
    
    return summary.strip()
