"""
Session Manager for poker.ev

Manages chat sessions and conversation history using Pinecone.
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from poker_ev.memory.pinecone_store import PineconeMemoryStore

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages chat sessions and conversation history using Pinecone

    Stores conversation summaries as vectors for semantic search and retrieval.
    """

    def __init__(self, pinecone_store: Optional[PineconeMemoryStore] = None):
        """
        Initialize session manager

        Args:
            pinecone_store: PineconeMemoryStore instance (creates new if None)
        """
        if pinecone_store is None:
            try:
                self.store = PineconeMemoryStore()
                logger.info("Session manager initialized with new Pinecone store")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone store: {e}")
                raise
        else:
            self.store = pinecone_store
            logger.info("Session manager initialized with provided Pinecone store")

        self.current_session_id = None
        self.current_messages = []

    def create_session(self) -> str:
        """
        Create a new chat session

        Returns:
            Session ID
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_id = session_id
        self.current_messages = []

        logger.info(f"Created new session: {session_id}")
        return session_id

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """
        Add a message to current session

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata (e.g., game state)
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.current_messages.append(message)

        # Auto-save session summary every 5 messages
        if len(self.current_messages) % 5 == 0:
            self._save_session_summary()

    def get_messages(
        self,
        role: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get messages from current session

        Args:
            role: Filter by role (None for all)
            limit: Maximum number of messages to return

        Returns:
            List of message dicts
        """
        messages = self.current_messages

        if role:
            messages = [m for m in messages if m['role'] == role]

        if limit:
            messages = messages[-limit:]

        return messages

    def get_conversation_context(self, max_messages: int = 10) -> List[Dict]:
        """
        Get recent conversation for LLM context

        Args:
            max_messages: Maximum messages to include

        Returns:
            List of recent messages in LLM format
        """
        messages = self.current_messages[-max_messages:]

        # Format for LLM (exclude metadata and timestamp)
        return [
            {'role': m['role'], 'content': m['content']}
            for m in messages
        ]

    def _create_session_summary(self) -> str:
        """
        Create a summary of the current session for embedding

        Returns:
            Summary string
        """
        if not self.current_messages:
            return "Empty session"

        # Extract key information
        user_messages = [m for m in self.current_messages if m['role'] == 'user']
        assistant_messages = [m for m in self.current_messages if m['role'] == 'assistant']

        # Get topics from user questions
        user_questions = [m['content'][:100] for m in user_messages[:5]]  # First 5 questions

        # Create summary
        summary = f"Chat session with {len(self.current_messages)} messages. "
        summary += f"User asked about: {', '.join(user_questions[:3])}"

        return summary

    def _extract_topics(self) -> List[str]:
        """
        Extract topics from conversation

        Returns:
            List of topics discussed
        """
        topics = []

        # Simple keyword extraction
        keywords = {
            'pot_odds': ['pot odds', 'odds', 'equity'],
            'bluffing': ['bluff', 'bluffing', 'semi-bluff'],
            'position': ['position', 'button', 'blinds'],
            'hand_strength': ['hand strength', 'premium', 'pocket'],
            'betting': ['bet', 'raise', 'call', 'fold'],
            'tournament': ['tournament', 'mtt', 'sit and go'],
            'cash_game': ['cash game', 'nlhe'],
        }

        # Check messages for keywords
        all_text = ' '.join([m['content'].lower() for m in self.current_messages])

        for topic, words in keywords.items():
            if any(word in all_text for word in words):
                topics.append(topic)

        return topics

    def _extract_advice(self) -> List[str]:
        """
        Extract advice given in conversation

        Returns:
            List of advice snippets
        """
        advice = []

        # Get assistant messages that contain advice indicators
        advice_indicators = ['should', 'consider', 'try', 'recommend', 'suggest']

        for msg in self.current_messages:
            if msg['role'] == 'assistant':
                content = msg['content']
                if any(indicator in content.lower() for indicator in advice_indicators):
                    # Extract first sentence or up to 100 chars
                    snippet = content.split('.')[0][:100]
                    advice.append(snippet)

        return advice[:5]  # Top 5 pieces of advice

    def _save_session_summary(self) -> bool:
        """
        Save current session summary to Pinecone

        Returns:
            True if saved successfully
        """
        if not self.current_session_id or not self.current_messages:
            return False

        try:
            # Create session data
            session_data = {
                'session_id': self.current_session_id,
                'timestamp': self.current_messages[0]['timestamp'] if self.current_messages else datetime.now().isoformat(),
                'summary': self._create_session_summary(),
                'topics': self._extract_topics(),
                'advice_given': self._extract_advice(),
                'user_questions': [m['content'][:100] for m in self.current_messages if m['role'] == 'user'][:10],
                'hands_discussed': [],  # Could extract from metadata
                'message_count': len(self.current_messages),
                'duration_minutes': 0  # Could calculate from timestamps
            }

            # Save to Pinecone
            success = self.store.save_session(session_data)

            if success:
                logger.debug(f"Saved session summary {self.current_session_id}")
            else:
                logger.warning(f"Failed to save session summary {self.current_session_id}")

            return success

        except Exception as e:
            logger.error(f"Error saving session summary: {e}")
            return False

    def save_session(self) -> bool:
        """
        Explicitly save current session

        Returns:
            True if saved successfully
        """
        return self._save_session_summary()

    def search_sessions(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for past sessions using semantic search

        Args:
            query: Search query (e.g., "discussions about pot odds")
            limit: Maximum number of sessions to return

        Returns:
            List of matching sessions
        """
        try:
            results = self.store.search_sessions(query=query, top_k=limit)

            sessions = []
            for result in results:
                session = result.get('metadata', {})
                session['similarity_score'] = result.get('score')
                sessions.append(session)

            logger.debug(f"Found {len(sessions)} sessions for query: '{query}'")
            return sessions

        except Exception as e:
            logger.error(f"Error searching sessions: {e}")
            return []

    def get_related_sessions(
        self,
        current_topic: str,
        limit: int = 3
    ) -> List[Dict]:
        """
        Get sessions related to current topic

        Args:
            current_topic: Current discussion topic
            limit: Maximum number of sessions to return

        Returns:
            List of related sessions
        """
        return self.search_sessions(query=current_topic, limit=limit)

    def get_past_advice_on_topic(
        self,
        topic: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get past advice given on a specific topic

        Args:
            topic: Topic to search for
            limit: Maximum number of advice items to return

        Returns:
            List of past advice snippets
        """
        try:
            # Search for related sessions
            sessions = self.search_sessions(query=topic, limit=limit)

            # Extract advice from sessions
            all_advice = []
            for session in sessions:
                advice = session.get('advice_given', [])
                if isinstance(advice, list):
                    all_advice.extend(advice)

            return all_advice[:limit]

        except Exception as e:
            logger.error(f"Error getting past advice: {e}")
            return []

    def clear_session(self):
        """Clear current session without saving"""
        # Save before clearing
        if self.current_messages:
            self._save_session_summary()

        self.current_messages = []
        self.current_session_id = None
        logger.info("Current session cleared")

    def export_conversation(self, format: str = 'txt') -> str:
        """
        Export current conversation to text

        Args:
            format: Export format ('txt' or 'md')

        Returns:
            Formatted conversation string
        """
        if not self.current_messages:
            return "No conversation to export."

        lines = []

        if format == 'md':
            lines.append(f"# Poker Coach Conversation")
            lines.append(f"\nSession: {self.current_session_id}")
            lines.append(f"Messages: {len(self.current_messages)}\n")
            lines.append("---\n")

        for msg in self.current_messages:
            timestamp = msg.get('timestamp', '')
            role = msg['role'].upper()
            content = msg['content']

            if format == 'md':
                lines.append(f"## {role} ({timestamp})")
                lines.append(content)
                lines.append("")
            else:
                lines.append(f"[{timestamp}] {role}:")
                lines.append(content)
                lines.append("")

        return '\n'.join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create session manager
    try:
        manager = SessionManager()
        print("✅ Session manager initialized with Pinecone")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        exit(1)

    # Create new session
    session_id = manager.create_session()
    print(f"\n✅ Created session: {session_id}")

    # Add some messages
    manager.add_message(
        role='user',
        content='Should I call here with pocket jacks?',
        metadata={'hand': ['J♠', 'J♥'], 'pot': 150}
    )

    manager.add_message(
        role='assistant',
        content='With pocket jacks in this situation, calling is reasonable. '
                'You have a strong hand but need to be cautious of overcards on the flop. '
                'Consider your position and the pot odds.'
    )

    manager.add_message(
        role='user',
        content='What about pot odds calculations?'
    )

    manager.add_message(
        role='assistant',
        content='Pot odds are the ratio of the current pot size to the cost of a contemplated call. '
                'To calculate: divide the amount you need to call by the pot after you call. '
                'Compare this to your equity in the hand.'
    )

    manager.add_message(
        role='user',
        content='How do I improve my button play?'
    )

    # Get conversation context
    context = manager.get_conversation_context()
    print(f"\n💬 Conversation context ({len(context)} messages):")
    for msg in context:
        print(f"  {msg['role']}: {msg['content'][:50]}...")

    # Save session
    if manager.save_session():
        print(f"\n💾 Session saved to Pinecone")

    # Search for sessions
    print("\n🔍 Searching for sessions about 'pot odds'...")
    results = manager.search_sessions("pot odds calculation")
    print(f"Found {len(results)} sessions:")
    for session in results:
        print(f"  • {session.get('session_id')} (score: {session.get('similarity_score', 0):.3f})")
        print(f"    Summary: {session.get('summary', 'N/A')[:80]}...")

    # Get past advice
    print("\n📚 Past advice on 'button play'...")
    advice = manager.get_past_advice_on_topic("button play")
    print(f"Found {len(advice)} pieces of advice:")
    for i, adv in enumerate(advice, 1):
        print(f"  {i}. {adv}")

    # Export conversation
    export = manager.export_conversation(format='txt')
    print(f"\n📄 Exported conversation:\n")
    print(export[:500] + "..." if len(export) > 500 else export)
