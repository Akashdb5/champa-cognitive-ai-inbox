"""
Task Extraction Chain
Extracts actionable tasks and deadlines from messages using LangChain.
"""
from typing import List, Optional, Tuple
from datetime import datetime
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.ai.config import get_ai_config, PromptTemplates


def create_task_extraction_chain() -> Runnable:
    """
    Create a chain for extracting tasks from messages
    
    Returns:
        Runnable: LangChain chain that takes message data and returns extracted tasks
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_task_extraction_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


def create_deadline_detection_chain() -> Runnable:
    """
    Create a chain for detecting deadlines in messages
    
    Returns:
        Runnable: LangChain chain that takes message data and returns detected deadlines
    """
    config = get_ai_config()
    llm = config.get_llm()
    prompt = PromptTemplates.get_deadline_detection_prompt()
    output_parser = StrOutputParser()
    
    # Create the chain: prompt | llm | output_parser
    chain = prompt | llm | output_parser
    
    return chain


async def extract_tasks(
    platform: str,
    sender: str,
    subject: str,
    content: str
) -> List[Tuple[str, str]]:
    """
    Extract actionable tasks from a message
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject (can be empty)
        content: Message content
    
    Returns:
        List[Tuple[str, str]]: List of (type, description) tuples for each task
    """
    chain = create_task_extraction_chain()
    
    result = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject or "No subject",
        "content": content
    })
    
    result = result.strip()
    
    # Check if no tasks were found
    if result == "NO_TASKS" or not result:
        return []
    
    # Parse the tasks from the response
    tasks = []
    for line in result.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # Expected format: TYPE: description
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                task_type = parts[0].strip().lower()
                description = parts[1].strip()
                
                # Validate task type
                if task_type in ["task", "deadline", "meeting"]:
                    tasks.append((task_type, description))
    
    return tasks


async def detect_deadlines(
    platform: str,
    sender: str,
    subject: str,
    content: str
) -> List[Tuple[str, Optional[str]]]:
    """
    Detect deadlines in a message
    
    Args:
        platform: Source platform (gmail, slack, calendar)
        sender: Message sender
        subject: Message subject (can be empty)
        content: Message content
    
    Returns:
        List[Tuple[str, Optional[str]]]: List of (description, date) tuples for each deadline
    """
    chain = create_deadline_detection_chain()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    result = await chain.ainvoke({
        "platform": platform,
        "sender": sender,
        "subject": subject or "No subject",
        "content": content,
        "current_date": current_date
    })
    
    result = result.strip()
    
    # Check if no deadlines were found
    if result == "NO_DEADLINES" or not result:
        return []
    
    # Parse the deadlines from the response
    deadlines = []
    for line in result.split("\n"):
        line = line.strip()
        if not line or not line.startswith("DEADLINE:"):
            continue
        
        # Expected format: DEADLINE: description | DATE: date_if_mentioned
        # or just: DEADLINE: description
        line = line.replace("DEADLINE:", "").strip()
        
        description = line
        date_str = None
        
        if "|" in line and "DATE:" in line:
            parts = line.split("|")
            description = parts[0].strip()
            date_part = parts[1].strip()
            if date_part.startswith("DATE:"):
                date_str = date_part.replace("DATE:", "").strip()
                if date_str.lower() in ["none", "not mentioned", ""]:
                    date_str = None
        
        deadlines.append((description, date_str))
    
    return deadlines
