# Hero Poker Data Analysis Suite

A streamlined poker data analysis system built with Python and Streamlit. This project focuses exclusively on analyzing your (Hero's) poker performance with key metrics and insights.

## Features

- **Hero-Focused Parser**: Extracts only your performance data, not opponents
- **Key Performance Metrics**: Showdown rates, flop win rates, profit tracking
- **Position Analysis**: Performance breakdown by table position
- **Stakes Analysis**: Performance across different stake levels
- **Hand Type Analysis**: Performance by hole card types
- **Export Capabilities**: Download data for further analysis
- **Streamlined Interface**: Focus on data analysis, not hand replay

## Installation

### Prerequisites

- Python 3.11 or higher
- Git (for cloning the repository)
- uv (Python package manager)

### Setup

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/poker-hand-analysis.git
cd poker-hand-analysis
```

2. **Install uv (if not already installed):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Install dependencies:**

```bash
uv sync
```

   This will create a virtual environment and install all dependencies as specified in `pyproject.toml`. The `uv.lock` file ensures reproducible builds.

4. **Run the application:**

```bash
uv run streamlit run src/streamlit_app.py
```

## Usage

### Basic Usage

1. **Load Hand Histories**: Upload your poker hand history files via the application interface
2. **Start the Application**: Run `uv run streamlit run src/streamlit_app.py`
3. **Select Analysis Options**: Choose which metrics and charts to display
4. **Analyze Your Performance**: Review your poker performance with key metrics and insights

### Supported Poker Sites

- GGPoker
- PokerStars
- 888poker
- Americas Cardroom (ACR)
- PartyPoker
- Winamax
- Unibet
- Bet365
- William Hill

### Hand History Format

The parser supports standard poker hand history formats. Place your `.txt` files in the `hand_histories` directory or any subdirectory.

## Configuration

Customize the replayer appearance and behavior by editing `replayer_config.py`:

- **Themes**: Classic, Dark, Neon, Minimal
- **Table Layouts**: 6-max, 9-max
- **Card Styles**: Standard, Large, Small
- **Display Options**: Show/hide various elements

## Statistics Explained

### Preflop Stats

- **VPIP**: Voluntarily Put money In Pot
- **PFR**: Pre-Flop Raise
- **3Bet**: 3-bet percentage
- **Steal**: Steal attempt percentage

### Postflop Stats

- **CBet**: Continuation bet percentage
- **AF**: Aggression Factor
- **WTSD**: Went to Showdown
- **W$SD**: Won $ at Showdown

### Positional Stats

All statistics are broken down by position (UTG, MP, CO, BTN, SB, BB)

## Export Options

- **Player Statistics**: Export to CSV
- **Actions Data**: Export all actions to CSV
- **Hands Data**: Export hand summaries to CSV
- **Individual Hands**: Export specific hands to JSON

## Development

### Running Tests

```bash
uv run python test/test_comprehensive_system.py
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **File Not Found**: Check that hand history files are in the correct directory
3. **Parsing Errors**: Ensure hand history files are in supported format

### Getting Help

- Check the documentation in the code
- Review the test files for examples
- Open an issue on GitHub

## License

This project is open source. Feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Changelog

### Version 1.0.0

- Initial release
- Comprehensive hand parser
- Interactive replayer
- Advanced statistics
- Multiple export options