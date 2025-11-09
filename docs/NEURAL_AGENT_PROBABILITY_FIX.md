# Neural Agent Probability Tensor Fix

**Date:** 2025-11-09
**File:** `model/poker_agent.py`
**Issue:** RuntimeError - probability tensor contains `inf`, `nan` or element < 0

## Problem Summary

The neural agent crashed when sampling actions for inactive players with the error:
```
RuntimeError: probability tensor contains either `inf`, `nan` or element < 0
```

This occurred in `poker_agent.py:283` during `torch.multinomial(action_probs, 1)`.

## Root Cause

**Edge case:** When the neural agent was called for an inactive player (folded or all-in):

1. `get_legal_actions()` returned all `False` (no legal actions available)
2. All action logits were masked to `-inf`
3. `F.softmax([-inf, -inf, -inf, -inf])` produced `[NaN, NaN, NaN, NaN]`
4. `torch.multinomial` cannot sample from `NaN` probabilities → crash

## Fix Implementation

Added two safety checks in the `act()` method (lines 276-298):

### Safety Check 1: No Legal Actions
```python
# Safety check: if no legal actions available, default to fold
if not legal_mask.any():
    print(f"WARNING: No legal actions for player {player_id}. Defaulting to fold.")
    action = 0  # Fold
    raise_amount = 0
    return action, raise_amount, action_logits, value
```

### Safety Check 2: Invalid Probabilities
```python
# Additional safety: check for NaN or Inf in probabilities
if torch.isnan(action_probs).any() or torch.isinf(action_probs).any():
    print(f"WARNING: Invalid probabilities detected. Logits: {masked_logits}, Probs: {action_probs}")
    action = 0  # Fold
    raise_amount = 0
    return action, raise_amount, action_logits, value
```

## Test Results

All edge cases now handled gracefully:

| Test Case | Result | Behavior |
|-----------|--------|----------|
| Normal active player | ✅ Pass | Acts normally |
| Inactive player (folded) | ✅ Pass | Defaults to fold with warning |
| All-in player (no chips) | ✅ Pass | Defaults to fold |

## Prevention

**Why was the agent called for inactive players?**

This suggests a logic issue in the calling code. The neural agent should only be invoked for players who:
- Are active (`env.active_players[player_id] == True`)
- Can act (`env.can_act[player_id] == True`)

**Recommendation:** Add validation in `agent_manager.py` or `neural_agent.py` to check player status before calling the model.

## Related Files

- `model/poker_agent.py` - Fixed action sampling
- `poker_ev/agents/neural_agent.py` - Calls the model
- `poker_ev/agents/agent_manager.py` - Manages agent turns

## Impact

- **Before:** Game crashed when neural agent was called for inactive players
- **After:** Game continues gracefully with warning messages for debugging
