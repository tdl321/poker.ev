"""
Test card rank parsing with Ten (T) to ensure no int() errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from poker_ev.llm.poker_tools import estimate_hand_strength


def test_ten_rank_parsing():
    """Test that Ten (T) rank doesn't cause int() errors"""
    print("\n" + "="*70)
    print("TEST: Ten (T) Rank Parsing")
    print("="*70)

    test_cases = [
        ("Ts", "Ten of spades"),
        ("Th", "Ten of hearts"),
        ("Td", "Ten of diamonds"),
        ("Tc", "Ten of clubs"),
        ("TT", "Pocket Tens"),
        ("AT", "Ace-Ten"),
        ("ATs", "Ace-Ten suited"),
        ("KT", "King-Ten"),
        ("T9s", "Ten-Nine suited"),
    ]

    print("\n🃏 Testing hands with Ten (T):")
    all_passed = True

    for hand_input, description in test_cases:
        print(f"\n   Testing: {hand_input} ({description})")
        try:
            result = estimate_hand_strength(hand_input)

            # Check that result doesn't contain error message
            if "error" in result.lower() and "invalid literal" in result.lower():
                print(f"      ❌ FAILED: Got int() conversion error")
                all_passed = False
            else:
                print(f"      ✅ PASSED: No int() error")

                # Print first line of result
                first_line = result.split('\n')[0]
                print(f"      Result: {first_line[:60]}...")

        except ValueError as e:
            if "invalid literal for int()" in str(e):
                print(f"      ❌ FAILED: {e}")
                all_passed = False
            else:
                raise
        except Exception as e:
            print(f"      ⚠️  Unexpected error: {e}")
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("   Ten (T) rank parsing works correctly")
    else:
        print("❌ SOME TESTS FAILED")
        print("   int() conversion error still present")
    print("="*70)

    assert all_passed, "Ten rank parsing tests failed!"


if __name__ == "__main__":
    test_ten_rank_parsing()
