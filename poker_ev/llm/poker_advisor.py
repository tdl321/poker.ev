"""
Poker Advisor - Simple LLM agent with RAG

Basic poker advisor using Ollama + RAG for strategy advice.
"""

import logging
from typing import Generator, Optional, Dict
from poker_ev.llm.ollama_client import OllamaClient
from poker_ev.llm.game_context import GameContextProvider
from poker_ev.rag.pinecone_store import PineconePokerStore, InMemoryPokerStore
from poker_ev.rag.document_loader import PokerDocumentLoader

logger = logging.getLogger(__name__)


class PokerAdvisor:
    """
    Simple poker advisor with RAG and streaming responses
    """

    # Basic system prompt
    SYSTEM_PROMPT = """You are a helpful poker advisor assistant.

Your role:
- Analyze poker situations and provide strategic advice
- Use poker knowledge to explain concepts clearly
- Be concise but informative
- Reference pot odds and position when relevant

Guidelines:
- Keep responses under 4-5 sentences unless asked for detail
- Use simple language
- Focus on practical advice the player can use right now
"""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        vector_store: Optional[object] = None,
        game_context_provider: Optional[GameContextProvider] = None
    ):
        """
        Initialize poker advisor

        Args:
            ollama_client: Ollama client (creates default if None)
            vector_store: Vector store for RAG (creates in-memory if None)
            game_context_provider: Game context provider
        """
        # Initialize Ollama client
        self.ollama = ollama_client or OllamaClient()

        # Check if Ollama is available
        if not self.ollama.is_available():
            logger.warning(
                "Ollama is not running. Start with: ollama serve\n"
                "Then pull a model: ollama pull phi3:mini"
            )

        # Initialize vector store (use in-memory fallback if Pinecone not configured)
        if vector_store is None:
            try:
                vector_store = PineconePokerStore()
            except Exception as e:
                logger.info(f"Using in-memory store: {e}")
                vector_store = InMemoryPokerStore()

        self.vector_store = vector_store

        # Game context provider
        self.game_context_provider = game_context_provider

        # Load knowledge base if store is empty
        self._maybe_load_knowledge_base()

    def _maybe_load_knowledge_base(self):
        """Load poker knowledge base if not already loaded"""
        try:
            stats = self.vector_store.get_stats()
            total_docs = stats.get('total_vectors', 0)

            if total_docs == 0:
                logger.info("Loading poker knowledge base...")
                loader = PokerDocumentLoader()
                documents = loader.load_all_documents()

                # Convert to format expected by vector store
                docs_for_store = []
                for doc in documents:
                    docs_for_store.append({
                        'id': f"{doc.metadata['filename']}_{doc.metadata['chunk_id']}",
                        'content': doc.content,
                        'metadata': doc.metadata
                    })

                count = self.vector_store.add_documents(docs_for_store)
                logger.info(f"Loaded {count} poker strategy chunks")
            else:
                logger.info(f"Knowledge base already loaded ({total_docs} docs)")

        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")

    def get_advice(
        self,
        user_query: str,
        game_state: Optional[Dict] = None,
        use_rag: bool = True
    ) -> str:
        """
        Get poker advice (non-streaming)

        Args:
            user_query: User's question
            game_state: Current game state dict
            use_rag: Whether to use RAG knowledge base

        Returns:
            Advice text
        """
        # Build context
        context_parts = [self.SYSTEM_PROMPT]

        # Add game context if available
        if game_state and self.game_context_provider:
            game_context = self.game_context_provider.get_full_context()
            context_parts.append(f"\nCurrent Game State:\n{game_context}")

        # Add RAG context if enabled
        if use_rag:
            rag_context = self.vector_store.search_as_context(user_query, k=2)
            context_parts.append(f"\nRelevant Poker Strategy:\n{rag_context}")

        # Build messages
        system_msg = '\n'.join(context_parts)
        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_query}
        ]

        # Get response from Ollama
        try:
            response = self.ollama.chat(messages)
            return response
        except Exception as e:
            logger.error(f"Error getting advice: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def get_advice_stream(
        self,
        user_query: str,
        game_state: Optional[Dict] = None,
        use_rag: bool = True
    ) -> Generator[str, None, None]:
        """
        Get poker advice with streaming response

        Args:
            user_query: User's question
            game_state: Current game state dict
            use_rag: Whether to use RAG knowledge base

        Yields:
            Text chunks as they arrive
        """
        # Build context (same as get_advice)
        context_parts = [self.SYSTEM_PROMPT]

        if game_state and self.game_context_provider:
            game_context = self.game_context_provider.get_full_context()
            context_parts.append(f"\nCurrent Game State:\n{game_context}")

        if use_rag:
            rag_context = self.vector_store.search_as_context(user_query, k=2)
            context_parts.append(f"\nRelevant Poker Strategy:\n{rag_context}")

        system_msg = '\n'.join(context_parts)
        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_query}
        ]

        # Stream response from Ollama
        try:
            for chunk in self.ollama.stream_chat(messages):
                yield chunk
        except Exception as e:
            logger.error(f"Error streaming advice: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"

    def quick_tip(self, situation: str) -> str:
        """
        Get a quick tip for a specific situation

        Args:
            situation: Situation description (e.g., "pocket jacks preflop")

        Returns:
            Quick tip text
        """
        # Search knowledge base
        context = self.vector_store.search_as_context(situation, k=1)

        messages = [
            {'role': 'system', 'content': self.SYSTEM_PROMPT},
            {'role': 'user', 'content': f"Give a quick tip for: {situation}\n\nContext: {context}"}
        ]

        try:
            response = self.ollama.chat(messages, temperature=0.7)
            return response
        except Exception as e:
            return f"Tip not available: {str(e)}"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🃏 Initializing Poker Advisor...")
    advisor = PokerAdvisor()

    # Test non-streaming
    print("\n" + "=" * 60)
    print("TEST 1: Non-streaming advice")
    print("=" * 60)
    query = "Should I call with pocket jacks?"
    print(f"\nQ: {query}")
    print(f"A: {advisor.get_advice(query)}")

    # Test streaming
    print("\n" + "=" * 60)
    print("TEST 2: Streaming advice")
    print("=" * 60)
    query = "What are pot odds?"
    print(f"\nQ: {query}")
    print("A: ", end='', flush=True)

    for chunk in advisor.get_advice_stream(query):
        print(chunk, end='', flush=True)
    print()

    # Test quick tip
    print("\n" + "=" * 60)
    print("TEST 3: Quick tip")
    print("=" * 60)
    print(advisor.quick_tip("playing from button position"))
