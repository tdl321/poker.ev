# Card Format Options

## Overview

The `GameContextProvider` now supports **three different card display formats** to ensure compatibility across different environments:

1. **Unicode** (default): Uses card suit symbols `♠♥♦♣`
2. **ASCII**: Uses single letters `s/h/d/c`
3. **Text**: Uses full card names "Ace of spades"

---

## Why Multiple Formats?

### Unicode Format (Default)
- **Best for**: GUI displays, modern terminals, LLM responses
- **Pros**: Visually clear, compact, professional
- **Cons**: May not display correctly in some terminals or systems
- **Example**: `K♦ K♣` (Pocket Kings)

### ASCII Format
- **Best for**: Terminal/console compatibility, logs, debugging
- **Pros**: Works everywhere, no encoding issues
- **Cons**: Less visually distinct (requires reading s/h/d/c)
- **Example**: `Kd Kc` (Pocket Kings)

### Text Format
- **Best for**: Screen readers, accessibility, beginner-friendly output
- **Pros**: Most readable, no ambiguity
- **Cons**: Verbose, takes more space
- **Example**: `King of diamonds, King of clubs` (Pocket Kings)

---

## Usage

### Basic Usage

```python
from poker_ev.llm.game_context import GameContextProvider
from poker_ev.engine.game_wrapper import PokerGame

game = PokerGame(num_players=6, buyin=1000, big_blind=10, small_blind=5)

# Unicode format (default)
context_unicode = GameContextProvider(game, card_format='unicode')

# ASCII format
context_ascii = GameContextProvider(game, card_format='ascii')

# Text format
context_text = GameContextProvider(game, card_format='text')
```

### Example Output

```python
from texasholdem import Card

# Create pocket kings
kd = Card('Kd')
kc = Card('Kc')

# Unicode format
print(context_unicode.cards_to_string([kd, kc]))
# Output: K♦ K♣

# ASCII format
print(context_ascii.cards_to_string([kd, kc]))
# Output: Kd Kc

# Text format
print(context_text.cards_to_string([kd, kc]))
# Output: King of diamonds, King of clubs
```

---

## Format Specifications

### Unicode Format

**Suits**:
- ♠ = Spades
- ♥ = Hearts
- ♦ = Diamonds
- ♣ = Clubs

**Ranks**: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2

**Examples**:
- Single card: `A♠`
- Pair: `K♦ K♣`
- Multiple cards: `A♠ K♥ Q♦`

---

### ASCII Format

**Suits**:
- s = spades
- h = hearts
- d = diamonds
- c = clubs

**Ranks**: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2

**Examples**:
- Single card: `As`
- Pair: `Kd Kc`
- Multiple cards: `As Kh Qd`

---

### Text Format

**Suits**: Full names (spades, hearts, diamonds, clubs)

**Ranks**: Full names (Ace, King, Queen, Jack, Ten, Nine, Eight, Seven, Six, Five, Four, Three, Two)

**Format**: `{Rank} of {suit}`

**Examples**:
- Single card: `Ace of spades`
- Pair: `King of diamonds, King of clubs`
- Multiple cards: `Ace of spades, King of hearts, Queen of diamonds`

**Note**: Multiple cards are **comma-separated** in text format (unlike space-separated in unicode/ascii)

---

## Integration with Poker Advisor

### Default Behavior (GUI)

The pygame GUI uses **unicode format** by default:

```python
# In pygame_gui.py
game_context = GameContextProvider(self.game)  # Uses 'unicode' by default
```

This provides the best visual experience in the GUI chat panel.

### Custom Format

To use a different format, modify the initialization:

```python
# ASCII format for terminal compatibility
game_context = GameContextProvider(self.game, card_format='ascii')

# Text format for accessibility
game_context = GameContextProvider(self.game, card_format='text')
```

---

## LLM Auto-Injection

### What Format is Injected?

The card format used in auto-injected game state depends on the `GameContextProvider` initialization.

**Default** (unicode):
```
[CURRENT GAME STATE]
🃏 YOUR CARDS: K♦ K♣
🎴 BOARD: A♠ 7♠ 2♦
```

**ASCII format**:
```
[CURRENT GAME STATE]
🃏 YOUR CARDS: Kd Kc
🎴 BOARD: As 7s 2d
```

**Text format**:
```
[CURRENT GAME STATE]
🃏 YOUR CARDS: King of diamonds, King of clubs
🎴 BOARD: Ace of spades, Seven of spades, Two of diamonds
```

---

## Recommendation

### For Most Users: **Unicode** (default)

- Works in modern terminals and GUIs
- Best visual clarity
- Compact and professional
- Preferred by LLMs for card recognition

### For Compatibility: **ASCII**

- Guaranteed to work everywhere
- Good for logs, debugging, CI/CD
- No encoding issues

### For Accessibility: **Text**

- Best for screen readers
- Beginner-friendly
- Unambiguous (no symbol confusion)

---

## Testing

All three formats have comprehensive test coverage in `tests/test_card_formats.py`:

```bash
python tests/test_card_formats.py
```

**Output**:
```
✅ PASSED: Unicode Format
✅ PASSED: ASCII Format
✅ PASSED: Text Format
✅ PASSED: Format Comparison
```

---

## Implementation Details

### Format Selection

The `GameContextProvider` constructor accepts a `card_format` parameter:

```python
def __init__(self, game: PokerGame, card_format: str = 'unicode'):
    """
    Args:
        game: PokerGame instance
        card_format: 'unicode', 'ascii', or 'text'
    """
```

### Internal Mappings

**Unicode** (`SUIT_SYMBOLS_UNICODE`):
```python
{1: '♠', 2: '♥', 4: '♦', 8: '♣'}
```

**ASCII** (`SUIT_SYMBOLS_ASCII`):
```python
{1: 's', 2: 'h', 4: 'd', 8: 'c'}
```

**Text** (`SUIT_SYMBOLS_TEXT`):
```python
{1: ' of spades', 2: ' of hearts', 4: ' of diamonds', 8: ' of clubs'}
```

### Rank Mappings

**Compact** (`RANK_SYMBOLS` - used by unicode/ascii):
```python
{12: 'A', 11: 'K', 10: 'Q', 9: 'J', 8: 'T', ...}
```

**Text** (`RANK_NAMES_TEXT` - used by text format):
```python
{12: 'Ace', 11: 'King', 10: 'Queen', 9: 'Jack', 8: 'Ten', ...}
```

---

## Troubleshooting

### Unicode Symbols Not Displaying

**Problem**: Seeing `K? K?` or `K� K�` instead of `K♦ K♣`

**Solution**: Switch to ASCII format:
```python
context = GameContextProvider(game, card_format='ascii')
```

### LLM Not Recognizing Cards

**Problem**: LLM confused about card values

**Solutions**:
1. Check card rank mapping is correct (see `test_card_rank_mapping.py`)
2. Try text format for maximum clarity:
   ```python
   context = GameContextProvider(game, card_format='text')
   ```

### Terminal Encoding Issues

**Problem**: Terminal shows garbled text for unicode symbols

**Solution**: Use ASCII format for terminal-safe output:
```python
context = GameContextProvider(game, card_format='ascii')
```

---

## Future Enhancements

Possible future additions:
- **HTML format**: `<span class="card-spade">A♠</span>`
- **Emoji format**: 🂡 (playing card characters)
- **Mixed format**: Unicode for GUI, ASCII for logs
- **Custom format**: User-defined templates

---

## Status

✅ **All formats implemented and tested**

**Files**:
- `poker_ev/llm/game_context.py` - Implementation
- `tests/test_card_formats.py` - Comprehensive tests
- `docs/CARD_FORMAT_OPTIONS.md` - This documentation

**Default**: Unicode format (best for most use cases)

**Compatibility**: ASCII format (works everywhere)

**Accessibility**: Text format (screen reader friendly)
