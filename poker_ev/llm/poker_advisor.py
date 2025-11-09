"""
Poker Advisor - LangChain Agent with RAG

Poker advisor using LangChain agents + DeepSeek API + Pinecone RAG for strategy advice.
"""

import logging
import os
from pathlib import Path
from typing import Generator, Optional, Dict
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

    Uses ReAct agent with 6 specialized tools:
    - search_poker_knowledge: Search poker strategy knowledge base
    - get_game_state: Get current game state
    - calculate_pot_odds: Calculate pot odds mathematically
    - estimate_hand_strength: Estimate hand strength
    - analyze_position: Analyze position advantage
    - get_recent_hands: Get recent hand history chronologically
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

You have access to these 8 specialized tools:

**1. search_poker_knowledge** - RAG knowledge base access
  * For quick advice: use k=2-3 (default)
  * For teaching/learning: use k=5-8 to get comprehensive context
  * Example: search_poker_knowledge("pot odds beginner tutorial", k=6)
  * Use when: Explaining concepts, teaching strategy, answering "what is X?" questions

**2. get_game_state** - Current hand context
  * Returns: Current cards, position, pot, opponents, board
  * Use FIRST when providing situation-specific advice
  * Critical: ONLY use for CURRENT hand, not past hands

**3. calculate_pot_odds** - Pot odds and EV calculator
  * Input: "pot_size,bet_to_call" for basic pot odds
  * Input: "pot_size,bet_to_call,equity" for full EV analysis
  * Input: "pot_size,bet_to_call,equity,teach" for teaching mode with step-by-step explanations
  * Examples:
    - "150,30" → Pot odds only
    - "150,30,35" → Pot odds + EV with 35% equity
    - "150,30,35,teach" → Full teaching mode with detailed probability breakdown
  * Use for: Call/fold decisions, profitability analysis, teaching pot odds/EV

**4. calculate_outs** - Outs and equity calculator (NEW - ESSENTIAL for probability teaching)
  * Input: Draw description like "flush draw on flop", "gutshot straight draw", "9 outs"
  * Returns:
    - Number of outs
    - Equity % using Rule of 2 and 4
    - Exact probability calculations
    - Teaching explanations of the math
  * Use for: Teaching probability, calculating equity for draws, explaining Rule of 2 and 4
  * Example: "flush draw on flop" → "9 outs, 36% equity, detailed probability breakdown"

**5. count_combinations** - Combinatorics calculator (NEW - for probability teaching)
  * Input: Hand descriptions like "AA", "AKs", "pocket pairs", "suited connectors"
  * Returns:
    - Number of combinations
    - Probability of being dealt
    - Teaching explanation of combinatorics
  * Use for: Teaching probability, range analysis, explaining why hands are rare/common
  * Example: "AA" → "6 combinations, 0.45% chance, you'll see AA once every 221 hands"

**6. estimate_hand_strength** - Hand evaluation with equity
  * Input: Hand description like "pocket aces", "AKs", "suited connectors"
  * Returns:
    - Hand strength tier (premium/strong/medium/weak)
    - Equity vs random hand
    - Combinations and probability
    - Strategic recommendations
    - Teaching explanation of why hand is strong/weak
  * Use for: Teaching hand selection, evaluating preflop hands, explaining equity

**7. analyze_position** - Position strategy
  * Input: Position name like "button", "big blind", "early position"
  * Returns: Position strength, advantages/disadvantages, strategy recommendations
  * Use for: Teaching position concepts, positional strategy

**8. get_recent_hands** - Hand history (chronological)
  * Returns: Recent hands sorted by TIME with cards, outcome, profit/loss
  * Use when: "What happened in my last hand?", "Show recent hands", "How have I been doing?"
  * Critical: DO NOT use for current hand analysis - use get_game_state() instead

Tool Usage Patterns:

**For Current Hand Advice:**
1. get_game_state() → See current situation
2. calculate_outs() → Determine equity from draws
3. calculate_pot_odds(pot,bet,equity) → Compare equity vs required
4. Recommend action (fold/call/raise)

**For Teaching Probability:**
1. search_poker_knowledge(topic, k=6) → Get comprehensive tutorial
2. calculate_outs() → Show example calculations
3. count_combinations() → Explain combinatorics
4. calculate_pot_odds(pot,bet,equity,teach) → Teaching mode for EV
5. estimate_hand_strength() → Explain hand equity

**For Quick Answers:**
- Current hand: get_game_state()
- Last hand: get_recent_hands()
- General concepts: search_poker_knowledge(k=2)
- Should I call?: calculate_pot_odds(pot,bet,equity)
- Is this profitable?: calculate_pot_odds with equity (+EV or -EV)
- Hand strength: estimate_hand_strength()
- Position strategy: analyze_position()

**Teaching Mode Triggers:**
- User asks to "teach me", "I want to learn", "explain", "I don't understand"
- Use k=5-8 in search_poker_knowledge for comprehensive context
- Use "teach" parameter in calculate_pot_odds for step-by-step explanations
- Always explain probability concepts using calculate_outs and count_combinations

Expected Value (EV) Guidance:
- Always try to include equity when using calculate_pot_odds for better analysis
- +EV = Profitable call (equity > required equity)
- -EV = Unprofitable call (equity < required equity)
- 0 EV = Break-even call (equity = required equity)

CRITICAL RULE FOR CURRENT HAND ANALYSIS:
When analyzing the user's CURRENT hand:
1. ALWAYS call get_game_state() FIRST to see the current cards, board, and pot
2. The cards from get_game_state() are the ONLY cards you should use for advice about the CURRENT situation
3. DO NOT use cards from get_recent_hands() for current hand advice
   - get_recent_hands() shows PAST hands, not current cards
4. If get_game_state() returns "No active game state available", tell the user there's no active hand

CORRECT Tool Usage for Current Hand:
- User: "What's the best move for my current hand?"
  Step 1: Call get_game_state() → "You have A♣ K♦ on K♠ 4♣ 5♣ flop"
  Step 2: Analyze these CURRENT cards (A♣ K♦) and provide advice
  Step 3: Use calculate_pot_odds if needed for the math

WRONG Tool Usage:
- User: "What's the best move for my current hand?"
  Step 1: Call get_recent_hands() and use those cards → ❌ WRONG! Those are PAST hands
  Step 2: Give advice based on past hand cards → ❌ WRONG! Must use current cards from get_game_state()

The distinction is simple:
- get_game_state() = Current hand's cards (what you HAVE now)
- get_recent_hands() = Past hands' cards (what you HAD before, for reference)
"""

    def __init__(
        self,
        model: str = "deepseek-reasoner",
        api_key: Optional[str] = None,
        vector_store: Optional[object] = None,
        game_context_provider: Optional[GameContextProvider] = None,
        decision_tracker: Optional[object] = None,
        hand_history: Optional[object] = None,
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
            hand_history: HandHistory for searching past hands (optional)
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

        # Hand history
        self.hand_history = hand_history

        # Load knowledge base if store is empty
        self._maybe_load_knowledge_base()

        # Create poker tools
        logger.info("Creating poker advisor tools...")
        poker_tools = PokerTools(
            pinecone_store=self.vector_store,
            game_context_provider=self.game_context_provider,
            decision_tracker=self.decision_tracker,
            hand_history=self.hand_history
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

    def get_advice_stream(
        self,
        user_query: str
    ) -> Generator[str, None, None]:
        """
        Get poker advice with streaming response

        Args:
            user_query: User's question

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
