"""
Session Manager for poker.ev

Manages chat sessions and conversation history.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages chat sessions and conversation history

    Stores conversations to disk for persistence across sessions.
    """

    def __init__(self, sessions_dir: str = None):
        """
        Initialize session manager

        Args:
            sessions_dir: Directory to store session files
        """
        if sessions_dir is None:
            # Default to poker_ev/memory/sessions/
            sessions_dir = Path(__file__).parent / "sessions"

        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

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

        # Auto-save every 5 messages
        if len(self.current_messages) % 5 == 0:
            self.save_session()

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

    def save_session(self) -> bool:
        """
        Save current session to disk

        Returns:
            True if saved successfully
        """
        if not self.current_session_id:
            logger.warning("No active session to save")
            return False

        try:
            session_file = self.sessions_dir / f"{self.current_session_id}.json"

            session_data = {
                'session_id': self.current_session_id,
                'created_at': self.current_messages[0]['timestamp'] if self.current_messages else datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'message_count': len(self.current_messages),
                'messages': self.current_messages
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)

            logger.debug(f"Saved session {self.current_session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def load_session(self, session_id: str) -> bool:
        """
        Load a session from disk

        Args:
            session_id: Session ID to load

        Returns:
            True if loaded successfully
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.json"

            if not session_file.exists():
                logger.warning(f"Session file not found: {session_id}")
                return False

            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            self.current_session_id = session_data['session_id']
            self.current_messages = session_data['messages']

            logger.info(f"Loaded session {session_id} with {len(self.current_messages)} messages")
            return True

        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False

    def list_sessions(self) -> List[Dict]:
        """
        List all saved sessions

        Returns:
            List of session info dicts
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                sessions.append({
                    'session_id': data['session_id'],
                    'created_at': data.get('created_at', 'unknown'),
                    'message_count': data.get('message_count', 0)
                })

            except Exception as e:
                logger.warning(f"Error reading {session_file}: {e}")

        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x['created_at'], reverse=True)

        return sessions

    def get_latest_session(self) -> Optional[str]:
        """
        Get ID of most recent session

        Returns:
            Session ID or None if no sessions exist
        """
        sessions = self.list_sessions()
        return sessions[0]['session_id'] if sessions else None

    def clear_session(self):
        """Clear current session without deleting file"""
        self.current_messages = []
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
    manager = SessionManager()

    # Create new session
    session_id = manager.create_session()
    print(f"✅ Created session: {session_id}")

    # Add some messages
    manager.add_message(
        role='user',
        content='Should I call here with pocket jacks?',
        metadata={'hand': ['J♠', 'J♥'], 'pot': 150}
    )

    manager.add_message(
        role='assistant',
        content='With pocket jacks in this situation, calling is reasonable. '
                'You have a strong hand but need to be cautious of overcards on the flop.'
    )

    manager.add_message(
        role='user',
        content='What about pot odds?'
    )

    # Get conversation context
    context = manager.get_conversation_context()
    print(f"\n💬 Conversation context ({len(context)} messages):")
    for msg in context:
        print(f"  {msg['role']}: {msg['content'][:50]}...")

    # Save session
    manager.save_session()
    print(f"\n💾 Session saved")

    # List sessions
    sessions = manager.list_sessions()
    print(f"\n📋 Available sessions: {len(sessions)}")
    for sess in sessions:
        print(f"  • {sess['session_id']} ({sess['message_count']} messages)")

    # Export conversation
    export = manager.export_conversation(format='txt')
    print(f"\n📄 Exported conversation:\n")
    print(export[:500] + "...")
