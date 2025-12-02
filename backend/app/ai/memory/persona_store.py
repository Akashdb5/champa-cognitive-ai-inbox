"""
User Persona Memory Store
Manages long-term memory for user communication patterns, preferences, and relationships.
Uses LangGraph Store for persistent memory across threads.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from langgraph.store.memory import InMemoryStore

from app.models.persona import UserPersona


class PersonaMemoryStore:
    """
    Manages user persona data using both LangGraph Store and PostgreSQL.
    
    LangGraph Store is used for agent-accessible memory during reply generation.
    PostgreSQL is used for durable storage and querying.
    """
    
    def __init__(self, db: Session, store: Optional[InMemoryStore] = None):
        """
        Initialize persona memory store
        
        Args:
            db: Database session for PostgreSQL storage
            store: LangGraph Store for agent memory (defaults to InMemoryStore)
        """
        self.db = db
        self.store = store or InMemoryStore()
    
    async def store_observation(
        self,
        user_id: str,
        observation_type: str,
        observation_data: Dict[str, Any]
    ) -> None:
        """
        Store an observation about user behavior or preferences
        
        Args:
            user_id: User ID
            observation_type: Type of observation (style_pattern, contact, preference)
            observation_data: The observation data
        
        Validates: Requirements 6.1
        """
        # Store in PostgreSQL
        memory_key = f"{observation_type}_{datetime.utcnow().isoformat()}"
        
        persona_entry = UserPersona(
            user_id=user_id,
            memory_key=memory_key,
            memory_value=observation_data
        )
        
        self.db.add(persona_entry)
        self.db.commit()
        
        # Also update aggregated memory in LangGraph Store for agent access
        await self._update_aggregated_memory(user_id, observation_type, observation_data)
    
    async def _update_aggregated_memory(
        self,
        user_id: str,
        observation_type: str,
        new_data: Dict[str, Any]
    ) -> None:
        """Update aggregated memory in LangGraph Store"""
        # Get existing aggregated data
        namespace = ("persona", user_id)
        
        try:
            existing = await self.store.aget(namespace, observation_type)
            if existing:
                # Merge with existing data
                aggregated = existing.get("value", {})
            else:
                aggregated = {}
        except:
            aggregated = {}
        
        # Update with new observation
        if observation_type == "style_pattern":
            # Merge style patterns
            if "patterns" not in aggregated:
                aggregated["patterns"] = []
            aggregated["patterns"].append(new_data)
            # Keep only last 10 patterns
            aggregated["patterns"] = aggregated["patterns"][-10:]
        
        elif observation_type == "contact":
            # Track contact relationships
            if "contacts" not in aggregated:
                aggregated["contacts"] = {}
            
            contact_email = new_data.get("email", "unknown")
            if contact_email not in aggregated["contacts"]:
                aggregated["contacts"][contact_email] = {
                    "name": new_data.get("name", ""),
                    "relationship": new_data.get("relationship", ""),
                    "interaction_count": 0
                }
            
            aggregated["contacts"][contact_email]["interaction_count"] += 1
            if "relationship" in new_data:
                aggregated["contacts"][contact_email]["relationship"] = new_data["relationship"]
        
        elif observation_type == "preference":
            # Store preferences
            if "preferences" not in aggregated:
                aggregated["preferences"] = {}
            
            aggregated["preferences"].update(new_data)
        
        # Store in LangGraph Store
        await self.store.aput(namespace, observation_type, {"value": aggregated})
    
    async def retrieve_style_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve communication style patterns for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict containing style patterns
        
        Validates: Requirements 6.2
        """
        namespace = ("persona", user_id)
        
        try:
            result = await self.store.aget(namespace, "style_pattern")
            if result:
                return result.get("value", {})
        except:
            pass
        
        # Fallback to PostgreSQL
        patterns = self.db.query(UserPersona).filter(
            UserPersona.user_id == user_id,
            UserPersona.memory_key.like("style_pattern%")
        ).order_by(UserPersona.created_at.desc()).limit(10).all()
        
        if patterns:
            return {
                "patterns": [p.memory_value for p in patterns]
            }
        
        return {"patterns": []}
    
    async def retrieve_contacts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve contact relationships for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of contact information
        
        Validates: Requirements 6.3
        """
        namespace = ("persona", user_id)
        
        try:
            result = await self.store.aget(namespace, "contact")
            if result:
                contacts_dict = result.get("value", {}).get("contacts", {})
                # Convert to list and sort by interaction count
                contacts_list = [
                    {"email": email, **data}
                    for email, data in contacts_dict.items()
                ]
                contacts_list.sort(key=lambda x: x.get("interaction_count", 0), reverse=True)
                return contacts_list
        except:
            pass
        
        # Fallback to PostgreSQL
        contacts = self.db.query(UserPersona).filter(
            UserPersona.user_id == user_id,
            UserPersona.memory_key.like("contact%")
        ).order_by(UserPersona.created_at.desc()).limit(20).all()
        
        if contacts:
            return [c.memory_value for c in contacts]
        
        return []
    
    async def retrieve_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user preferences for message handling
        
        Args:
            user_id: User ID
        
        Returns:
            Dict containing user preferences
        
        Validates: Requirements 6.4
        """
        namespace = ("persona", user_id)
        
        try:
            result = await self.store.aget(namespace, "preference")
            if result:
                return result.get("value", {}).get("preferences", {})
        except:
            pass
        
        # Fallback to PostgreSQL
        prefs = self.db.query(UserPersona).filter(
            UserPersona.user_id == user_id,
            UserPersona.memory_key.like("preference%")
        ).order_by(UserPersona.created_at.desc()).first()
        
        if prefs:
            return prefs.memory_value
        
        return {}
    
    async def get_full_persona(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete persona data for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict containing all persona data
        
        Validates: Requirements 6.5
        """
        style_patterns = await self.retrieve_style_patterns(user_id)
        contacts = await self.retrieve_contacts(user_id)
        preferences = await self.retrieve_preferences(user_id)
        
        return {
            "style_patterns": style_patterns,
            "contacts": contacts,
            "preferences": preferences
        }
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search through user memories
        
        Args:
            user_id: User ID
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching memories
        """
        # Simple text search in PostgreSQL
        # In production, could use full-text search or vector similarity
        memories = self.db.query(UserPersona).filter(
            UserPersona.user_id == user_id
        ).order_by(UserPersona.created_at.desc()).limit(limit * 2).all()
        
        # Filter by query (simple contains check)
        query_lower = query.lower()
        results = []
        
        for memory in memories:
            memory_str = str(memory.memory_value).lower()
            if query_lower in memory_str or query_lower in memory.memory_key.lower():
                results.append({
                    "key": memory.memory_key,
                    "value": memory.memory_value,
                    "created_at": memory.created_at.isoformat()
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def delete_user_persona(self, user_id: str) -> bool:
        """
        Delete all persona data for a user
        
        Args:
            user_id: User ID
        
        Returns:
            bool: True if successful
        """
        try:
            self.db.query(UserPersona).filter(
                UserPersona.user_id == user_id
            ).delete()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting user persona: {e}")
            return False


def get_persona_store(db: Session, store: Optional[InMemoryStore] = None) -> PersonaMemoryStore:
    """
    Get a persona memory store instance
    
    Args:
        db: Database session
        store: Optional LangGraph Store
    
    Returns:
        PersonaMemoryStore: Configured persona store
    """
    return PersonaMemoryStore(db=db, store=store)
