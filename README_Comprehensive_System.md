# 🃏 Comprehensive Poker Analysis Suite

A professional-grade poker hand analysis system that extracts and analyzes all the data needed for serious poker study and improvement. This system rivals commercial poker tracking software like PokerTracker and Hold'em Manager.

## 🚀 Features

### **Comprehensive Data Extraction**
- **Raw Hand Data**: Hand ID, site, game type, stakes, timestamps, table info
- **Player Information**: Names, seats, stacks, positions, hole cards, VPIP/PFR eligibility
- **Action Sequences**: Complete action log with timing, amounts, pot tracking
- **Board Cards**: Flop, turn, river with street separation
- **Money Flow**: Pot size, rake, jackpot, side pots, winnings
- **Showdown Data**: Winners, hand rankings, showdown participants

### **Advanced Statistics (50+ Metrics)**
- **Preflop Stats**: VPIP, PFR, 3Bet%, 4Bet%, Steal%, Squeeze%
- **Postflop Stats**: CBet%, Fold-to-CBet%, Donk-bet%, Check-raise%
- **Aggression Metrics**: AF, AFq, Bet sizing distributions
- **Showdown Stats**: WTSD%, W$SD%, WSD amount
- **Positional Analysis**: All stats split by position (UTG, MP, CO, BTN, SB, BB)
- **Stack Depth**: Shallow, Mid, Deep stack analysis
- **Money Metrics**: BB/100, Net won, Hourly rate

### **Interactive Hand Replayer**
- Step-by-step action replay
- Real-time HUD statistics
- Player status tracking (active/folded/current)
- Action timeline with detailed metrics
- Board cards and pot tracking
- Hand analysis and context

### **Leak Detection System**
- Automatic weakness identification
- VPIP/PFR balance analysis
- 3-bet frequency checks
- C-bet frequency analysis
- Aggression factor evaluation
- Positional leak detection

### **Export Capabilities**
- Player statistics CSV
- Actions data CSV
- Hands data CSV
- JSON export options

## 📁 File Structure

```
Parser/
├── comprehensive_parser.py      # Enhanced parser with full data extraction
├── poker_statistics.py         # Statistics calculator with 50+ metrics
├── comprehensive_replayer.py   # Full-featured Streamlit interface
├── test_comprehensive_system.py # Test script to verify functionality
├── README_Comprehensive_System.md # This documentation
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation

1. **Install Python 3.13+** (if not already installed)

2. **Install dependencies:**
   ```bash
   py -3.13 -m pip install streamlit pandas plotly openpyxl
   ```

3. **Verify installation:**
   ```bash
   py -3.13 test_comprehensive_system.py
   ```

## 🎯 Usage

### **Run the Application**
```bash
py -3.13 -m streamlit run comprehensive_replayer.py
```

### **Load Hand Histories**
1. Place your hand history files in a folder (e.g., `TestHands/`)
2. Enter the folder path in the sidebar
3. Click "🔄 Load Hands"

### **Analysis Modes**

#### **1. Hand Replayer**
- Select a hand from the dropdown
- Use controls to step through actions
- View real-time HUD stats for each player
- See action timeline with detailed metrics
- Analyze hand context and board texture

#### **2. Player Statistics**
- Select a player to view comprehensive stats
- See HUD metrics (VPIP, PFR, 3Bet, CBet, AF, etc.)
- View positional breakdowns
- Get leak detection reports

#### **3. Hand Analysis**
- Overall session statistics
- Showdown analysis
- Game type breakdowns
- Pot size analysis

#### **4. Leak Detection**
- Automatic weakness identification for all players
- VPIP/PFR balance checks
- 3-bet frequency analysis
- C-bet frequency analysis
- Aggression factor evaluation

#### **5. Export Data**
- Download player statistics as CSV
- Export actions data for analysis
- Export hands data for database import

## 📊 Statistics Explained

### **Preflop Statistics**
- **VPIP** (Voluntarily Put $ In Pot): % of hands player voluntarily put money in preflop
- **PFR** (Preflop Raise): % of hands player raised preflop
- **3Bet%**: % of hands player 3-bet preflop
- **4Bet%**: % of hands player 4-bet preflop
- **Steal%**: % of hands player attempted to steal blinds
- **Squeeze%**: % of hands player squeezed (raised over limpers)

### **Postflop Statistics**
- **CBet%**: % of flops player continuation bet
- **Fold to CBet%**: % of flops player folded to continuation bet
- **Donk-bet%**: % of flops player donk bet (bet out of position)
- **Check-raise%**: % of flops player check-raised
- **AF** (Aggression Factor): (Bets + Raises) / Calls
- **AFq** (Aggression Frequency): (Bets + Raises) / Total Actions

### **Showdown Statistics**
- **WTSD%** (Went To Showdown): % of hands player reached showdown
- **W$SD** (Won $ at Showdown): Win rate when reaching showdown
- **WSD%** (Won Showdown): % of showdowns player won

### **Positional Statistics**
All stats are broken down by position:
- **UTG** (Under the Gun)
- **MP** (Middle Position)
- **CO** (Cutoff)
- **BTN** (Button)
- **SB** (Small Blind)
- **BB** (Big Blind)

## 🔧 Customization

### **Adding New Statistics**
Edit `poker_statistics.py` to add new metrics:

```python
@dataclass
class PlayerStats:
    # Add your new stat here
    your_new_stat: float = 0.0
```

### **Modifying Parser**
Edit `comprehensive_parser.py` to extract additional data:

```python
def extract_your_data(self, hand_text: str):
    # Add your extraction logic here
    pass
```

### **Customizing UI**
Edit `comprehensive_replayer.py` to modify the interface:

```python
def render_your_component(self):
    # Add your UI component here
    pass
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
py -3.13 test_comprehensive_system.py
```

This will test:
- Parser functionality
- Statistics calculation
- DataFrame creation
- CSV export
- HUD stats generation

## 📈 Data Model

### **Hands Table**
- Hand ID, Site, Game Type, Variant
- Tournament info, Table name, Timestamp
- Stakes, Blinds, Antes, Button seat
- Board cards, Pot size, Rake, Jackpot
- Winner, Winning hand, Hand rank
- Showdown info, Heads up/Multiway flags

### **Actions Table**
- Hand ID, Action order, Player, Action type
- Amount, Total bet, Street, Position
- Pot before/after, Effective stack
- Pot odds, Bet size ratio
- Voluntary/Aggressive flags

### **Players Table**
- Player name, Seat, Starting/ending stack
- Position, Hole cards, VPIP/PFR eligibility
- Showdown status, Cards shown/mucked
- Net won, Final hand, Hand rank

## 🎯 Supported Sites

The parser supports hand histories from:
- PokerStars
- 888poker
- Americas Cardroom (ACR)
- GGPoker
- PartyPoker
- Winamax
- Unibet
- Bet365
- William Hill

## 🔍 Leak Detection Rules

The system automatically detects common poker leaks:

- **VPIP too high**: >25% (should be <25%)
- **VPIP too low**: <15% (should be >15%)
- **PFR too high**: >80% of VPIP
- **PFR too low**: <60% of VPIP
- **3-bet too high**: >8% (should be <8%)
- **3-bet too low**: <3% (should be >3%)
- **C-bet too high**: >80% (should be <80%)
- **C-bet too low**: <50% (should be >50%)
- **Too aggressive**: AF >3 (should be <3)
- **Too passive**: AF <1 (should be >1)

## 🚀 Performance

- **Fast parsing**: Processes hundreds of hands per second
- **Memory efficient**: Optimized data structures
- **Scalable**: Handles large hand history databases
- **Real-time**: Instant HUD stats during replay

## 🤝 Contributing

To add new features:

1. **New Statistics**: Add to `PlayerStats` class in `poker_statistics.py`
2. **New Parser Features**: Add methods to `ComprehensiveParser` class
3. **New UI Components**: Add methods to `ComprehensiveReplayer` class
4. **New Export Formats**: Add methods to export functions

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the test script: `py -3.13 test_comprehensive_system.py`
2. Verify Python version: `py --version` (should be 3.13+)
3. Check dependencies: `py -3.13 -m pip list`
4. Review error messages in the console

## 🎉 Conclusion

This comprehensive poker analysis suite provides everything you need for serious poker study and improvement. With 50+ statistics, interactive replay, leak detection, and export capabilities, it rivals commercial poker tracking software while being completely free and open source.

**Happy analyzing! 🃏📊**

