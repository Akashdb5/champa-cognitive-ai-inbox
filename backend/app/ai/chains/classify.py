"""
Intent Classification Chain
Classifies message intent using LangChain.
"""
from typing import Literal
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.ai.config import get_ai_config, PromptTemplates


# Valid intent categories
IntentType = Literal["request", "information", "question", "meeting", "notification", "social", "other"]


def create_intent_classification_chain() -> Runnable:
    """
    Create a chain for classifying message intent
    
    Returns:
        Runnable: LangChain chain that takes message data and returns intent classification
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_intent_classification_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


async def classify_intent(
    platform: str,
    sender: str,
    subject: str,
    content: str
) -> str:
    """
    Classify the intent of a message
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject (can be empty)
        content: Message content
    
    Returns:
        str: Intent classification (request, information, question, meeting, notification, social, other)
    """
    chain = create_intent_classification_chain()
    
    intent = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject or "No subject",
        "content": content
    })
    
    # Clean up the response and ensure it's a valid intent
    intent = intent.strip().lower()
    
    valid_intents = ["request", "information", "question", "meeting", "notification", "social", "other"]
    if intent not in valid_intents:
        # Default to "other" if the model returns an invalid intent
        intent = "other"
    
    return intent
