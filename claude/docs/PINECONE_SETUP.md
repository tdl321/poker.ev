# Pinecone Setup Guide

## Quick Start

### 1. Get Your Pinecone API Key

1. Go to [https://www.pinecone.io/](https://www.pinecone.io/)
2. Sign up for a free account
3. Create a new project (if prompted)
4. Copy your API key from the dashboard

### 2. Configure Your Environment

Edit the `.env` file in the project root:

```bash
PINECONE_API_KEY=your-actual-api-key-here
```

**Important:** Never commit your `.env` file to git! It's already in `.gitignore`.

### 3. Test Your Connection

```bash
python3 tests/test_pinecone.py
```

This will:
- ✅ Verify your API key
- ✅ Connect to Pinecone
- ✅ Create the `poker-knowledge` index (first time only)
- ✅ Load poker strategy documents (~40 chunks)
- ✅ Test semantic search

**First run takes 30-60 seconds** to upload documents. After that, the knowledge base persists in Pinecone!

### 4. Run the Game

```bash
python3 main.py
```

The poker advisor will now use Pinecone for RAG!

---

## How It Works

### Architecture

```
.env file (PINECONE_API_KEY)
         ↓
    main.py (loads .env)
         ↓
    PygameGUI → PokerAdvisor
                     ↓
              PineconePokerStore
                     ↓
        Pinecone Cloud (poker-knowledge index)
```

### First-Time Setup

1. **Load .env** - `python-dotenv` loads `PINECONE_API_KEY`
2. **Initialize Pinecone** - `PineconePokerStore.__init__()`
3. **Check/Create Index** - `_init_index()` creates `poker-knowledge` if it doesn't exist
4. **Load Documents** - `PokerDocumentLoader` reads markdown files
5. **Upload to Pinecone** - Batch upload with embeddings (sentence-transformers)

### After Setup

Once documents are in Pinecone, they stay there! No need to reload:

1. **Game starts** - `PineconePokerStore` connects to existing index
2. **Check stats** - `get_stats()` shows existing vectors
3. **Skip loading** - If vectors exist, document loading is skipped
4. **Ready to use** - Semantic search works immediately

---

## Pinecone Index Details

**Index Name:** `poker-knowledge`
**Dimension:** 384 (all-MiniLM-L6-v2 embeddings)
**Metric:** Cosine similarity
**Cloud:** AWS
**Region:** us-east-1
**Type:** Serverless (free tier)

### Free Tier Limits

- **Storage:** 1 GB
- **Queries:** Unlimited
- **Indexes:** 1 serverless index

Your poker knowledge base uses ~40 vectors × 384 dimensions = **~15 KB**

You're well within the free tier! 🎉

---

## Document Loading Process

### Source Files

```
poker_ev/rag/knowledge_base/
├── hand_rankings.md      - Hand strength and ranges
├── position_strategy.md  - Position-based play
├── pot_odds.md          - Mathematical concepts
└── opponent_profiling.md - Reading opponents
```

### Loading Pipeline

1. **PokerDocumentLoader** reads markdown files
2. **Text chunking** - 500 chars per chunk, 100 char overlap
3. **Metadata extraction** - filename, category, chunk_id
4. **Embedding generation** - Local sentence-transformers (no API needed)
5. **Upsert to Pinecone** - Batches of 100 vectors

### Example Document Format

```python
{
    'id': 'hand_rankings.md_0',
    'content': 'Premium pairs like AA, KK, and QQ...',
    'metadata': {
        'filename': 'hand_rankings.md',
        'category': 'hand_rankings',
        'chunk_id': 0
    }
}
```

After embedding, becomes:

```python
(
    'hand_rankings.md_0',           # ID
    [0.123, -0.456, 0.789, ...],    # 384-dim vector
    {                                # Metadata
        'content': 'Premium pairs...',
        'filename': 'hand_rankings.md',
        'category': 'hand_rankings',
        'chunk_id': 0
    }
)
```

---

## Search & Retrieval

### Semantic Search

When you ask "Should I call with pocket jacks?":

1. **Query embedding** - `embed_text("Should I call with pocket jacks?")`
2. **Vector search** - Pinecone finds top-k similar vectors (cosine similarity)
3. **Format results** - Return content + metadata
4. **LLM context** - Pass to Ollama as context

### Example Search

```python
from poker_ev.rag.pinecone_store import PineconePokerStore

store = PineconePokerStore()
results = store.search("What are pocket aces?", k=2)

# Returns:
[
    {
        'content': 'Pocket aces (AA) are the strongest...',
        'score': 0.89,
        'metadata': {'category': 'hand_rankings', ...}
    },
    {
        'content': 'Premium pairs should be raised...',
        'score': 0.76,
        'metadata': {'category': 'position_strategy', ...}
    }
]
```

---

## Troubleshooting

### "No Pinecone API key found"

**Problem:** `.env` file not configured
**Solution:** Add `PINECONE_API_KEY=...` to `.env` file

### "Pinecone not installed"

**Problem:** Missing dependency
**Solution:** `pip install pinecone`

### "Failed to initialize Pinecone: Unauthorized"

**Problem:** Invalid API key
**Solution:** Check API key in Pinecone dashboard, update `.env`

### "Index already exists with different dimension"

**Problem:** Index created with wrong settings
**Solution:** Delete index in Pinecone dashboard, run test again

### "Connection timeout"

**Problem:** Network issues
**Solution:** Check internet connection, Pinecone status page

---

## Monitoring & Management

### Check Index Stats

```python
from poker_ev.rag.pinecone_store import PineconePokerStore
store = PineconePokerStore()
print(store.get_stats())
# {'total_vectors': 42, 'dimension': 384}
```

### View in Pinecone Dashboard

1. Go to [https://app.pinecone.io/](https://app.pinecone.io/)
2. Select your project
3. Click on `poker-knowledge` index
4. View stats, browse vectors, test queries

### Delete & Recreate

If you need to start fresh:

1. **Option A - Dashboard:** Delete index in Pinecone UI
2. **Option B - Code:**
   ```python
   from pinecone import Pinecone
   import os

   pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
   pc.delete_index("poker-knowledge")
   ```

3. Run `python3 tests/test_pinecone.py` to recreate

---

## Advanced Configuration

### Change Index Name

Edit `poker_ev/rag/pinecone_store.py`:

```python
def __init__(
    self,
    api_key: Optional[str] = None,
    index_name: str = "my-custom-index",  # Change here
    embedding_model: str = "all-MiniLM-L6-v2",
    dimension: int = 384
):
```

### Use Different Embedding Model

```python
# poker_ev/rag/pinecone_store.py
embedding_model: str = "all-mpnet-base-v2"  # Better quality, larger size
dimension: int = 768  # Must match model dimension
```

### Change Region

```python
# poker_ev/rag/pinecone_store.py (_init_index method)
spec=ServerlessSpec(
    cloud='aws',
    region='eu-west-1'  # Change to your preferred region
)
```

---

## Next Steps

1. ✅ Complete Pinecone setup with `test_pinecone.py`
2. ✅ Run the game with `python3 main.py`
3. ✅ Ask the poker advisor questions in the chat!

Example questions to try:
- "What hand should I play?"
- "Should I call with pocket jacks?"
- "What are pot odds?"
- "How do I play from the button?"

---

## Resources

- **Pinecone Docs:** [https://docs.pinecone.io/](https://docs.pinecone.io/)
- **Pinecone Python Client:** [https://github.com/pinecone-io/pinecone-python-client](https://github.com/pinecone-io/pinecone-python-client)
- **SentenceTransformers:** [https://www.sbert.net/](https://www.sbert.net/)
- **poker.ev RAG Architecture:** See `claude/docs/RAG_ARCHITECTURE.md`
