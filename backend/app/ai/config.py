"""
AI Pipeline Configuration
Configures LLM client, embedding model, and prompt templates for message analysis.
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings


class AIConfig:
    """Configuration for AI Pipeline components"""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        temperature: float = 0.0
    ):
        """
        Initialize AI configuration
        
        Args:
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model_name: Name of the OpenAI model to use
            embedding_model: Name of the embedding model to use
            temperature: Temperature for LLM generation (0.0 = deterministic)
        """
        self.openai_api_key = openai_api_key or settings.OPENAI_API_KEY
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.temperature = temperature
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
    
    def get_llm(self) -> ChatOpenAI:
        """
        Get configured LLM client
        
        Returns:
            ChatOpenAI: Configured OpenAI chat model
        """
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.openai_api_key
        )
    
    def get_embeddings(self) -> OpenAIEmbeddings:
        """
        Get configured embedding model
        
        Returns:
            OpenAIEmbeddings: Configured OpenAI embeddings model
        """
        return OpenAIEmbeddings(
            model=self.embedding_model,
            api_key=self.openai_api_key
        )


class PromptTemplates:
    """Prompt templates for message analysis"""
    
    @staticmethod
    def get_summarization_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for message summarization
        
        Returns:
            ChatPromptTemplate: Prompt for generating message summaries
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at summarizing messages concisely.
Your task is to create a brief, clear summary of the message that captures the key points.
Keep the summary to 1-2 sentences maximum."""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}

Generate a concise summary of this message:""")
        ])
    
    @staticmethod
    def get_intent_classification_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for intent classification
        
        Returns:
            ChatPromptTemplate: Prompt for classifying message intent
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at classifying message intent.
Classify the message into one of these categories:
- request: Asking for something or requesting action
- information: Sharing information or updates
- question: Asking a question
- meeting: Meeting invitation or scheduling
- notification: System notification or alert
- social: Social/casual communication
- other: Doesn't fit other categories

Respond with only the category name."""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}

What is the intent of this message?""")
        ])
    
    @staticmethod
    def get_task_extraction_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for task extraction
        
        Returns:
            ChatPromptTemplate: Prompt for extracting tasks from messages
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at identifying actionable tasks in messages.
Extract any tasks, action items, or to-dos mentioned in the message.
For each task, provide:
1. A clear description of the task
2. The type (task, deadline, or meeting)

If there are no tasks, respond with "NO_TASKS".
Format each task as: TYPE: description"""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}

Extract all actionable tasks from this message:""")
        ])
    
    @staticmethod
    def get_deadline_detection_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for deadline detection
        
        Returns:
            ChatPromptTemplate: Prompt for detecting deadlines in messages
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at identifying deadlines and time-sensitive information.
Extract any deadlines, due dates, or time-sensitive items mentioned in the message.
For each deadline, provide:
1. A description of what is due
2. The deadline date/time if mentioned

If there are no deadlines, respond with "NO_DEADLINES".
Format each deadline as: DEADLINE: description | DATE: date_if_mentioned"""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}
Current date: {current_date}

Extract all deadlines from this message:""")
        ])
    
    @staticmethod
    def get_priority_scoring_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for priority scoring
        
        Returns:
            ChatPromptTemplate: Prompt for assigning priority scores
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at assessing message priority.
Analyze the message and assign a priority score from 0.0 to 1.0 where:
- 0.0-0.3: Low priority (informational, social, can wait)
- 0.4-0.6: Medium priority (needs attention soon)
- 0.7-1.0: High priority (urgent, time-sensitive, important)

Consider factors like:
- Urgency and time sensitivity
- Sender importance
- Presence of deadlines or action items
- Keywords indicating urgency (urgent, ASAP, deadline, etc.)

Respond with only a number between 0.0 and 1.0."""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}

What is the priority score for this message?""")
        ])
    
    @staticmethod
    def get_smart_reply_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for generating smart reply suggestions
        
        Returns:
            ChatPromptTemplate: Prompt for generating contextual reply suggestions
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating professional, contextual reply suggestions.

Analyze the message and generate 3 appropriate reply options that are:
- Professional and courteous
- Contextually relevant to the message content
- Varied in tone (acknowledgment, detailed response, brief response)
- Appropriate for the platform and sender relationship

Consider:
- The sender's tone and formality level
- Whether this requires immediate action or is informational
- The platform context (email vs chat vs calendar)
- Professional vs personal relationship indicators

Output format (exactly 3 lines):
REPLY_1: [TYPE] First reply suggestion
REPLY_2: [TYPE] Second reply suggestion  
REPLY_3: [TYPE] Third reply suggestion

Types: acknowledgment, thanks, question, detailed, brief, defer, meeting, action

Examples:
REPLY_1: [acknowledgment] Thank you for the update. I'll review this and get back to you.
REPLY_2: [question] Thanks for sharing this. Could you clarify the timeline for implementation?
REPLY_3: [brief] Got it, thanks!"""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}""")
        ])
    
    @staticmethod
    def get_spam_detection_prompt() -> ChatPromptTemplate:
        """
        Get prompt template for spam/promotional email detection
        
        Returns:
            ChatPromptTemplate: Prompt for detecting spam and promotional content
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at detecting spam, promotional emails, and unwanted messages.

Analyze the message and determine if it's spam or promotional content.

Consider these factors:
- Marketing language and sales pitches
- Promotional offers and discounts
- Newsletter patterns
- Automated/bulk email indicators
- Suspicious links or phishing attempts
- Sender reputation patterns

Output format (exactly 4 lines):
IS_SPAM: true/false
SPAM_SCORE: 0.0-1.0 (confidence level)
SPAM_TYPE: promotional/newsletter/marketing/phishing/none
REASON: brief explanation

Examples:
- Promotional: "50% off sale", "limited time offer", marketing emails
- Newsletter: regular updates, subscriptions, digest emails
- Marketing: product announcements, company updates
- Phishing: suspicious links, urgent requests, impersonation
- None: legitimate personal or business communication"""),
            ("user", """Platform: {platform}
Sender: {sender}
Subject: {subject}
Content: {content}""")
        ])


# Global configuration instance
_ai_config: Optional[AIConfig] = None


def get_ai_config() -> AIConfig:
    """
    Get or create global AI configuration instance
    
    Returns:
        AIConfig: Global AI configuration
    """
    global _ai_config
    if _ai_config is None:
        _ai_config = AIConfig()
    return _ai_config


def set_ai_config(config: AIConfig) -> None:
    """
    Set global AI configuration instance
    
    Args:
        config: AI configuration to set
    """
    global _ai_config
    _ai_config = config
