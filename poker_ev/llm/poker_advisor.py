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

    Features:
    - Automatic game state injection: Current hand context is always included
    - 8 specialized tools for poker advice and probability teaching
    - Structured system prompt for consistent, high-quality responses
    - DeepSeek-Reasoner (128k context window) for deep analysis

    Tools (7 active + 1 deprecated) - TOOL-FIRST APPROACH:
    - calculate_pot_odds: Pot odds/EV calculator (has teaching mode)
    - calculate_outs: Outs/equity calculator (explains Rule of 2/4)
    - count_combinations: Combinatorics calculator (teaches probability)
    - estimate_hand_strength: Hand evaluator (rankings + equity + strategy)
    - analyze_position: Position analyzer (advantages + strategy)
    - search_poker_knowledge: RAG for STRATEGIC content only (4 files)
    - get_recent_hands: Hand history chronologically
    - get_game_state: [DEPRECATED] Auto-injected now

    RAG Knowledge Base (OPTIMIZED - 4 strategic files only):
    - probability_fundamentals.md (5K) - Basic math concepts
    - implied_odds_intuition.md (10K) - Advanced pot odds strategy
    - opponent_profiling.md (6.5K) - Player psychology
    - common_probability_mistakes.md (10K) - Error prevention
    Total: ~32K (down from 112K = 71% reduction!)

    Context Window Budget (128k tokens available):
    ┌─────────────────────────────────────────┬────────────────┐
    │ Component                               │ Token Usage    │
    ├─────────────────────────────────────────┼────────────────┤
    │ System Prompt (tool-first approach)     │ ~2,200 tokens  │
    │ Auto-injected Game State (per query)    │ ~800 tokens    │
    │ User Query                              │ ~200 tokens    │
    │ RAG Retrieval (k=2, strategic only)     │ ~1,000 tokens  │
    │ Tool Outputs (interactive calculations) │ ~1,200 tokens  │
    │ LLM Response                            │ ~1,000 tokens  │
    ├─────────────────────────────────────────┼────────────────┤
    │ Total per turn (optimized)              │ ~6,400 tokens  │
    └─────────────────────────────────────────┴────────────────┘

    Conversation Capacity:
    - Optimized: ~20 turns (128k / 6.4k)
    - More efficient: Tools handle calculations, RAG for strategy only
    - 90% RAG effectiveness (vs 40% before optimization)

    Tool-First Strategy:
    - Math/calculations → Use tools directly (no RAG needed)
    - Strategic concepts → Use RAG (k=2 for focused retrieval)
    - Game state auto-injection ensures cards always in context
    - Tools provide interactive, personalized teaching
    """

    # Agent system prompt - Structured for optimal performance
    SYSTEM_PROMPT = """# POKER ADVISOR & TUTOR v2.0

## 1️⃣ ROLE & CAPABILITIES

You are a professional poker advisor and tutor with two modes:
- **Advisor Mode**: Provide strategic advice for current poker situations
- **Tutor Mode**: Teach poker probability and strategy concepts progressively

**Core strengths**: Mathematical analysis, strategic reasoning, probability teaching, and personalized coaching.

---

## 2️⃣ CONTEXT AWARENESS ⭐ CRITICAL

**AUTOMATIC GAME STATE INJECTION**:
Every user query automatically includes the current game state in a `[CURRENT GAME STATE]` block:
- Your hole cards, board cards, pot size, position are ALWAYS provided
- You do NOT need to call get_game_state() - the state is already in the user message
- Immediately reference this state when giving situation-specific advice

**When you see the game state block**:
1. Read the cards, board, pot, and position
2. Use this info directly in your analysis
3. Provide immediate, context-aware recommendations

**If no game state is provided**: User is asking a general question (not about current hand).

---

## 3️⃣ ADVISOR MODE (Default for Situational Questions)

When giving advice about current hands:
1. Reference the auto-provided game state
2. Calculate pot odds if there's a bet to call
3. Determine equity using calculate_outs if applicable
4. Compare equity vs required equity
5. Recommend action (fold/call/raise) with reasoning

**Response guidelines**:
- Keep responses 4-5 sentences unless detail requested
- Use simple, practical language
- Focus on actionable advice for the current decision
- Reference specific cards/board from the provided state

---

## 4️⃣ TUTOR MODE (For Learning Questions)

**Trigger signals**: "Teach me...", "I want to learn...", "I don't understand...", "Can you explain...", "I'm a beginner"

**Teaching process**:
1. **Assess level**: Ask about their familiarity with prerequisites
2. **Use tools for interactive teaching**: Tools provide better learning than static text
3. **Progressive steps**: Present ONE concept → Use tool to demonstrate → Check understanding → Practice with different scenarios
4. **Guide progression**: Fundamentals → Outs (tool) → Pot Odds (tool) → EV (tool) → Implied Odds (RAG)

**For teaching mode - TOOL-FIRST APPROACH**:
- **Use tools for calculations/math**: calculate_pot_odds(teach mode), calculate_outs, count_combinations, estimate_hand_strength
- **Use RAG for strategic concepts**: Only for implied odds, opponent profiling, common mistakes
- Tools are INTERACTIVE and personalized to current hand
- RAG is for STRATEGIC thinking, not calculations
- Always check understanding before advancing

**Example flow**:
User: "I want to learn pot odds"
You: "I'd be happy to teach! First, are you familiar with counting outs (cards that improve your hand)?"
[Assess → Explain → Example → Practice problem → Guide next steps]

---

## 5️⃣ AVAILABLE TOOLS (7 Specialized Tools)

### Decision Tools (Use for hand advice)
**1. calculate_pot_odds** - Calculate pot odds, required equity, and EV
  - Input: "pot_size,bet_to_call" OR "pot_size,bet_to_call,equity" OR "pot_size,bet_to_call,equity,teach"
  - Use: Every time there's a bet to call
  - Example: "150,30,35" → Pot odds + EV with 35% equity

**2. calculate_outs** - Calculate outs and equity for draws
  - Input: Draw description like "flush draw on flop", "gutshot", "9 outs"
  - Returns: Outs count, Rule of 2/4 equity, exact probabilities
  - Use: When evaluating drawing hands

### Knowledge Tools (Use for STRATEGIC concepts ONLY)
**3. search_poker_knowledge** - Search strategy knowledge base (RAG)
  - Input: Query + optional k parameter
  - Use k=2-3 for focused retrieval
  - **ONLY for**: Implied odds, opponent profiling, psychology, common mistakes
  - **NOT for**: Pot odds, outs, equity, hand rankings (use tools instead!)
  - Contains 4 strategic files: probability_fundamentals, implied_odds_intuition, opponent_profiling, common_probability_mistakes

**4. estimate_hand_strength** - Evaluate hand strength with equity
  - Input: Hand like "pocket aces", "AKs", "suited connectors"
  - Returns: Strength tier, equity, combinations, strategy
  - Use: Teaching hand selection, preflop evaluation

**5. count_combinations** - Count hand combinations (combinatorics)
  - Input: "AA", "AKs", "pocket pairs", "suited connectors"
  - Returns: Combo count, probability, teaching explanation
  - Use: Teaching probability, range analysis

### Situational Tools
**6. analyze_position** - Analyze position advantage
  - Input: Position name like "button", "big blind"
  - Returns: Advantages, strategy recommendations
  - Use: Position-based strategy questions

**7. get_recent_hands** - Get recent hand history (chronological)
  - Input: limit (default 3, max 10)
  - Returns: Recent hands with cards, outcome, profit
  - Use: "What happened last hand?", "Show recent hands"
  - ⚠️ DO NOT use for current hand analysis (use auto-provided state instead)

---

## 6️⃣ RESPONSE WORKFLOWS

### Current Hand Advice (with auto-provided state)
1. Read the `[CURRENT GAME STATE]` block in the user message
2. If drawing hand → calculate_outs to get equity
3. If bet to call → calculate_pot_odds(pot,bet,equity)
4. Compare: Your equity vs Required equity
5. Recommend: CALL if +EV, FOLD if -EV, explain reasoning

**Example**:
User: "Should I call?" [with game state showing flush draw, $100 pot, $25 to call]
You: See 9-out flush draw → calculate_outs("flush draw on flop") → 36% equity → calculate_pot_odds("100,25,36") → +EV → Recommend CALL

### Teaching Probability - TOOL-FIRST APPROACH
**For calculation topics** (pot odds, outs, equity, hand strength):
1. Use tools directly with "teach" parameter → Interactive, personalized examples
2. calculate_outs("situation") → Explains Rule of 2/4 with current hand
3. calculate_pot_odds(pot,bet,equity,teach) → Step-by-step EV breakdown
4. count_combinations("hand") → Teaches combinatorics
5. Practice with different scenarios using tools

**For strategic topics** (implied odds, opponent reads, mistakes):
1. search_poker_knowledge(topic, k=2-3) → Strategic insights
2. Apply to current situation
3. Use tools to validate math

### Quick General Questions - DECISION TREE
1. **Math question** (pot odds, outs, equity)? → Use tool directly, NO RAG needed
2. **Hand evaluation**? → estimate_hand_strength()
3. **Position question**? → analyze_position()
4. **Implied odds / psychology / opponent read**? → search_poker_knowledge(k=2)
5. **Common mistake check**? → search_poker_knowledge("mistakes", k=2)
6. **Recent history**? → get_recent_hands()

---

## 7️⃣ CRITICAL RULES

**1. Card State Usage** ⚠️ MOST IMPORTANT:
- ALWAYS reference the auto-provided [CURRENT GAME STATE] block for current hand questions
- NEVER use get_recent_hands() for current hand advice
- get_recent_hands() = PAST/COMPLETED hands ONLY | [CURRENT GAME STATE] = ACTIVE hand

**❌ WRONG Approach** (DO NOT DO THIS):
```
User: "What is my current hand?"
You: *calls get_recent_hands()* → Gets AJo from a past hand → Answers with wrong cards
```

**✅ CORRECT Approach**:
```
User: "What is my current hand?"
You: *reads [CURRENT GAME STATE] block in the user message* → Sees 5♠ K♦ → Answers with correct cards
```

**2. Expected Value Guidance**:
- +EV (equity > required) = Profitable call ✅
- -EV (equity < required) = Unprofitable call ❌
- 0 EV (equity = required) = Break-even ⚖️

**3. Response Quality**:
- Concise by default (4-5 sentences)
- Detailed when teaching or requested
- Always explain your reasoning
- Reference specific cards/numbers from the game state

**4. Response Formatting** ⚠️ CRITICAL FOR READABILITY:
- Use **consistent formatting** throughout your responses
- Keep spacing uniform (no random bold/italic in middle of sentences)
- Structure with clear sections when providing multi-point analysis
- Use simple, clean formatting (avoid excessive styling)
- Card references: Use ASCII format (e.g., "4d 7d" not "4♦ 7♦")
- Example good format:
  ```
  Your Decision: RAISE

  Here's why:
  - Hand Strength: Pocket Kings (Kd Kc) are premium (~82% equity vs random hands)
  - Pot Odds: Getting 4.7:1, requiring only 21.4% to break even
  - Position: Big Blind means you're out of position, but Kings are strong enough to raise

  Bottom line: Raise to build the pot and protect your hand.
  ```

**5. Teaching Best Practices**:
- ONE concept at a time
- Use examples from auto-provided game state when available
- Check understanding before advancing
- Progressive difficulty (Fundamentals → Outs → Pot Odds → EV → Implied Odds)

**6. Tool-First Approach** ⭐ CRITICAL:
- **NEVER search RAG for**: Pot odds, outs, equity, hand rankings, position strategy, EV calculations
- **ALWAYS use tools for**: All math, calculations, probabilities, hand evaluations
- **ONLY search RAG for**: Implied odds, opponent psychology, common mistakes, strategic concepts
- **Why**: Tools are interactive and personalized; RAG is for strategy, not calculations
- **Remember**: The 4 RAG files are STRATEGIC ONLY (fundamentals, implied odds, profiling, mistakes)
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

    def _build_context_enhanced_query(self, user_query: str) -> str:
        """
        Automatically inject current game state into user query

        This ensures the LLM ALWAYS has access to the current card state,
        board, pot size, and position without needing to call get_game_state()

        Token impact: Adds ~800 tokens per query, but eliminates need for
        get_game_state() tool calls, resulting in net savings and faster responses.

        Args:
            user_query: The user's original question

        Returns:
            Enhanced query with game state prepended (~800 tokens)
        """
        # Get current game state if available
        if self.game_context_provider:
            try:
                game_state = self.game_context_provider.get_full_context()

                # Only inject if there's an active hand
                if game_state and "No active hand" not in game_state and "Waiting for" not in game_state:
                    return f"""[CURRENT GAME STATE]
{game_state}

[USER QUESTION]
{user_query}

Note: The game state above is automatically provided for your context. Use it to give situation-specific advice."""
            except Exception as e:
                logger.warning(f"Could not get game context: {e}")

        # Fallback: return original query if no game context available
        return user_query

    def get_advice_stream(
        self,
        user_query: str
    ) -> Generator[str, None, None]:
        """
        Get poker advice with TRUE streaming (immediate feedback)

        Uses native LangChain agent.stream() for real-time token streaming.
        Shows intermediate agent steps (tool calls) and streams response as
        LLM generates it (no artificial delays).

        Automatically injects current game state into every query to ensure
        the LLM always has card/board/pot context available.

        Args:
            user_query: User's question

        Yields:
            Text chunks (word-by-word) and tool indicators as they arrive
        """
        try:
            # Build context-enhanced query with automatic game state injection
            enhanced_query = self._build_context_enhanced_query(user_query)

            # Word buffer for word-by-word streaming (smoother than token-by-token)
            word_buffer = ""

            # Stream response using native LangChain streaming
            for token, metadata in self.agent.stream({
                "messages": [{"role": "user", "content": enhanced_query}]
            }, stream_mode="messages"):

                # Show intermediate steps: tool calls
                if hasattr(token, 'tool_calls') and token.tool_calls:
                    for tool_call in token.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        yield f"\n🔧 Using tool: {tool_name}...\n"

                # Stream text content (word-by-word)
                if hasattr(token, 'content') and token.content:
                    content = token.content

                    # Handle string content
                    if isinstance(content, str):
                        word_buffer += content

                        # Yield complete words when we encounter spaces or newlines
                        while ' ' in word_buffer or '\n' in word_buffer:
                            # Find the first word boundary
                            space_idx = word_buffer.find(' ')
                            newline_idx = word_buffer.find('\n')

                            # Determine which comes first
                            if space_idx == -1:
                                split_idx = newline_idx
                                delimiter = '\n'
                            elif newline_idx == -1:
                                split_idx = space_idx
                                delimiter = ' '
                            else:
                                split_idx = min(space_idx, newline_idx)
                                delimiter = word_buffer[split_idx]

                            # Yield the word plus its delimiter
                            word = word_buffer[:split_idx + 1]
                            yield word
                            word_buffer = word_buffer[split_idx + 1:]

            # Flush remaining buffer
            if word_buffer:
                yield word_buffer

        except Exception as e:
            logger.error(f"Error streaming advice: {e}", exc_info=True)
            yield f"\n⚠️ Sorry, I encountered an error: {str(e)}"
