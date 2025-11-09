# Knowledge Base Indexing Guide

## Overview

The poker knowledge base consists of 15 markdown files totaling ~150KB of poker strategy content. These files are vectorized and stored in the `poker-knowledge` Pinecone index for semantic search by the LLM advisor.

## Knowledge Base Files

Located in `poker_ev/rag/knowledge_base/`:

### Core Concepts (5 files)
1. **hand_rankings.md** (11.3 KB) - Complete hand strength hierarchy
2. **position_strategy.md** (4.6 KB) - Playing from different positions
3. **opponent_profiling.md** (6.5 KB) - Reading opponent tendencies
4. **probability_fundamentals.md** (5.2 KB) - Basic probability concepts
5. **probability_quick_reference.md** (8.6 KB) - Quick lookup tables

### Probability & Math (6 files)
6. **calculating_outs.md** (8.3 KB) - How to count outs
7. **pot_odds.md** (10.2 KB) - Pot odds concepts
8. **pot_odds_tutorial.md** (9.7 KB) - Step-by-step pot odds
9. **rule_of_2_and_4.md** (7.3 KB) - Quick equity estimation
10. **equity_explained.md** (7.8 KB) - Understanding equity
11. **expected_value_mastery.md** (9.9 KB) - EV calculations

### Advanced Concepts (2 files)
12. **implied_odds_intuition.md** (10.4 KB) - Future betting value
13. **common_probability_mistakes.md** (10.0 KB) - Common errors

### Learning Resources (2 files)
14. **learning_path.md** (13.7 KB) - Progressive curriculum
15. **practice_problems.md** (30.3 KB) - 47 practice problems

**Total:** ~153 KB of poker strategy content

## Indexing Process

The knowledge base is split into **247 chunks** for optimal retrieval:

- **Chunk size:** 800 characters (provides good context)
- **Overlap:** 150 characters (maintains continuity)
- **Embedding model:** all-MiniLM-L6-v2 (384 dimensions)
- **Total vectors:** 247 in Pinecone

### Chunk Distribution

```
Practice Problems:              47 chunks (19%)
Learning Path:                  22 chunks (9%)
Hand Rankings:                  19 chunks (8%)
Implied Odds:                   17 chunks (7%)
Pot Odds:                       16 chunks (6%)
Common Mistakes:                16 chunks (6%)
Pot Odds Tutorial:              16 chunks (6%)
Expected Value:                 15 chunks (6%)
Probability Quick Reference:    14 chunks (6%)
Calculating Outs:               14 chunks (6%)
Equity Explained:               13 chunks (5%)
Rule of 2 and 4:                12 chunks (5%)
Opponent Profiling:             10 chunks (4%)
Probability Fundamentals:        9 chunks (4%)
Position Strategy:               7 chunks (3%)
```

## Re-indexing the Knowledge Base

If you add new files or update existing content, run:

```bash
python scripts/index_knowledge_base.py
```

This script will:
1. Clear the existing `poker-knowledge` index
2. Load all markdown files from `poker_ev/rag/knowledge_base/`
3. Split into optimized chunks
4. Vectorize using all-MiniLM-L6-v2
5. Upload to Pinecone
6. Verify indexing with test queries

**Runtime:** ~30-60 seconds for full re-index

## Testing Search

To verify the knowledge base search is working:

```bash
python tests/test_knowledge_search.py
```

This runs several test queries and shows the retrieved results.

## Usage in Poker Advisor

The LLM poker advisor uses the `search_poker_knowledge` tool to query this index:

```python
# In advisor mode (quick advice)
search_poker_knowledge("pot odds", k=2)  # Returns 2 most relevant chunks

# In tutor mode (teaching)
search_poker_knowledge("pot odds beginner tutorial", k=6)  # Returns 6 chunks for comprehensive teaching
```

### When to Use

**Use poker-knowledge index for:**
- General poker concepts
- Strategy questions
- Learning/teaching requests
- Probability calculations

**Don't use for:**
- Current hand state (use `get_game_state()`)
- Past decision history (use `poker-memory` index)
- Real-time game data

## Metadata Structure

Each chunk has metadata:

```python
{
    "content": "The actual chunk text...",
    "category": "Pot Odds Tutorial",  # Human-readable name
    "source_file": "pot_odds_tutorial",  # Original filename
    "source": "/path/to/pot_odds_tutorial.md"  # Full path
}
```

## Search Performance

The semantic search works excellently:

**Query:** "How do I calculate pot odds?"
- Returns chunks from pot_odds_tutorial.md, pot_odds.md, learning_path.md
- Highly relevant, tutorial-focused content

**Query:** "Explain the rule of 2 and 4"
- Returns chunks from rule_of_2_and_4.md (exact match)
- Supplemented with probability_fundamentals.md

## Adding New Content

To add new knowledge base files:

1. Create markdown file in `poker_ev/rag/knowledge_base/`
2. Use descriptive filename (e.g., `bankroll_management.md`)
3. Write clear, tutorial-style content
4. Run `python scripts/index_knowledge_base.py`
5. Test with `python tests/test_knowledge_search.py`

## Best Practices

### Content Writing
- Use clear headings and structure
- Include examples
- Keep sections focused
- Add practice problems when applicable

### Chunking
- Current settings (800 chars, 150 overlap) work well
- Don't make chunks too small (loses context)
- Don't make chunks too large (less precise retrieval)

### Retrieval
- **k=2-3** for quick advice
- **k=5-8** for teaching/learning
- Test queries to verify relevance

## Troubleshooting

### "No relevant results found"

1. Check if knowledge base is indexed:
   ```python
   from pinecone import Pinecone
   pc = Pinecone(api_key="...")
   index = pc.Index("poker-knowledge")
   stats = index.describe_index_stats()
   print(stats)  # Should show 247 vectors
   ```

2. Re-index if needed:
   ```bash
   python scripts/index_knowledge_base.py
   ```

### "Results not relevant"

- Increase `k` parameter (retrieve more chunks)
- Rephrase the query
- Check if content exists in knowledge base files
- Consider adding new content for that topic

## Maintenance

- **Add new files:** Run indexing script
- **Update existing files:** Re-run indexing script (clears old data)
- **Monitor performance:** Review LLM advisor responses
- **Regular updates:** Keep content current with poker theory
