# 🚀 Quick Start - Poker.ev with AI Chat

## ✅ Dependencies Installed!

All Python packages are now installed. You're almost ready to play!

---

## 🔧 Next Steps

### Option 1: Run Game WITHOUT Chat (Instant)

```bash
python3 main.py
```

The game will work but chat will be disabled if Ollama isn't running.

---

### Option 2: Enable AI Chat (5 minutes setup)

#### Step 1: Install Ollama

**On macOS**:
```bash
# Download and install from: https://ollama.com/download
# OR use Homebrew:
brew install ollama
```

**On Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Step 2: Start Ollama & Pull Model

```bash
# Start Ollama server (keep this running in a terminal)
ollama serve

# In a NEW terminal, pull the AI model
ollama pull llama3.1:8b
```

#### Step 3: Run Game with Chat!

```bash
python3 main.py
```

---

## 🎮 Using the Chat

Once the game is running with Ollama:

1. **Look at the right side** - You'll see "POKER ADVISOR" panel
2. **Click the text input** at the bottom of the chat panel
3. **Type your question**:
   - "Should I call here?"
   - "What are pot odds?"
   - "How do I play pocket jacks?"
4. **Press Enter** - Watch the response stream in real-time!

---

## 🔍 Verify Setup

Check if everything is ready:

```bash
python3 verify_setup.py
```

This will tell you:
- ✅ What's working
- ⚠️  What needs setup
- ❌ What's broken

---

## 🐛 Troubleshooting

### "Chat unavailable" message in game

**Fix**: Ollama isn't running
```bash
# Start Ollama
ollama serve
```

### Chat shows but no responses

**Fix**: Model not downloaded
```bash
ollama pull llama3.1:8b
```

### Import errors

**Fix**: Dependencies not installed
```bash
pip install -r requirements.txt
```

---

## 🎯 What You'll See

### Game Layout

```
┌────────────────────────────┬─────────────────┐
│                            │  POKER ADVISOR  │
│     POKER TABLE            ├─────────────────┤
│                            │  [Chat bubbles  │
│  [Your cards, opponents]   │   appear here   │
│                            │   with retro    │
│  [Board, pot, actions]     │   styling]      │
│                            │                 │
│                            │  💬 ●●●         │
│                            │  (typing...)    │
│                            ├─────────────────┤
│                            │  Type message.. │
└────────────────────────────┴─────────────────┘
```

### Chat Example

**You**: "Should I call with pocket jacks?"

**AI** (streams word-by-word):
> Pocket jacks are a strong hand but vulnerable to overcards. In this position (Button), calling is reasonable. With $150 pot and $30 to call, you're getting 5:1 pot odds which justifies the call. Be cautious on the flop if an ace or king appears.

---

## 📚 Learn More

- **`CHAT_SETUP_GUIDE.md`** - Detailed setup instructions
- **`INTEGRATION_COMPLETE.md`** - Technical overview
- **`IMPLEMENTATION_STATUS.md`** - What was built

---

## 🎉 You're Ready!

**Without chat**:
```bash
python3 main.py
```

**With chat** (after Ollama setup):
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run game
python3 main.py
```

**Enjoy your AI poker coach! 🃏🤖**
