# RAG Architecture - Poker Advisor System

## Overview

The poker.ev AI advisor uses a **Retrieval-Augmented Generation (RAG)** system to provide contextual poker advice. This document explains how the UI, LLM, streaming, and RAG components work together.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ChatPanel (poker_ev/gui/chat/chat_panel.py)             │  │
│  │  - Message display & input                                │  │
│  │  - Scroll handling                                        │  │
│  │  - Event handling                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Poker Advisor Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PokerAdvisor (poker_ev/llm/poker_advisor.py)            │  │
│  │  - Orchestrates RAG pipeline                             │  │
│  │  - Combines context sources                              │  │
│  │  - Manages streaming responses                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
┌──────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  Game Context    │ │ RAG Vector  │ │ Ollama LLM      │
│  Provider        │ │ Store       │ │ Client          │
│                  │ │             │ │                 │
│  - Hand state    │ │ - Poker KB  │ │ - phi3:mini     │
│  - Position      │ │ - Semantic  │ │ - Streaming     │
│  - Pot odds      │ │   search    │ │ - HTTP API      │
│  - Opponents     │ │ - Embeddings│ │                 │
└──────────────────┘ └─────────────┘ └─────────────────┘
```

---

## Component Details

### 1. UI Layer - Chat Panel

**Location:** `poker_ev/gui/chat/`

#### ChatPanel (`chat_panel.py`)
Main chat interface component that manages the user experience.

**Key Features:**
- Message history display
- User input field
- Typing indicators
- Auto-scrolling
- Event handling (keyboard, mouse)

**Flow:**
```python
User types message → ChatPanel.handle_event()
                  → on_message_send callback
                  → PygameGUI._handle_chat_message()
```

#### MessageRenderer (`message_renderer.py`)
Renders chat messages with proper formatting and word wrapping.

**Features:**
- User messages (green/right-aligned)
- AI responses (yellow/left-aligned)
- Word wrapping for long text
- Timestamp display

#### ChatInput (`chat_input.py`)
Handles text input with cursor positioning and editing.

**Features:**
- Text editing with cursor
- Backspace/delete support
- Enter to submit
- Visual feedback

#### ScrollHandler (`scroll_handler.py`)
Manages scrolling through chat history.

**Features:**
- Mouse wheel scrolling
- Auto-scroll to bottom on new messages
- Scroll bar visualization

---

### 2. Poker Advisor - RAG Orchestration

**Location:** `poker_ev/llm/poker_advisor.py`

The `PokerAdvisor` class orchestrates the entire RAG pipeline.

#### Key Methods

##### `get_advice_stream(user_query, game_state, use_rag=True)`
Streaming advice generation with RAG.

**Pipeline:**
```python
1. Build System Prompt
   ↓
2. Add Game Context (if available)
   ├─ Get current hand state
   ├─ Player position & cards
   ├─ Pot odds calculation
   └─ Opponent information
   ↓
3. Add RAG Context (if enabled)
   ├─ Embed user query
   ├─ Search vector store (k=2 chunks)
   └─ Format retrieved knowledge
   ↓
4. Construct Messages
   ├─ System message (context)
   └─ User message (query)
   ↓
5. Stream from Ollama
   └─ Yield chunks as they arrive
```

**Code Example:**
```python
def get_advice_stream(self, user_query, game_state=None, use_rag=True):
    # 1. System prompt
    context_parts = [self.SYSTEM_PROMPT]

    # 2. Game context
    if game_state and self.game_context_provider:
        game_context = self.game_context_provider.get_full_context()
        context_parts.append(f"\nCurrent Game State:\n{game_context}")

    # 3. RAG context
    if use_rag:
        rag_context = self.vector_store.search_as_context(user_query, k=2)
        context_parts.append(f"\nRelevant Poker Strategy:\n{rag_context}")

    # 4. Build messages
    system_msg = '\n'.join(context_parts)
    messages = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_query}
    ]

    # 5. Stream response
    for chunk in self.ollama.stream_chat(messages):
        yield chunk
```

---

### 3. Game Context Provider

**Location:** `poker_ev/llm/game_context.py`

Converts internal game state into LLM-friendly natural language.

#### Key Features

**Hand State:**
```
============================================================
CURRENT HAND
============================================================

🃏 YOUR CARDS: A♠ K♠
📍 POSITION: Button (BTN)

🎯 PHASE: PRE-FLOP

💰 POT: $15
💵 YOUR CHIPS: $1000
📢 TO CALL: $10
📊 MIN RAISE: $10
```

**Opponent Profiling:**
```
OPPONENTS
============================================================

Player 1 (Call Agent (always calls)):
  Position: Small Blind (SB), $990, BET $5, ACTIVE

Player 3 (Aggressive Agent (raises often)):
  Position: Big Blind (BB), $985, BET $10, ACTIVE
```

**Pot Odds Calculation:**
```
Pot Odds Analysis:
  • You need to call: $10
  • Current pot: $15
  • Total pot after call: $25
  • Pot odds: 2.5:1
  • Break-even equity needed: 40.0%
```

---

### 4. RAG Vector Store

**Location:** `poker_ev/rag/`

#### Vector Store Architecture

**Two implementations:**
1. **PineconePokerStore** - Cloud vector database (requires API key)
2. **InMemoryPokerStore** - Local fallback (used when Pinecone unavailable)

#### Knowledge Base

**Location:** `poker_ev/rag/knowledge_base/`

**Documents:**
- `hand_rankings.md` - Hand strength and ranges
- `position_strategy.md` - Position-based play
- `pot_odds.md` - Mathematical concepts
- `opponent_profiling.md` - Reading opponents

#### Document Loading Pipeline

```python
# DocumentLoader (rag/document_loader.py)
1. Load markdown files from knowledge_base/
   ↓
2. Split into chunks (500 chars, 100 overlap)
   ↓
3. Generate embeddings (sentence-transformers)
   ↓
4. Store in vector database with metadata
```

#### Semantic Search

**Query Process:**
```python
user_query = "Should I call with pocket jacks?"
                    ↓
1. Embed query with same model
                    ↓
2. Cosine similarity search in vector store
                    ↓
3. Retrieve top-k most relevant chunks (k=2)
                    ↓
4. Format as context for LLM:

"""
Relevant Poker Strategy:

[Chunk 1 - Score: 0.89]
Premium pairs like JJ-AA are strong hands...

[Chunk 2 - Score: 0.82]
From middle position, consider 3-betting...
"""
```

---

### 5. Ollama LLM Client

**Location:** `poker_ev/llm/ollama_client.py`

Interface to local Ollama service for LLM inference.

#### Configuration

```python
OllamaClient(
    base_url="http://localhost:11434",  # Local Ollama server
    model="phi3:mini",                   # 2.2GB model
    temperature=0.7,                     # Response creativity
    timeout=120                          # Request timeout
)
```

#### Streaming Chat

**HTTP Streaming:**
```python
def stream_chat(self, messages, temperature=None, max_tokens=None):
    payload = {
        "model": self.model,
        "messages": messages,
        "stream": True,  # Enable streaming
        "options": {
            "temperature": temperature or self.temperature
        }
    }

    # Stream response chunks
    response = requests.post(
        f"{self.base_url}/api/chat",
        json=payload,
        stream=True  # HTTP streaming
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if 'message' in data:
                content = data['message'].get('content', '')
                if content:
                    yield content  # Stream to caller
```

**Why Streaming?**
- **Better UX:** Show response as it's generated
- **Perceived speed:** User sees output immediately
- **Responsiveness:** Game doesn't freeze during generation

---

## Complete Data Flow

### Example: User asks "Should I call with pocket jacks?"

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                               │
│    User types in ChatPanel: "Should I call with JJ?"       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. EVENT HANDLING                                           │
│    ChatPanel.on_message_send() → callback                  │
│    PygameGUI._handle_chat_message()                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CONTEXT GATHERING (Parallel)                            │
│                                                              │
│    A. Game Context Provider:                                │
│       - Current hand: J♠ J♣                                │
│       - Position: Button (BTN)                              │
│       - Pot: $25, To call: $10                             │
│       - Opponent bets: Player 3 raised to $20              │
│                                                              │
│    B. RAG Vector Store:                                     │
│       - Embed query: "Should I call with JJ?"              │
│       - Search knowledge base                               │
│       - Retrieve: hand_rankings.md (JJ strategy)           │
│       - Retrieve: position_strategy.md (button play)       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PROMPT CONSTRUCTION                                      │
│                                                              │
│    System Prompt:                                           │
│    "You are a helpful poker advisor..."                    │
│                                                              │
│    + Game State:                                            │
│    "🃏 YOUR CARDS: J♠ J♣                                   │
│     📍 POSITION: Button (BTN)                              │
│     💰 POT: $25, TO CALL: $10..."                          │
│                                                              │
│    + RAG Context:                                           │
│    "Relevant Strategy:                                      │
│     JJ is a strong hand but vulnerable to overs..."        │
│                                                              │
│    User Query:                                              │
│    "Should I call with JJ?"                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. LLM STREAMING                                            │
│                                                              │
│    Thread 1 (Background):                                   │
│    ┌────────────────────────────────────────────┐          │
│    │ OllamaClient.stream_chat()                 │          │
│    │   ↓                                         │          │
│    │ HTTP POST to localhost:11434/api/chat     │          │
│    │   ↓                                         │          │
│    │ phi3:mini generates response               │          │
│    │   ↓                                         │          │
│    │ Stream chunks: ["With", " pocket", " jacks"]│          │
│    └────────────────────────────────────────────┘          │
│                                                              │
│    Thread 2 (Main - Game Loop):                            │
│    - Game continues running at 60 FPS                      │
│    - User can still interact with table                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. RESPONSE DISPLAY                                         │
│                                                              │
│    ChatPanel displays:                                      │
│    ┌──────────────────────────────────────────┐            │
│    │ You: Should I call with JJ?              │            │
│    │                                  15:24   │            │
│    ├──────────────────────────────────────────┤            │
│    │ Poker Advisor: With pocket jacks from   │            │
│    │ the button, this is a strong hand.      │            │
│    │ Given the pot odds (2.5:1) and your    │            │
│    │ position, calling is reasonable. However,│            │
│    │ consider 3-betting against loose        │            │
│    │ opponents to build the pot with premium │            │
│    │ equity.                          15:24   │            │
│    └──────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## Threading Model

### Why Threading?

**Problem:** LLM inference takes 2-10 seconds
**Solution:** Run in background thread

```python
def _handle_chat_message(self, message: str):
    game_state = self.game.get_game_state()

    def stream_response():
        # Runs in background thread
        self.chat_panel.set_typing(True)

        full_response = ""
        for chunk in self.poker_advisor.get_advice_stream(message, game_state):
            full_response += chunk

        self.chat_panel.add_ai_response(full_response)

    # Start background thread
    thread = threading.Thread(target=stream_response, daemon=True)
    thread.start()

    # Main thread continues - game keeps running!
```

**Benefits:**
- Game runs at 60 FPS during LLM generation
- User can continue playing while waiting for advice
- Typing indicator shows advisor is "thinking"

---

## Performance Considerations

### Model Selection

**phi3:mini (2.2 GB)**
- **Inference speed:** 20-50 tokens/sec on CPU
- **Quality:** Good for poker advice
- **Memory:** 3-4 GB RAM during inference

**Alternatives:**
- `qwen2.5-coder:7b` - Better reasoning (slower)
- `deepseek-r1:7b` - Chain-of-thought (much slower)

### RAG Optimization

**Vector Store:**
- In-memory: Fast (0.01ms search)
- Pinecone: Slower (50-100ms) but scalable

**Chunking Strategy:**
- Chunk size: 500 chars
- Overlap: 100 chars
- Ensures complete concepts in each chunk

**Retrieval:**
- k=2 chunks (balance context vs prompt size)
- Cosine similarity threshold: 0.7
- Total context: ~1000 chars from knowledge base

---

## Configuration & Customization

### Change LLM Model

```python
# In poker_ev/llm/ollama_client.py
client = OllamaClient(model="qwen2.5-coder:7b")
```

### Adjust RAG Retrieval

```python
# In poker_ev/llm/poker_advisor.py
# Line 132: Change k value
rag_context = self.vector_store.search_as_context(user_query, k=3)  # More context
```

### Modify System Prompt

```python
# In poker_ev/llm/poker_advisor.py
# Lines 23-35: Edit SYSTEM_PROMPT
SYSTEM_PROMPT = """Your custom instructions here..."""
```

### Temperature Control

```python
# Higher = more creative, Lower = more deterministic
client = OllamaClient(temperature=0.9)  # More creative
client = OllamaClient(temperature=0.3)  # More focused
```

---

## Error Handling

### Ollama Not Running
```
Error: Cannot connect to Ollama
→ Check: ollama serve is running
→ Check: Model downloaded (ollama list)
```

### Out of Memory
```
Error: Ollama request timed out
→ Use smaller model (phi3:mini)
→ Close other applications
→ Reduce max_tokens parameter
```

### RAG Failures
```
Warning: Pinecone not initialized
→ Fallback: InMemoryPokerStore
→ No API key needed for in-memory mode
```

---

## Future Enhancements

### Planned Improvements

1. **Multi-turn Conversations**
   - Maintain chat history
   - Follow-up questions with context

2. **Advanced RAG**
   - Re-ranking retrieved chunks
   - Query expansion
   - Hybrid search (semantic + keyword)

3. **Performance**
   - Quantized models for faster inference
   - Caching common queries
   - Batch processing

4. **Features**
   - Hand history analysis
   - Opponent modeling from game data
   - Personalized advice based on play style

---

## References

### Code Locations

- **UI:** `poker_ev/gui/chat/`
- **LLM:** `poker_ev/llm/`
- **RAG:** `poker_ev/rag/`
- **Knowledge Base:** `poker_ev/rag/knowledge_base/`

### Dependencies

- **Ollama:** Local LLM runtime
- **sentence-transformers:** Embeddings
- **langchain:** RAG framework
- **pygame:** UI rendering
- **requests:** HTTP client

### External Documentation

- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Sentence Transformers](https://www.sbert.net/)

---

## Summary

The poker.ev RAG system combines:
1. **Real-time game context** - Current hand, position, odds
2. **Semantic knowledge retrieval** - Poker strategy from vector DB
3. **LLM generation** - Natural language advice with phi3:mini
4. **Streaming UI** - Responsive chat interface

All components work together to provide contextual, real-time poker advice while maintaining smooth gameplay at 60 FPS.
