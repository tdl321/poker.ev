# Poker.ev Chat Assistant - Setup Guide

## 🎉 What's New?

Your poker game now includes an **AI Poker Advisor** chat panel with:
- ✅ Always-visible side panel (400px on right)
- ✅ Retro 8-bit styled chat interface
- ✅ **Streaming responses** in real-time with retro fonts
- ✅ RAG-powered poker strategy knowledge
- ✅ Game-aware advice based on current hand
- ✅ Local LLM (free, no API costs)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install & Start Ollama

**Install Ollama** (one-time setup):
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from: https://ollama.com/download
```

**Pull the LLM model**:
```bash
ollama pull llama3.1:8b
```

**Start Ollama server** (keep running in background):
```bash
ollama serve
```

### 3. (Optional) Set Up Pinecone for RAG

The chat works **out-of-the-box** with in-memory storage, but for better performance:

**Get free Pinecone API key**:
- Sign up at: https://www.pinecone.io/
- Create an API key from dashboard

**Set environment variable**:
```bash
export PINECONE_API_KEY="your-api-key-here"
```

Or add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export PINECONE_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Run the Game!

```bash
python main.py
```

---

## 🎮 Using the Chat

### Chat Interface

The chat panel appears on the **right side** of the screen:

```
┌─────────────────────────────┬────────────────────┐
│                             │  POKER ADVISOR     │
│                             ├────────────────────┤
│      POKER TABLE            │  Chat messages     │
│                             │  scroll here       │
│      (Your game)            │                    │
│                             │  ↕ Scrollbar       │
│                             ├────────────────────┤
│                             │  Type here...      │
└─────────────────────────────┴────────────────────┘
      1000px                        400px
```

### How to Use

1. **Click the text input** at bottom of chat panel
2. **Type your question** (e.g., "Should I call here?")
3. **Press Enter** to send
4. **Watch the response stream** in real-time with retro styling!

### Example Questions

**Hand Analysis**:
- "Should I call with pocket jacks?"
- "What should I do here?"
- "Is this a good spot to raise?"

**Strategy**:
- "What are pot odds?"
- "How do I play from the button?"
- "How should I play against the aggressive player?"

**Specific Situations**:
- "I have A-K on a Q-J-10 flop, should I bet?"
- "When should I fold top pair?"
- "How do I calculate my outs?"

### Features

**Game-Aware**:
- Advisor sees your cards, position, pot size
- Knows the current board and phase
- Understands opponent tendencies (AI agent types)

**Streaming Responses**:
- Text appears word-by-word as it's generated
- Typing indicator (bouncing dots) while AI thinks
- Retro fonts match the 8-bit game aesthetic

**Knowledge Base**:
- Hand rankings and equity
- Pot odds and expected value
- Position-based strategy
- Opponent profiling

---

## ⚙️ Configuration

### Disable Chat (if needed)

Edit `main.py`:

```python
# In main() function
gui = PygameGUI(game, agent_manager, enable_chat=False)  # Disable chat
```

### Change LLM Model

For **better quality** (but slower):

```bash
ollama pull llama3.1:70b
```

Then edit `poker_ev/llm/poker_advisor.py`:

```python
self.ollama = OllamaClient(model="llama3.1:70b")  # Higher quality
```

### Adjust Response Style

Edit `poker_ev/llm/poker_advisor.py` and modify `SYSTEM_PROMPT`:

```python
SYSTEM_PROMPT = """You are a professional poker coach.

Your role:
- Provide detailed strategic analysis
- Explain concepts thoroughly
- Use poker terminology
- Reference GTO principles

Guidelines:
- Be comprehensive and educational
- Explain the "why" behind recommendations
- Use specific percentages and odds
"""
```

---

## 🐛 Troubleshooting

### "Ollama not available" error

**Fix**: Make sure Ollama is running:
```bash
# Start Ollama in a terminal
ollama serve

# In another terminal, verify it's working
curl http://localhost:11434/api/tags
```

### Chat panel not showing

**Check**:
1. Window size is at least 1400px wide
2. Chat is enabled: `enable_chat=True` in `main.py`
3. No errors in terminal output

### Slow responses

**Options**:
1. Use smaller model: `llama3.1:8b` (default, fast)
2. Reduce context: Set `use_rag=False` in advisor
3. Upgrade hardware or use GPU acceleration

### Pinecone errors

**Fix**:
- If you see Pinecone errors, the system automatically falls back to **in-memory storage**
- Everything works, just without cloud persistence
- Set `PINECONE_API_KEY` to use cloud storage

### Font issues

If retro fonts don't load:
- System falls back to default Pygame font
- Check `poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf` exists
- Fonts should load automatically from assets

---

## 🧪 Testing

### Test Ollama Connection

```bash
python poker_ev/llm/ollama_client.py
```

Expected output:
```
✅ Ollama is running!
Available models:
  - llama3.1:8b
```

### Test Poker Advisor

```bash
python poker_ev/llm/poker_advisor.py
```

Should show:
- Non-streaming advice
- Streaming advice (word by word)
- Quick tips

### Test Chat Panel Standalone

```bash
python poker_ev/gui/chat/chat_panel.py
```

Opens a window with just the chat panel for testing.

---

## 📊 What's Included

### Files Added

**LLM Integration**:
- `poker_ev/llm/ollama_client.py` - Ollama API client
- `poker_ev/llm/game_context.py` - Game state → text
- `poker_ev/llm/poker_advisor.py` - Main advisor

**RAG System**:
- `poker_ev/rag/pinecone_store.py` - Pinecone vector store
- `poker_ev/rag/document_loader.py` - Load strategy docs
- `poker_ev/rag/knowledge_base/*.md` - Poker strategy (4 files)

**Chat UI**:
- `poker_ev/gui/chat/chat_panel.py` - Main panel
- `poker_ev/gui/chat/message_renderer.py` - Message bubbles
- `poker_ev/gui/chat/chat_input.py` - Text input
- `poker_ev/gui/chat/scroll_handler.py` - Scrolling

**Memory System**:
- `poker_ev/memory/hand_history.py` - Hand storage
- `poker_ev/memory/pattern_tracker.py` - Pattern analysis
- `poker_ev/memory/session_manager.py` - Chat sessions

### Updated Files

- `poker_ev/gui/pygame_gui.py` - Integrated chat panel
- `requirements.txt` - Added dependencies

---

## 💡 Tips

**Best Practices**:
- Ask specific questions about the current hand
- Use the advisor to learn poker concepts
- Try different phrasings if you don't get useful advice
- Scroll up to review previous conversations

**Performance**:
- Streaming responses are fast (appears instantly)
- Full response takes 2-5 seconds depending on model
- Game continues playing while AI responds

**Privacy**:
- Everything runs locally (Ollama)
- No data sent to external APIs (except Pinecone if configured)
- Chat history stored locally in `poker_ev/memory/sessions/`

---

## 🚀 Next Steps

**Try it out**:
1. Start a game: `python main.py`
2. Play a few hands
3. Ask for advice when you're unsure
4. Learn poker strategy in real-time!

**Customize**:
- Adjust system prompts for different coaching styles
- Add your own poker strategy documents to knowledge base
- Experiment with different LLM models

**Extend**:
- Add voice input/output
- Create training mode with quizzes
- Build hand replay with AI commentary
- Export analysis reports

---

## 📞 Support

**Issues**:
- Check terminal output for error messages
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Make sure dependencies installed: `pip install -r requirements.txt`

**Questions**:
- Ollama docs: https://ollama.com/
- Pinecone docs: https://docs.pinecone.io/

---

**Enjoy your AI poker coach! 🃏🤖**
