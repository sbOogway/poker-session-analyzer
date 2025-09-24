# 🎯 Poker Statistics Calculation Guide

## **3-Bet% Calculation**

### **Formula:**
```
3-Bet% = (Number of times player 3-bet) / (Number of 3-bet opportunities) × 100
```

### **What counts as a 3-bet opportunity:**
1. **Player faces a raise preflop** (not a call or limp)
2. **Player is in position to 3-bet** (hasn't already acted)
3. **Player is not the original raiser**

### **What counts as a 3-bet:**
1. **Player raises over a previous raise preflop**
2. **This is the first raise by this player in the hand**

### **Example Scenarios:**

**✅ 3-Bet Opportunity:**
```
UTG: raises to $3
Hero: [HAS 3-bet opportunity] - can call, fold, or 3-bet
BTN: folds
```

**✅ 3-Bet Made:**
```
UTG: raises to $3
Hero: raises to $9 [3-BET!]
BTN: folds
```

**❌ No 3-Bet Opportunity:**
```
UTG: calls $1
Hero: [NO 3-bet opportunity] - UTG only called, didn't raise
BTN: folds
```

### **Implementation Issues in Current Code:**
- **Line 207-211**: `_process_preflop_actions()` is **empty**
- **Missing**: 3-bet opportunity detection
- **Missing**: 3-bet counting logic
- **Missing**: 3-bet% calculation in `_calculate_final_percentages()`

---

## **W$SD (Won $ at Showdown) Calculation**

### **Formula:**
```
W$SD = Amount won at showdown
```

### **Key Points:**
- **W$SD** = Dollar amount won specifically at showdown
- **NOT** the same as WSD% (Won Showdown %)
- **NOT** the same as net won for entire hand
- **Only** counts money won when reaching showdown

### **Example:**
```
Hand: Player goes to showdown and wins $50
W$SD = $50 (amount won at showdown)
WSD% = 100% (won this showdown)
WTSD% = 25% (went to showdown 1 out of 4 hands)
```

### **Implementation Issues in Current Code:**
- **Line 51**: `wsd_amount: float = 0.0` (correctly defined)
- **Line 201-205**: Basic tracking but **W$SD calculation is wrong**
- **Line 274**: `stats.wsd = (stats.wsd / stats.wtsd) * 100` (This is WSD%, not W$SD)

---

## **WTSD% (Went to Showdown) Calculation**

### **Formula:**
```
WTSD% = (Number of times went to showdown) / (Total hands played) × 100
```

### **What counts as "went to showdown":**
1. **Player reaches the river** (doesn't fold before river)
2. **At least one other player also reaches river**
3. **Cards are shown** (not mucked)

### **Example:**
```
Hand 1: Player folds on flop → NO
Hand 2: Player reaches river, shows cards → YES
Hand 3: Player folds on turn → NO
Hand 4: Player reaches river, shows cards → YES

WTSD% = (2 / 4) × 100 = 50%
```

---

## **WSD% (Won Showdown) Calculation**

### **Formula:**
```
WSD% = (Number of showdowns won) / (Number of showdowns reached) × 100
```

### **Example:**
```
Player went to showdown 4 times:
- Won showdown 1: YES
- Won showdown 2: NO
- Won showdown 3: YES
- Won showdown 4: NO

WSD% = (2 / 4) × 100 = 50%
```

---

## **Corrected Implementation**

### **3-Bet Calculation:**
```python
def _process_preflop_actions(self, player_actions: List[Action], all_actions: List[Action], stats: PlayerStats):
    """Process preflop actions for statistics with CORRECTED 3-bet calculation"""
    
    player_name = stats.player_name
    has_3bet_opportunity = False
    has_3bet = False
    
    # Find all preflop actions
    preflop_actions = [a for a in all_actions if a.street == 'preflop']
    
    # Check if player had a 3-bet opportunity
    for i, action in enumerate(preflop_actions):
        if action.player == player_name:
            # Check if there was a raise before this player's action
            for j in range(i):
                if preflop_actions[j].action_type == 'raise':
                    has_3bet_opportunity = True
                    break
            
            # Check if this player 3-bet (raised over a previous raise)
            if action.action_type == 'raise' and has_3bet_opportunity:
                has_3bet = True
                break
    
    # Update 3-bet statistics
    if has_3bet_opportunity:
        stats.three_bet_opportunities += 1
        if has_3bet:
            stats.three_bet += 1
```

### **W$SD Calculation:**
```python
def _calculate_final_percentages(self):
    """Calculate final percentage statistics with CORRECTED calculations"""
    for player_name, stats in self.player_stats.items():
        # ... other calculations ...
        
        # W$SD CALCULATION - CORRECTED
        # W$SD = Amount won at showdown (not percentage)
        if stats.wtsd > 0:
            stats.wsd_amount = (stats.wsd_amount / stats.wtsd) if stats.wtsd > 0 else 0
```

---

## **Common Mistakes to Avoid**

### **3-Bet Mistakes:**
1. **Counting all raises as 3-bets** (only raises over previous raises count)
2. **Not tracking opportunities** (need denominator for percentage)
3. **Counting 3-bets when player was original raiser** (that's just a raise)

### **W$SD Mistakes:**
1. **Confusing W$SD with WSD%** (W$SD is dollar amount, WSD% is percentage)
2. **Using net won for entire hand** (W$SD is only showdown winnings)
3. **Not tracking showdown-specific winnings** (need separate tracking)

### **WTSD Mistakes:**
1. **Counting hands where player folded** (must reach showdown)
2. **Not counting hands where player won without showdown** (must reach river)
3. **Confusing with VPIP** (WTSD is about reaching showdown, not entering pot)

---

## **Testing the Calculations**

### **Test Scenario:**
```
UTG: raises to $3
Hero: raises to $9 (3-bet)
BTN: folds
[Goes to showdown, Hero wins $12]
```

### **Expected Results:**
- **Hero 3-Bet Opportunities**: 1
- **Hero 3-Bets Made**: 1
- **Hero 3-Bet%**: 100%
- **Hero WTSD**: 100% (went to showdown)
- **Hero W$SD**: $12 (won at showdown)

---

## **Summary**

The current `poker_statistics.py` file has **two major issues**:

1. **3-Bet%**: Not implemented at all (empty function)
2. **W$SD**: Calculated incorrectly (showing percentage instead of dollar amount)

The corrected implementation properly tracks:
- 3-bet opportunities and 3-bets made
- Showdown winnings in dollars
- Proper percentage calculations

This ensures accurate poker statistics for serious analysis and study.

