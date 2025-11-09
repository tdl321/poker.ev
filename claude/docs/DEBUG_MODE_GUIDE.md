# Debug Mode Guide - Testing Pinecone Integration

This guide explains how to test and debug Pinecone storage integration while running the full poker application with GUI.

## 🚀 Quick Start

Run the debug version instead of the regular game:

```bash
python main_debug.py
```

Or directly:

```bash
./main_debug.py
```

## 🐛 What Debug Mode Does

The debug version automatically:

1. **✓ Connects to Pinecone** on startup and confirms connection
2. **✓ Tracks every hand** from start to finish
3. **✓ Auto-saves to Pinecone** when each hand completes
4. **✓ Logs to console** with detailed information
5. **✓ Shows debug overlay** in the GUI with live status
6. **✓ Verifies storage** after each save

## 📊 Debug Overlay

The debug overlay appears in the top-left corner showing:

```
🐛 DEBUG INFO
───────────────────────────
Pinecone Status:
  Connection: CONNECTED
  Hands Saved: 5
  Current Hand: Active
  Last Save: SUCCESS

Press 'D' to toggle
```

### Toggle Debug Overlay

- Press **`D`** to show/hide the overlay
- Default: visible

## 📝 Console Output

You'll see detailed logging in your terminal:

### When a Hand Starts

```
======================================================================
🎴 NEW HAND STARTED: hand_1699564823_0
======================================================================
Time: 14:23:43
Phase: HandPhase.PREFLOP
Pot: $15
Your cards: A♠, K♦
======================================================================
```

### When a Hand Completes

```
======================================================================
🏁 HAND COMPLETED: hand_1699564823_0
======================================================================
💾 Saving hand to Pinecone...

📋 Hand Data:
   Cards: A♠, K♦
   Board: Q♥, J♠, 9♦, 8♣, 2♦
   Outcome: won
   Profit: +$45
   Pot: $75

✅ Hand saved successfully!
   Total hands saved: 1
======================================================================
```

## 🎮 Controls

All regular controls plus:

- **D**: Toggle debug overlay on/off
- **Tab**: Toggle AI advisor (still works)
- **F**: Fold
- **C**: Call/Check
- **R**: Raise
- **A**: All In
- **ESC**: Cancel raise

## 🔍 What Data Is Saved

Each hand saves:

- **Hand ID**: Unique identifier (e.g., `hand_1699564823_0`)
- **Timestamp**: When hand started
- **Your Cards**: Hole cards dealt to you (e.g., `["A♠", "K♦"]`)
- **Board**: Community cards (e.g., `["Q♥", "J♠", "9♦"]`)
- **Pot**: Final pot size
- **Phase**: How far the hand went (PREFLOP, FLOP, TURN, RIVER)
- **Position**: Your position (Button, Small Blind, etc.)
- **Outcome**: won/lost/folded/push
- **Profit**: Net chips gained/lost
- **Hand Strength**: Simple categorization (Strong/Medium/Weak)
- **Board Texture**: Analysis of community cards

## 📈 Verifying Storage

### Method 1: Watch the Debug Overlay

The overlay shows:
- Number of hands saved
- Last save status (SUCCESS/FAILED/ERROR)
- Connection status

### Method 2: Console Logs

Check your terminal for:
```
✅ Hand saved successfully!
   Total hands saved: 3
```

### Method 3: Query Pinecone After Playing

After playing a few hands, verify in a separate terminal:

```bash
python tests/test_game_pinecone_storage.py --verify
```

This will show all hands stored in your database.

### Method 4: Pinecone Dashboard

1. Go to https://app.pinecone.io/
2. Click on your `poker-memory` index
3. Check the vector count increasing
4. View metadata for stored hands

## 🧪 Testing Workflow

Here's a complete testing workflow:

### 1. Start Debug Mode

```bash
python main_debug.py
```

### 2. Check Connection

Look for:
```
🔌 Connecting to Pinecone...
✅ Pinecone connection successful!
   Using index: poker-memory
```

### 3. Play a Hand

- Game starts automatically
- Watch the console log when hand starts
- Make your decision (fold/call/raise)
- Watch the console when hand completes

### 4. Verify Save

Check for:
```
✅ Hand saved successfully!
```

### 5. Play More Hands

- The game automatically starts new hands
- Each hand is tracked and saved
- Watch the counter in the debug overlay increase

### 6. Verify All Data

In another terminal:
```bash
python tests/test_game_pinecone_storage.py --verify
```

## 🐞 Troubleshooting

### Debug Mode Won't Start

**Error**: `Failed to connect to Pinecone`

**Solution**: Check your `.env` file has:
```
PINECONE_API_KEY=your-api-key-here
```

### No Debug Overlay Visible

**Solution**: Press `D` to toggle it on

### Hands Not Being Saved

**Check**:
1. Console shows "Hand saved successfully"?
2. Debug overlay shows hands saved count increasing?
3. Any error messages in console?

**Common Issues**:
- API key invalid/expired
- Network connection issues
- Pinecone index doesn't exist

### Want More Detailed Logs

Edit `main_debug.py` and change logging level:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    ...
)
```

## 📊 Comparing Debug vs Regular Mode

| Feature | Regular Mode | Debug Mode |
|---------|-------------|------------|
| Pinecone Auto-save | ❌ No | ✅ Yes |
| Console Logging | Minimal | Detailed |
| Debug Overlay | ❌ No | ✅ Yes |
| Hand Tracking | ❌ No | ✅ Yes |
| Save Verification | ❌ No | ✅ Yes |
| Performance | Faster | Slightly slower |

## 💡 Best Practices

### For Testing Storage

1. **Start with debug mode** to see everything working
2. **Play 5-10 hands** to get good test data
3. **Verify with query script** to confirm storage
4. **Check Pinecone dashboard** for visual confirmation

### For Development

1. **Keep debug mode running** in one terminal
2. **Keep verification script ready** in another terminal
3. **Monitor the overlay** while playing
4. **Check console logs** for any errors

### For Debugging Issues

1. **Look at console first** - most errors appear there
2. **Check the overlay** - shows connection status
3. **Run verification script** - confirms what's in DB
4. **Check Pinecone dashboard** - ultimate source of truth

## 🔄 Integration with Regular Mode

After testing in debug mode, you can integrate into regular mode by:

1. Adding `hand_history` parameter to regular `PygameGUI`
2. Calling `hand_history.save_hand()` when hands complete
3. Removing the debug overlay (or making it optional)

See `poker_ev/gui/pygame_gui_debug.py` for the implementation.

## 📚 Related Files

- **main_debug.py** - Debug mode entry point
- **poker_ev/gui/pygame_gui_debug.py** - Debug GUI implementation
- **tests/test_game_pinecone_storage.py** - Standalone test
- **tests/TEST_PINECONE_STORAGE.md** - Test documentation

## 🎯 Next Steps

After verifying everything works in debug mode:

1. Integrate hand saving into regular `main.py`
2. Add configuration option for auto-save
3. Add hand history viewer in GUI
4. Create analytics dashboard using stored data

## 🆘 Need Help?

If you encounter issues:

1. Check console output for error messages
2. Verify Pinecone API key is correct
3. Run the standalone test: `python tests/test_game_pinecone_storage.py`
4. Check your Pinecone dashboard for any service issues
5. Review logs for connection errors

## 📖 Advanced Usage

### Custom Logging Format

Modify `main_debug.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
```

### Save to File

Add file handler:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Disable Overlay

Pass flag to GUI:

```python
gui = PygameGUIDebug(
    game,
    agent_manager,
    enable_chat=True,
    hand_history=hand_history
)
gui.debug_overlay_visible = False
```

---

Happy debugging! 🐛🎰
