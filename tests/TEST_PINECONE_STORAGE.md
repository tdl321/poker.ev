# Pinecone Storage Test Guide

This test verifies that your poker game successfully stores hand data to Pinecone database.

## Prerequisites

1. **Pinecone API Key**: You need a Pinecone API key
   - Sign up at https://www.pinecone.io/
   - Get your API key from the dashboard

2. **Environment Setup**: Create a `.env` file in the project root:
   ```bash
   PINECONE_API_KEY=your-api-key-here
   ```

3. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Test

### Option 1: Full Test (Recommended)

This will create a new game, deal cards, and save to Pinecone:

```bash
python tests/test_game_pinecone_storage.py
```

Or make it executable and run directly:

```bash
chmod +x tests/test_game_pinecone_storage.py
./tests/test_game_pinecone_storage.py
```

### Option 2: Verify Existing Data

To only check what's already stored in Pinecone (without creating new test data):

```bash
python tests/test_game_pinecone_storage.py --verify
```

## What the Test Does

The test performs 5 steps:

### Step 1: Configuration Check ✓
- Verifies Pinecone API key is set
- Confirms environment is configured

### Step 2: Game Initialization ✓
- Creates a 4-player poker game
- Sets up starting chips and blinds

### Step 3: Card Dealing ✓
- Starts a new hand
- Deals cards to all players
- Displays game state (your cards, pot, board)

### Step 4: Save to Pinecone ✓
- Prepares hand data structure
- Generates semantic embeddings
- Stores data to Pinecone vector database

### Step 5: Verification ✓
- Queries Pinecone for recent hands
- Confirms test hand was stored
- Displays retrieved data

## Expected Output

```
======================================================================
  STEP 1: Checking Pinecone Configuration
======================================================================

✅ Pinecone API key found: pc-abc123...

======================================================================
  STEP 2: Initializing Poker Game
======================================================================

✅ Game initialized successfully
   Players: 4
   Starting chips: 1000
   Blinds: 5/10

======================================================================
  STEP 3: Starting Hand and Dealing Cards
======================================================================

✅ Hand started successfully

📊 Game State:
   Hand Active: True
   Phase: HandPhase.PREFLOP
   Pot: $15
   Current Player: Player 2

🃏 Your Cards (Player 0):
   A♠, K♦

🎴 Board: (empty - preflop)

👥 Players:
   Player 0: $995 (bet: $5) [ACTIVE]
   Player 1: $990 (bet: $10) [ACTIVE]
   Player 2: $1000 (bet: $0) [ACTIVE]
   Player 3: $1000 (bet: $0) [ACTIVE]

======================================================================
  STEP 4: Saving Hand Data to Pinecone
======================================================================

Initializing Pinecone store...
✅ Pinecone store initialized

📝 Hand Data to Store:
   Hand ID: test_hand_1234567890
   Cards: A♠, K♦
   Board: Preflop
   Pot: $15
   Phase: HandPhase.PREFLOP

💾 Saving to Pinecone...
✅ Hand data saved to Pinecone successfully!

======================================================================
  STEP 5: Verifying Data Storage in Pinecone
======================================================================

Waiting 2 seconds for Pinecone indexing...
Querying Pinecone for recent hands...
✅ Found 5 hand(s) in database

   Hand 1:
      ID: test_hand_1234567890
      Cards: ["A♠", "K♦"]
      Pot: $15
      Phase: HandPhase.PREFLOP
      Timestamp: 2025-11-08T10:30:45
      ⭐ THIS IS OUR TEST HAND!

✅ Test hand successfully stored and retrieved from Pinecone!

======================================================================
  TEST SUMMARY
======================================================================

✅ All tests passed successfully!

📊 What was tested:
   ✓ Pinecone API connection
   ✓ Game initialization
   ✓ Card dealing and game state
   ✓ Hand data storage to Pinecone
   ✓ Data retrieval from Pinecone

💡 Your game data is being stored to Pinecone successfully!
   You can verify this in your Pinecone dashboard.
```

## Troubleshooting

### Error: "PINECONE_API_KEY not found"
**Solution**: Create a `.env` file with your API key:
```bash
echo "PINECONE_API_KEY=your-key-here" > .env
```

### Error: "No module named 'poker_ev'"
**Solution**: Make sure you're running from the project root:
```bash
cd /Users/skylerlee/School/COSC-243/poker.ev
python tests/test_game_pinecone_storage.py
```

### Error: "Failed to initialize Pinecone"
**Solution**: Check your API key is valid:
1. Log into https://app.pinecone.io/
2. Verify your API key
3. Check your index name is correct (default: "poker-memory")

### Warning: "No hands found in database"
**Solution**: Pinecone indexing can take a few seconds. Try:
```bash
sleep 5 && python tests/test_game_pinecone_storage.py --verify
```

## Verifying in Pinecone Dashboard

1. Go to https://app.pinecone.io/
2. Click on your "poker-memory" index
3. You should see vectors stored with metadata
4. Each vector represents a stored hand with:
   - Cards
   - Board state
   - Pot size
   - Game phase
   - Timestamp
   - Notes

## What Data is Stored?

Each hand stored includes:

- **hand_id**: Unique identifier
- **your_cards**: Your hole cards (e.g., ["A♠", "K♦"])
- **board**: Community cards (e.g., ["Q♥", "J♠", "9♦"])
- **pot**: Total pot size
- **phase**: Game phase (PREFLOP, FLOP, TURN, RIVER)
- **position**: Your position (Button, UTG, etc.)
- **outcome**: win/lose/fold
- **profit**: Net profit/loss for the hand
- **actions_summary**: Summary of actions taken
- **timestamp**: When hand was played
- **notes**: Additional context

## Integration with Main Game

In your main game (`main.py`), hands are automatically stored when:
- A hand completes
- You make significant actions
- The AI advisor analyzes your play

The same storage system used in this test is used throughout the application.

## Next Steps

After verifying storage works:

1. **Run the main game** and play some hands
2. **Check your Pinecone dashboard** to see real game data
3. **Use the AI advisor** which queries this stored data for advice
4. **View hand history** to analyze your play patterns

## Need Help?

- Check the main README.md for general setup
- Review poker_ev/memory/pinecone_store.py for implementation details
- Check poker_ev/memory/hand_history.py for storage API
