"""
Poker Advisor - LangChain Agent with RAG

Poker advisor using LangChain agents + DeepSeek API + Pinecone RAG for strategy advice.
"""

import logging
import os
from pathlib import Path
from typing import Generator, Optional, Dict, List
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from poker_ev.llm.poker_tools import PokerTools
from poker_ev.llm.game_context import GameContextProvider

logger = logging.getLogger(__name__)


class VectorStoreWrapper:
    """
    Wrapper around LangChain's PineconeVectorStore to provide
    search_as_context method for poker_tools compatibility
    """

    def __init__(self, vector_store: PineconeVectorStore):
        self.vector_store = vector_store

    def search_as_context(self, query: str, k: int = 3) -> str:
        """
        Search and format results as context string for LLM

        Args:
            query: Search query
            k: Number of results (default: 3 for quick answers, use 5-8 for teaching)

        Returns:
            Formatted context string
        """
        try:
            # Use LangChain's similarity_search
            results = self.vector_store.similarity_search(query, k=k)

            if not results:
                return "No relevant poker strategy information found."

            context_parts = []
            for i, doc in enumerate(results, 1):
                category = doc.metadata.get('category', 'Unknown')
                context_parts.append(f"[Source {i}: {category}]")
                context_parts.append(doc.page_content)
                context_parts.append("")

            return '\n'.join(context_parts)
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return "No relevant poker strategy information found."

    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        try:
            # Try to get index stats from Pinecone
            index = self.vector_store._index
            stats = index.describe_index_stats()
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0)
            }
        except Exception as e:
            logger.warning(f"Could not get stats: {e}")
            return {'total_vectors': 0}


class PokerAdvisor:
    """
    LangChain-based poker advisor with RAG and streaming responses

    Uses ReAct agent with 5 specialized tools:
    - search_poker_knowledge: Search poker strategy knowledge base
    - get_game_state: Get current game state
    - calculate_pot_odds: Calculate pot odds mathematically
    - estimate_hand_strength: Estimate hand strength
    - analyze_position: Analyze position advantage
    """

    # Agent system prompt
    SYSTEM_PROMPT = """You are a helpful poker advisor assistant and tutor.

Your dual role:
1. **Advisor Mode**: Analyze poker situations and provide strategic advice
2. **Tutor Mode**: Teach poker probability and strategy concepts progressively

# Advisor Mode (default for situational questions)

When giving advice:
- Analyze poker situations and provide strategic advice
- Use poker knowledge to explain concepts clearly
- Be concise but informative
- Reference pot odds and position when relevant

Guidelines:
- Keep responses under 4-5 sentences unless asked for detail
- Use simple language
- Focus on practical advice the player can use right now

# Tutor Mode (for learning questions)

When user asks to LEARN or UNDERSTAND concepts (not asking about a specific hand):

1. **Assess Current Level**
   - Ask clarifying questions to gauge their knowledge
   - Questions like: "Have you worked with pot odds before?" or "Are you familiar with counting outs?"

2. **Start at Appropriate Level**
   - Beginner (never seen the concept): Use probability_fundamentals.md, simple analogies
   - Intermediate (heard of it): Use calculating_outs.md, pot_odds_tutorial.md
   - Advanced (wants to master): Use expected_value_mastery.md, implied_odds_intuition.md

3. **Progressive Teaching**
   - Present ONE concept at a time
   - Include a simple example
   - Ask if they understand before moving on
   - Reference learning_path.md for structured progression

4. **Check Understanding**
   - After explaining, give a simple practice problem
   - Wait for their answer before continuing
   - Use problems from practice_problems.md

5. **Guide Next Steps**
   - When they master a concept, suggest the next one
   - Follow the progression: Fundamentals → Outs → Pot Odds → EV → Implied Odds
   - Reference learning_path.md for the complete path

**Tutoring Signals** - Switch to tutor mode when user says:
- "Teach me...", "I want to learn...", "How do I understand..."
- "What are pot odds?" (explanation request, not calculation)
- "I don't understand...", "Can you explain..."
- "I'm a beginner", "I'm new to poker"

**Example Tutor Flow**:
User: "I want to learn about pot odds"
You: "I'd be happy to teach you about pot odds! First, are you familiar with counting outs (the cards that improve your hand)? This will help me explain at the right level for you."
[Wait for response]
[If beginner]: "Perfect! Let's start with the basics using a simple analogy..."
[If knows outs]: "Great! Since you know about outs, let's connect that to pot odds..."

You have access to these tools:
- search_poker_knowledge: Search poker strategy knowledge base for hand rankings, position strategy, pot odds, opponent profiling
  * For quick advice: use k=2-3 (default)
  * For teaching/learning: use k=5-8 to get more comprehensive context
  * Example: search_poker_knowledge("pot odds beginner tutorial", k=6)
- get_game_state: Get current game state (cards, position, pot, opponents) - use FIRST when providing situation-specific advice
- calculate_pot_odds: Calculate pot odds (input: "pot_size,bet_to_call")
- estimate_hand_strength: Estimate hand strength (input: hand description like "pocket aces")
- analyze_position: Analyze position advantage (input: position name like "button" or "big blind")
- search_past_decisions: Search YOUR past decisions in similar situations - shows what actions you took before and their outcomes

When to use tools:
- If user asks about their current hand → use get_game_state first
- If user asks about general poker concepts → use search_poker_knowledge
- If user asks "should I call?" → use calculate_pot_odds AND search_past_decisions to see what worked before
- If user asks about a specific hand type → use estimate_hand_strength
- If user asks about position → use analyze_position
- If user wants to know what they did in similar spots → use search_past_decisions
- **In tutor mode**: Use search_poker_knowledge with k=5-8 to retrieve comprehensive learning materials

CRITICAL RULE FOR CURRENT HAND ANALYSIS:
When analyzing the user's CURRENT hand:
1. ALWAYS call get_game_state() FIRST to see the current cards, board, and pot
2. The cards from get_game_state() are the ONLY cards you should use for advice
3. DO NOT use cards from search_past_decisions() - those are from PREVIOUS hands, not the current one
4. search_past_decisions() is ONLY for learning from history, NOT for determining current cards
5. If get_game_state() returns "No active game state available", tell the user there's no active hand

Example:
- User: "What's the best move for my current hand?"
- Step 1: Call get_game_state() → "You have A♣ K♦ on K♠ 4♣ 5♣ flop"
- Step 2: Analyze THESE cards (A♣ K♦), NOT any cards from past hands
- Step 3: Provide advice based on the CURRENT game state
"""

    def __init__(
        self,
        model: str = "deepseek-reasoner",
        api_key: Optional[str] = None,
        vector_store: Optional[object] = None,
        game_context_provider: Optional[GameContextProvider] = None,
        decision_tracker: Optional[object] = None,
        temperature: float = 0.7,
        index_name: str = "poker-knowledge"
    ):
        """
        Initialize LangChain poker advisor agent with DeepSeek API

        Args:
            model: DeepSeek model name (default: deepseek-reasoner)
                Options: "deepseek-reasoner", "deepseek-chat"
            api_key: DeepSeek API key (or set DEEPSEEK_API_KEY env var)
            vector_store: VectorStoreWrapper for RAG (creates default if None)
            game_context_provider: GameContextProvider for current game state
            decision_tracker: DecisionTracker for decision history (optional)
            temperature: LLM temperature (0.0-1.0)
            index_name: Pinecone index name
        """
        # Get DeepSeek API key
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not found in environment. "
                "Add it to .env file or pass as parameter. "
                "Get your API key at: https://platform.deepseek.com/"
            )

        # Initialize DeepSeek via ChatOpenAI (OpenAI-compatible API)
        logger.info(f"Initializing DeepSeek API with model: {model}")
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://api.deepseek.com",
            temperature=temperature
        )

        # Initialize vector store using LangChain + Pinecone
        if vector_store is None:
            logger.info("Initializing Pinecone vector store with LangChain...")

            # Get Pinecone API key
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError(
                    "PINECONE_API_KEY not found in environment. "
                    "Set it in .env or environment variables."
                )

            # Initialize Pinecone client
            pc = Pinecone(api_key=api_key)

            # Check if index exists, create if not
            existing_indexes = pc.list_indexes()
            index_names = existing_indexes.names() if hasattr(existing_indexes, 'names') else \
                          [idx['name'] for idx in existing_indexes]

            if index_name not in index_names:
                logger.info(f"Creating Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric='cosine',
                    spec=ServerlessSpec(cloud='aws', region='us-east-1')
                )
                logger.info(f"Index '{index_name}' created")
            else:
                logger.info(f"Using existing Pinecone index: {index_name}")

            # Initialize embeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            # Create LangChain Pinecone vector store
            # IMPORTANT: text_key must match the field name in Pinecone metadata
            pinecone_store = PineconeVectorStore(
                index_name=index_name,
                embedding=embeddings,
                text_key="content"  # Our vectors use 'content' field, not 'text'
            )

            # Wrap in our compatibility wrapper
            vector_store = VectorStoreWrapper(pinecone_store)

        self.vector_store = vector_store

        # Game context provider
        self.game_context_provider = game_context_provider

        # Decision tracker
        self.decision_tracker = decision_tracker

        # Load knowledge base if store is empty
        self._maybe_load_knowledge_base()

        # Create poker tools
        logger.info("Creating poker advisor tools...")
        poker_tools = PokerTools(
            pinecone_store=self.vector_store,
            game_context_provider=self.game_context_provider,
            decision_tracker=self.decision_tracker
        )
        self.tools = poker_tools.create_tools()
        logger.info(f"Created {len(self.tools)} tools: {[t.name for t in self.tools]}")

        # Create agent with new LangChain v1.0 API
        logger.info("Creating poker advisor agent...")
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.SYSTEM_PROMPT
        )

        logger.info("Poker advisor initialized successfully!")

    def _maybe_load_knowledge_base(self):
        """Load poker knowledge base if not already loaded using LangChain native components"""
        try:
            stats = self.vector_store.get_stats()
            total_docs = stats.get('total_vectors', 0)

            if total_docs == 0:
                logger.info("Loading poker knowledge base with LangChain...")

                # Find knowledge base directory
                current_dir = Path(__file__).parent.parent
                knowledge_base_dir = current_dir / "rag" / "knowledge_base"

                if not knowledge_base_dir.exists():
                    logger.warning(f"Knowledge base directory not found: {knowledge_base_dir}")
                    return

                # Use LangChain's DirectoryLoader to load all .md files
                loader = DirectoryLoader(
                    str(knowledge_base_dir),
                    glob="*.md",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8'}
                )
                documents = loader.load()

                # Add category metadata from filename
                for doc in documents:
                    filename = Path(doc.metadata['source']).stem
                    doc.metadata['category'] = filename.replace('_', ' ').title()

                # Use LangChain's text splitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=100,
                    separators=["\n\n", "\n", " ", ""]
                )
                split_docs = text_splitter.split_documents(documents)

                # Add to vector store using LangChain's add_documents
                self.vector_store.vector_store.add_documents(split_docs)
                logger.info(f"Loaded {len(split_docs)} poker strategy chunks")
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
            game_state: Current game state dict (unused - agent uses get_game_state tool)
            use_rag: Whether to use RAG (unused - agent uses search_poker_knowledge tool)

        Returns:
            Advice text
        """
        try:
            # Run agent with user query (LangChain v1.0 API)
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": user_query}]
            })

            # Extract final text answer from agent messages
            if isinstance(result, dict) and "messages" in result:
                # Iterate through messages from end to find last text response
                for message in reversed(result["messages"]):
                    # Check for content attribute (AIMessage)
                    if hasattr(message, "content") and message.content:
                        # Skip tool call JSON, get actual text response
                        if isinstance(message.content, str) and not message.content.strip().startswith("{"):
                            return message.content
                    # Check for dict format
                    elif isinstance(message, dict) and "content" in message:
                        content = message.get("content", "")
                        if content and not content.strip().startswith("{"):
                            return content

                # If no text found, return last message
                last_message = result["messages"][-1]
                if hasattr(last_message, "content"):
                    return last_message.content
                elif isinstance(last_message, dict):
                    return last_message.get("content", str(result))

            return str(result)
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
            game_state: Current game state dict (unused - agent uses get_game_state tool)
            use_rag: Whether to use RAG (unused - agent uses search_poker_knowledge tool)

        Yields:
            Text chunks for smooth streaming display
        """
        try:
            # Get response from agent (agents with tools need to run synchronously)
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": user_query}]
            })

            # Extract final text answer
            response_text = ""
            if isinstance(result, dict) and "messages" in result:
                for message in reversed(result["messages"]):
                    if hasattr(message, "content") and message.content:
                        if isinstance(message.content, str) and not message.content.strip().startswith("{"):
                            response_text = message.content
                            break
                    elif isinstance(message, dict) and "content" in message:
                        content = message.get("content", "")
                        if content and not content.strip().startswith("{"):
                            response_text = content
                            break

            if not response_text:
                response_text = str(result)

            # Stream response character by character for smooth display
            import time
            for char in response_text:
                yield char
                time.sleep(0.01)  # Small delay for smooth streaming effect

        except Exception as e:
            logger.error(f"Error streaming advice: {e}", exc_info=True)
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            for char in error_msg:
                yield char

    def quick_tip(self, situation: str) -> str:
        """
        Get a quick tip for a specific situation

        Args:
            situation: Situation description (e.g., "pocket jacks preflop")

        Returns:
            Quick tip text
        """
        try:
            # Use agent to get quick tip
            query = f"Give a quick tip for: {situation}"
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": query}]
            })

            # Extract text from response
            if isinstance(result, dict) and "messages" in result:
                last_message = result["messages"][-1]
                if hasattr(last_message, "content"):
                    return last_message.content
                elif isinstance(last_message, dict):
                    return last_message.get("content", "")

            return str(result)
        except Exception as e:
            logger.error(f"Error getting quick tip: {e}")
            return f"Tip not available: {str(e)}"


# Example usage
if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv

    # Load .env file for standalone testing
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    print("🃏 Initializing LangChain Poker Advisor...")
    print("=" * 60)
    advisor = PokerAdvisor()

    # Test non-streaming
    print("\n" + "=" * 60)
    print("TEST 1: Non-streaming advice (agent decides which tools to use)")
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

    print("\n" + "=" * 60)
    print("✅ All tests complete!")
    print("=" * 60)
