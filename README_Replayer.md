# 🃏 Interactive Poker Hand Replayer

A comprehensive poker hand replayer that works alongside your existing poker parser. Visualize and analyze your poker hands with an interactive interface inspired by programs like PokerTracker.

## ✨ Features

### 🎯 Core Functionality
- **Interactive Poker Table**: Visual representation with player positions, chip counts, and hole cards
- **Step-by-Step Replay**: Navigate through actions with timeline controls
- **Real-time Updates**: See pot sizes, player status, and board cards update as you progress
- **Hand Statistics**: Comprehensive stats for each hand
- **Export Options**: Export hand data to JSON or CSV format

### 🎨 Customization
- **Multiple Themes**: Classic, Dark, Neon, and Minimal themes
- **Table Layouts**: Support for 6-max and 9-max tables
- **Card Styles**: Standard, Large, and Small card sizes
- **Animations**: Smooth transitions and highlights (configurable)
- **Display Options**: Toggle various UI elements on/off

### 📊 Analysis Tools
- **Action Timeline**: Complete history of all betting actions
- **Player Tracking**: Monitor each player's contributions and status
- **Pot Tracking**: See pot size changes throughout the hand
- **Hand Rankings**: Final hand strength and winner information

## 🚀 Quick Start

### Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Replayer**:
   ```bash
   streamlit run launch_replayer.py
   ```

3. **Or run directly**:
   ```bash
   streamlit run poker_replayer.py
   ```

### Basic Usage

1. **Load Hands**: Use the sidebar to specify your hand history folder
2. **Select Hand**: Choose from the dropdown of available hands
3. **Navigate Actions**: Use the controls to step through the hand
4. **Analyze**: View statistics and export data as needed

## 📁 File Structure

```
├── enhanced_parser.py      # Enhanced parser with replayer data
├── poker_replayer.py       # Main replayer application
├── replayer_config.py      # UI customization and themes
├── launch_replayer.py      # Simple launcher script
├── requirements.txt        # Python dependencies
└── README_Replayer.md      # This documentation
```

## 🔧 Parser Updates Required

The enhanced parser extracts additional data needed for the replayer:

### New Data Extracted
- **Player Information**: All players' names, chip counts, positions, and hole cards
- **Action Sequence**: Complete betting actions with amounts and timing
- **Pot Tracking**: Pot size after each action
- **Hand Strength**: Final hand rankings for showdown
- **Timing**: Action order and street progression
- **Showdown Info**: Winner, winning hand, and hand rank

### Data Structures

#### Player Object
```python
@dataclass
class Player:
    name: str
    seat: int
    chips: float
    position: str
    hole_cards: List[str]
    is_hero: bool
    is_active: bool
    is_all_in: bool
    total_contributed: float
    final_hand: str
    hand_rank: str
```

#### Action Object
```python
@dataclass
class Action:
    player: str
    action_type: str  # 'fold', 'call', 'raise', 'bet', 'check', 'all-in'
    amount: float
    total_bet: float
    street: str  # 'preflop', 'flop', 'turn', 'river'
    pot_before: float
    pot_after: float
    timestamp: int
```

## 🎨 Customization Guide

### Themes

The replayer supports multiple visual themes:

```python
# Available themes
THEMES = {
    "classic": {...},  # Traditional poker table look
    "dark": {...},     # Dark mode theme
    "neon": {...},     # Neon/cyberpunk style
    "minimal": {...}   # Clean, minimal design
}
```

### Table Layouts

Support for different table sizes:

```python
# Available layouts
TABLE_LAYOUTS = {
    "6max": {...},  # 6-player table
    "9max": {...}   # 9-player table
}
```

### Card Styles

Customize card appearance:

```python
# Available card styles
CARD_STYLES = {
    "standard": {...},  # Standard size
    "large": {...},     # Larger cards
    "small": {...}      # Smaller cards
}
```

### Configuration

Modify `replayer_config.py` to customize:

- **Colors and themes**
- **Table layouts**
- **Card styles**
- **Animation settings**
- **Display options**
- **Export formats**

## 📊 Usage Examples

### Basic Hand Replay

1. Load your hand histories
2. Select a hand from the dropdown
3. Use the timeline slider to step through actions
4. Observe how the table state changes

### Export Hand Data

1. Select a hand
2. Click "Export to JSON" or "Export to CSV"
3. Download the formatted data

### Customize Appearance

1. Modify `replayer_config.py`
2. Restart the application
3. See your changes applied

## 🔍 Advanced Features

### Action Timeline

The timeline shows:
- All betting actions in chronological order
- Street separations (preflop, flop, turn, river)
- Current action highlighting
- Pot size tracking

### Player Tracking

Monitor each player:
- Chip counts
- Hole cards (when revealed)
- Position at table
- Action history
- Final hand strength

### Hand Analysis

View comprehensive statistics:
- Total actions per hand
- Pot size progression
- Player contributions
- Hand rankings

## 🛠️ Development

### Adding New Themes

1. Add theme to `THEMES` in `replayer_config.py`
2. Define color scheme
3. Restart application

### Adding New Table Layouts

1. Add layout to `TABLE_LAYOUTS` in `replayer_config.py`
2. Define seat positions
3. Update CSS generation

### Extending Parser

Add new data extraction in `enhanced_parser.py`:
1. Create new extraction function
2. Add to `parse_hand_enhanced()`
3. Update data structures if needed

## 🐛 Troubleshooting

### Common Issues

1. **Streamlit not found**: Install with `pip install streamlit`
2. **No hands loaded**: Check folder path and file format
3. **UI not updating**: Refresh browser or restart application
4. **Performance issues**: Reduce number of hands in memory

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Future Enhancements

- **Auto-play functionality** with speed controls
- **Hand comparison** side-by-side
- **Statistics dashboard** across multiple hands
- **Video export** of hand replays
- **Mobile-responsive** design
- **Real-time collaboration** features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by PokerTracker and similar poker analysis tools
- Built with Streamlit for rapid UI development
- Uses Plotly for interactive visualizations

---

**Happy analyzing! 🃏**
