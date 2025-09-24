"""
Configuration file for the Poker Hand Replayer
Easy customization of UI themes, colors, and layouts
"""

# Color Themes
THEMES = {
    "classic": {
        "table_color": "#0d5016",
        "table_border": "#8B4513",
        "player_bg": "#2c3e50",
        "player_border": "#34495e",
        "hero_bg": "#e67e22",
        "hero_border": "#f39c12",
        "active_bg": "#2ecc71",
        "active_border": "#27ae60",
        "folded_bg": "#7f8c8d",
        "card_bg": "#ffffff",
        "card_border": "#333333",
        "red_card": "#e74c3c",
        "black_card": "#2c3e50",
        "pot_bg": "rgba(0,0,0,0.8)",
        "pot_text": "#ffffff"
    },
    "dark": {
        "table_color": "#1a1a1a",
        "table_border": "#444444",
        "player_bg": "#2d2d2d",
        "player_border": "#555555",
        "hero_bg": "#ff6b35",
        "hero_border": "#ff8c42",
        "active_bg": "#4ecdc4",
        "active_border": "#45b7aa",
        "folded_bg": "#666666",
        "card_bg": "#f8f9fa",
        "card_border": "#333333",
        "red_card": "#ff4757",
        "black_card": "#2c2c2c",
        "pot_bg": "rgba(0,0,0,0.9)",
        "pot_text": "#ffffff"
    },
    "neon": {
        "table_color": "#0a0a0a",
        "table_border": "#00ff00",
        "player_bg": "#1a1a1a",
        "player_border": "#00ffff",
        "hero_bg": "#ff00ff",
        "hero_border": "#ffff00",
        "active_bg": "#00ff00",
        "active_border": "#00ffff",
        "folded_bg": "#333333",
        "card_bg": "#ffffff",
        "card_border": "#00ff00",
        "red_card": "#ff0080",
        "black_card": "#00ffff",
        "pot_bg": "rgba(0,255,0,0.8)",
        "pot_text": "#000000"
    },
    "minimal": {
        "table_color": "#f8f9fa",
        "table_border": "#dee2e6",
        "player_bg": "#ffffff",
        "player_border": "#6c757d",
        "hero_bg": "#007bff",
        "hero_border": "#0056b3",
        "active_bg": "#28a745",
        "active_border": "#1e7e34",
        "folded_bg": "#e9ecef",
        "card_bg": "#ffffff",
        "card_border": "#6c757d",
        "red_card": "#dc3545",
        "black_card": "#212529",
        "pot_bg": "rgba(0,0,0,0.7)",
        "pot_text": "#ffffff"
    }
}

# Table Layouts
TABLE_LAYOUTS = {
    "6max": {
        "seats": 6,
        "positions": {
            1: {"top": "20px", "left": "50%", "transform": "translateX(-50%)"},
            2: {"top": "80px", "left": "20px"},
            3: {"top": "80px", "right": "20px"},
            4: {"bottom": "80px", "right": "20px"},
            5: {"bottom": "80px", "left": "20px"},
            6: {"bottom": "20px", "left": "50%", "transform": "translateX(-50%)"}
        }
    },
    "9max": {
        "seats": 9,
        "positions": {
            1: {"top": "20px", "left": "50%", "transform": "translateX(-50%)"},
            2: {"top": "60px", "left": "30px"},
            3: {"top": "100px", "left": "10px"},
            4: {"top": "100px", "right": "10px"},
            5: {"top": "60px", "right": "30px"},
            6: {"bottom": "60px", "right": "30px"},
            7: {"bottom": "100px", "right": "10px"},
            8: {"bottom": "100px", "left": "10px"},
            9: {"bottom": "60px", "left": "30px"}
        }
    }
}

# Card Styles
CARD_STYLES = {
    "standard": {
        "width": "30px",
        "height": "42px",
        "border_radius": "4px",
        "font_size": "10px"
    },
    "large": {
        "width": "40px",
        "height": "56px",
        "border_radius": "6px",
        "font_size": "12px"
    },
    "small": {
        "width": "24px",
        "height": "34px",
        "border_radius": "3px",
        "font_size": "8px"
    }
}

# Animation Settings
ANIMATIONS = {
    "enabled": True,
    "card_flip_duration": "0.3s",
    "action_highlight_duration": "0.5s",
    "pot_update_duration": "0.2s",
    "player_highlight_duration": "0.3s"
}

# Display Options
DISPLAY_OPTIONS = {
    "show_chip_counts": True,
    "show_positions": True,
    "show_hole_cards": True,
    "show_board_cards": True,
    "show_pot_size": True,
    "show_action_amounts": True,
    "show_hand_rankings": True,
    "show_timestamps": False,
    "show_side_pots": True
}

# Export Options
EXPORT_OPTIONS = {
    "default_format": "json",
    "include_timestamps": True,
    "include_debug_info": False,
    "compress_output": False
}

# Performance Settings
PERFORMANCE = {
    "max_hands_in_memory": 1000,
    "lazy_loading": True,
    "cache_parsed_hands": True,
    "max_actions_display": 1000
}

# Default Configuration
DEFAULT_CONFIG = {
    "theme": "classic",
    "table_layout": "6max",
    "card_style": "standard",
    "animations": ANIMATIONS,
    "display": DISPLAY_OPTIONS,
    "export": EXPORT_OPTIONS,
    "performance": PERFORMANCE
}

def get_theme_css(theme_name: str = "classic") -> str:
    """Generate CSS for the specified theme"""
    theme = THEMES.get(theme_name, THEMES["classic"])
    
    return f"""
    <style>
        :root {{
            --table-color: {theme['table_color']};
            --table-border: {theme['table_border']};
            --player-bg: {theme['player_bg']};
            --player-border: {theme['player_border']};
            --hero-bg: {theme['hero_bg']};
            --hero-border: {theme['hero_border']};
            --active-bg: {theme['active_bg']};
            --active-border: {theme['active_border']};
            --folded-bg: {theme['folded_bg']};
            --card-bg: {theme['card_bg']};
            --card-border: {theme['card_border']};
            --red-card: {theme['red_card']};
            --black-card: {theme['black_card']};
            --pot-bg: {theme['pot_bg']};
            --pot-text: {theme['pot_text']};
        }}
        
        .poker-table {{
            background: radial-gradient(circle, var(--table-color), {theme['table_color']}dd);
            border: 8px solid var(--table-border);
        }}
        
        .player-seat {{
            background: var(--player-bg);
            border: 2px solid var(--player-border);
        }}
        
        .player-seat.hero {{
            background: var(--hero-bg);
            border-color: var(--hero-border);
        }}
        
        .player-seat.active {{
            background: var(--active-bg);
            border-color: var(--active-border);
        }}
        
        .player-seat.folded {{
            background: var(--folded-bg);
        }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
        }}
        
        .card.red {{
            color: var(--red-card);
        }}
        
        .card.black {{
            color: var(--black-card);
        }}
        
        .pot-display {{
            background: var(--pot-bg);
            color: var(--pot-text);
        }}
    </style>
    """

def get_table_layout_css(layout_name: str = "6max") -> str:
    """Generate CSS for the specified table layout"""
    layout = TABLE_LAYOUTS.get(layout_name, TABLE_LAYOUTS["6max"])
    
    css = ""
    for seat, position in layout["positions"].items():
        position_css = "; ".join([f"{prop}: {value}" for prop, value in position.items()])
        css += f"""
        .player-seat.seat-{seat} {{
            {position_css};
        }}
        """
    
    return css

def get_card_style_css(style_name: str = "standard") -> str:
    """Generate CSS for the specified card style"""
    style = CARD_STYLES.get(style_name, CARD_STYLES["standard"])
    
    return f"""
    <style>
        .card {{
            width: {style['width']};
            height: {style['height']};
            border-radius: {style['border_radius']};
            font-size: {style['font_size']};
        }}
    </style>
    """

def get_animation_css() -> str:
    """Generate CSS for animations"""
    if not ANIMATIONS["enabled"]:
        return ""
    
    return f"""
    <style>
        .card {{
            transition: transform {ANIMATIONS['card_flip_duration']} ease-in-out;
        }}
        
        .card:hover {{
            transform: scale(1.1);
        }}
        
        .action-item.current {{
            animation: highlight {ANIMATIONS['action_highlight_duration']} ease-in-out;
        }}
        
        .player-seat.active {{
            animation: pulse {ANIMATIONS['player_highlight_duration']} ease-in-out;
        }}
        
        @keyframes highlight {{
            0% {{ background-color: var(--active-bg); }}
            50% {{ background-color: var(--hero-bg); }}
            100% {{ background-color: var(--active-bg); }}
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
    </style>
    """

def get_full_css(theme: str = "classic", layout: str = "6max", card_style: str = "standard") -> str:
    """Generate complete CSS for the replayer"""
    return (
        get_theme_css(theme) +
        get_table_layout_css(layout) +
        get_card_style_css(card_style) +
        get_animation_css()
    )
