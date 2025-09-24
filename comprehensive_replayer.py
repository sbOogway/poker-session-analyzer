import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import glob
from typing import List, Dict, Any, Optional
from comprehensive_parser import parse_file_comprehensive, HandData, Player, Action
from poker_statistics import PokerStatisticsCalculator, create_actions_dataframe, create_hands_dataframe
import json
from datetime import datetime
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Comprehensive Poker Analysis Suite",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 5px 0;
    }
    
    .stat-highlight {
        background: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
    }
    
    .leak-warning {
        background: #ffebee;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    
    .leak-success {
        background: #e8f5e8;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
    
    .player-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid #dee2e6;
    }
    
    .player-card.hero {
        border-color: #ffc107;
        background: #fff3cd;
    }
    
    .player-card.active {
        border-color: #28a745;
        background: #d4edda;
    }
    
    .action-timeline {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #007bff;
    }
    
    .action-item {
        padding: 8px 0;
        border-bottom: 1px solid #dee2e6;
    }
    
    .action-item.current {
        background: #e3f2fd;
        border-radius: 5px;
        padding: 8px;
    }
    
    .street-header {
        background: #007bff;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class ComprehensiveReplayer:
    def __init__(self):
        self.hands = []
        self.current_hand_index = 0
        self.current_action = 0
        self.stats_calculator = PokerStatisticsCalculator()
    
    def load_hands(self, folder_path: str) -> List[HandData]:
        """Load all hands from the specified folder"""
        try:
            file_pattern = os.path.join(folder_path, '**', '*.txt')
            all_files = glob.glob(file_pattern, recursive=True)
            
            all_hands = []
            for filepath in all_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                hands = parse_file_comprehensive(text)
                all_hands.extend(hands)
            
            # Calculate statistics
            self.stats_calculator.load_hands(all_hands)
            self.stats_calculator.calculate_all_stats()
            
            return all_hands
        except Exception as e:
            st.error(f"Error loading hands: {e}")
            return []
    
    def render_player_card(self, player: Player, is_active: bool = False, is_current: bool = False, stats: Dict = None):
        """Render a player card with comprehensive information"""
        card_class = "player-card"
        if player.is_hero:
            card_class += " hero"
        if is_active:
            card_class += " active"
        
        # Get player statistics
        hud_stats = self.stats_calculator.generate_hud_stats(player.name) if stats is None else stats
        
        return f'''
        <div class="{card_class}">
            <h4>{player.name} {"🎯" if is_current else "⭐" if player.is_hero else ""}</h4>
            <p><strong>Seat {player.seat}</strong> - {player.position}</p>
            <p><strong>Chips:</strong> ${player.starting_stack:.2f}</p>
            <p><strong>Cards:</strong> {' '.join(player.hole_cards) if player.hole_cards else 'Hidden'}</p>
            {f'<p><strong>VPIP:</strong> {hud_stats.get("VPIP", "N/A")} | <strong>PFR:</strong> {hud_stats.get("PFR", "N/A")} | <strong>3Bet:</strong> {hud_stats.get("3Bet", "N/A")}</p>' if hud_stats else ''}
            {f'<p><strong>AF:</strong> {hud_stats.get("AF", "N/A")} | <strong>WTSD:</strong> {hud_stats.get("WTSD", "N/A")} | <strong>Hands:</strong> {hud_stats.get("Hands", "N/A")}</p>' if hud_stats else ''}
        </div>
        '''
    
    def render_action_timeline(self, hand: HandData, current_index: int = None):
        """Render the action timeline with comprehensive information"""
        if not hand or not hand.actions:
            return ""
        
        timeline_html = ""
        current_street = None
        
        for i, action in enumerate(hand.actions):
            # Add street header if street changed
            if action.street != current_street:
                current_street = action.street
                timeline_html += f'<div class="street-header">{action.street.upper()}</div>'
            
            # Determine if this is the current action
            is_current = i == current_index
            item_class = "action-item"
            if is_current:
                item_class += " current"
            
            # Format action text with additional info
            action_text = f"{action.player} {action.action_type}"
            if action.amount > 0:
                action_text += f" ${action.amount:.2f}"
            if action.total_bet > 0:
                action_text += f" (total: ${action.total_bet:.2f})"
            
            # Add position and bet sizing info
            position_info = f" [{action.position}]" if action.position else ""
            bet_size_info = f" ({action.bet_size_ratio:.1%} pot)" if action.bet_size_ratio > 0 else ""
            
            timeline_html += f'''
            <div class="{item_class}">
                <strong>{action_text}{position_info}{bet_size_info}</strong>
                <div style="font-size: 12px; color: #6c757d;">
                    Pot: ${action.pot_after:.2f} | Stack: ${action.effective_stack:.2f} | 
                    {'Aggressive' if action.is_aggressive else 'Passive'} | 
                    {'Voluntary' if action.is_voluntary else 'Forced'}
                </div>
            </div>
            '''
        
        return f'<div class="action-timeline">{timeline_html}</div>'
    
    def render_hand_analysis(self, hand: HandData):
        """Render comprehensive hand analysis"""
        analysis_html = ""
        
        # Hand context
        analysis_html += f'''
        <div class="stat-highlight">
            <h4>Hand Context</h4>
            <p><strong>Game Type:</strong> {hand.game_type} {hand.variant}</p>
            <p><strong>Stakes:</strong> {hand.stakes}</p>
            <p><strong>Players:</strong> {hand.number_of_players} | <strong>Heads Up:</strong> {'Yes' if hand.is_heads_up else 'No'} | <strong>Multiway:</strong> {'Yes' if hand.is_multiway else 'No'}</p>
            <p><strong>Showdown:</strong> {'Yes' if hand.went_to_showdown else 'No'}</p>
        </div>
        '''
        
        # Board analysis
        if hand.board_cards:
            analysis_html += f'''
            <div class="stat-highlight">
                <h4>Board Analysis</h4>
                <p><strong>Flop:</strong> {' '.join(hand.flop_cards)}</p>
                <p><strong>Turn:</strong> {hand.turn_card}</p>
                <p><strong>River:</strong> {hand.river_card}</p>
            </div>
            '''
        
        # Action summary
        action_summary = {
            'preflop': len([a for a in hand.actions if a.street == 'preflop']),
            'flop': len([a for a in hand.actions if a.street == 'flop']),
            'turn': len([a for a in hand.actions if a.street == 'turn']),
            'river': len([a for a in hand.actions if a.street == 'river'])
        }
        
        analysis_html += f'''
        <div class="stat-highlight">
            <h4>Action Summary</h4>
            <p><strong>Preflop:</strong> {action_summary['preflop']} actions | 
            <strong>Flop:</strong> {action_summary['flop']} actions | 
            <strong>Turn:</strong> {action_summary['turn']} actions | 
            <strong>River:</strong> {action_summary['river']} actions</p>
        </div>
        '''
        
        return analysis_html

def main():
    st.title("🃏 Comprehensive Poker Analysis Suite")
    st.markdown("Advanced poker hand analysis with comprehensive statistics and learning tools")
    
    # Initialize session state
    if 'current_action' not in st.session_state:
        st.session_state.current_action = 0
    if 'current_hand_index' not in st.session_state:
        st.session_state.current_hand_index = 0
    if 'replayer' not in st.session_state:
        st.session_state.replayer = ComprehensiveReplayer()
    
    replayer = st.session_state.replayer
    
    # Sidebar controls
    with st.sidebar:
        st.header("📊 Analysis Controls")
        
        # Load hands
        folder_path = st.text_input("Hand History Folder:", "TestHands")
        
        if st.button("🔄 Load Hands"):
            with st.spinner("Loading and analyzing hands..."):
                hands = replayer.load_hands(folder_path)
                st.session_state.hands = hands
                st.session_state.current_hand_index = 0
                st.success(f"Loaded {len(hands)} hands")
        
        # Analysis mode selection
        st.subheader("📈 Analysis Mode")
        analysis_mode = st.selectbox(
            "Select Analysis Mode:",
            ["Hand Replayer", "Player Statistics", "Hand Analysis", "Leak Detection", "Export Data"]
        )
        
        if 'hands' in st.session_state and st.session_state.hands:
            hands = st.session_state.hands
            
            if analysis_mode == "Hand Replayer":
                # Hand selection
                st.subheader("🎯 Hand Selection")
                hand_options = [f"Hand {i+1}: {hand.hand_id} - {hand.timestamp.strftime('%Y-%m-%d %H:%M')}" 
                              for i, hand in enumerate(hands)]
                
                selected_hand = st.selectbox(
                    "Select Hand:",
                    range(len(hands)),
                    format_func=lambda x: hand_options[x]
                )
                
                st.session_state.current_hand_index = selected_hand
                current_hand = hands[selected_hand]
                
                # Action controls
                if current_hand.actions:
                    st.subheader("⏯️ Replay Controls")
                    max_actions = len(current_hand.actions)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("⏮️ First"):
                            st.session_state.current_action = 0
                    with col2:
                        if st.button("⏭️ Last"):
                            st.session_state.current_action = max_actions - 1
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.button("⏪ Previous"):
                            if st.session_state.current_action > 0:
                                st.session_state.current_action -= 1
                    with col4:
                        if st.button("⏩ Next"):
                            if st.session_state.current_action < max_actions - 1:
                                st.session_state.current_action += 1
                    
                    # Action slider
                    st.session_state.current_action = st.slider(
                        "Action Step:",
                        0,
                        max_actions - 1,
                        st.session_state.current_action,
                        key="action_slider"
                    )
            
            elif analysis_mode == "Player Statistics":
                st.subheader("👥 Player Selection")
                all_players = set()
                for hand in hands:
                    for player in hand.players:
                        all_players.add(player.name)
                
                selected_player = st.selectbox("Select Player:", list(all_players))
                st.session_state.selected_player = selected_player
    
    # Main content area
    if 'hands' in st.session_state and st.session_state.hands:
        hands = st.session_state.hands
        
        if analysis_mode == "Hand Replayer":
            current_hand = hands[st.session_state.current_hand_index]
            current_action = st.session_state.get('current_action', 0)
            
            # Hand information header
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Hand ID", current_hand.hand_id)
            with col2:
                st.metric("Stakes", current_hand.stakes)
            with col3:
                st.metric("Table", current_hand.table_name)
            with col4:
                st.metric("Timestamp", current_hand.timestamp.strftime('%H:%M:%S'))
            
            # Current action info
            if current_hand.actions and current_action < len(current_hand.actions):
                action = current_hand.actions[current_action]
                st.info(f"🎯 Current Action: {action.player} {action.action_type} ${action.amount:.2f} ({action.street})")
            
            # Poker table visualization
            st.subheader("🎯 Poker Table")
            
            # Calculate current pot size
            pot_size = 0.0
            if current_hand.actions and current_action < len(current_hand.actions):
                pot_size = current_hand.actions[current_action].pot_after
            else:
                pot_size = current_hand.pot_size
            
            st.markdown(f"### 💰 Pot: ${pot_size:.2f}")
            
            # Display board cards
            if current_hand.board_cards:
                st.subheader("🃏 Board Cards")
                cols = st.columns(len(current_hand.board_cards))
                for i, card in enumerate(current_hand.board_cards):
                    with cols[i]:
                        st.markdown(f"**{card}**")
            
            # Display players with HUD stats
            st.subheader("👥 Players")
            
            # Determine which players are active
            active_players = set()
            if current_hand.actions and current_action < len(current_hand.actions):
                for i, action in enumerate(current_hand.actions[:current_action + 1]):
                    if action.action_type != 'fold':
                        active_players.add(action.player)
            
            # Get current action player
            current_player = None
            if current_hand.actions and current_action < len(current_hand.actions):
                current_player = current_hand.actions[current_action].player
            
            # Display players in a grid
            cols = st.columns(3)
            for i, player in enumerate(current_hand.players):
                col = cols[i % 3]
                with col:
                    is_active = player.name in active_players or current_action == 0
                    is_current = player.name == current_player
                    
                    # Get HUD stats for this player
                    hud_stats = replayer.stats_calculator.generate_hud_stats(player.name)
                    
                    # Render player card
                    player_card = replayer.render_player_card(player, is_active, is_current, hud_stats)
                    st.markdown(player_card, unsafe_allow_html=True)
            
            # Action timeline
            st.subheader("📋 Action Timeline")
            timeline_html = replayer.render_action_timeline(current_hand, current_action)
            components.html(timeline_html, height=400, scrolling=True)
            
            # Hand analysis
            st.subheader("🔍 Hand Analysis")
            analysis_html = replayer.render_hand_analysis(current_hand)
            st.markdown(analysis_html, unsafe_allow_html=True)
        
        elif analysis_mode == "Player Statistics":
            selected_player = st.session_state.get('selected_player', '')
            if selected_player:
                st.subheader(f"📊 Statistics for {selected_player}")
                
                # Get player stats
                player_stats = replayer.stats_calculator.player_stats.get(selected_player)
                if player_stats:
                    # Display HUD stats
                    hud_stats = replayer.stats_calculator.generate_hud_stats(selected_player)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("VPIP", hud_stats.get("VPIP", "N/A"))
                        st.metric("PFR", hud_stats.get("PFR", "N/A"))
                    with col2:
                        st.metric("3Bet", hud_stats.get("3Bet", "N/A"))
                        st.metric("CBet", hud_stats.get("CBet", "N/A"))
                    with col3:
                        st.metric("AF", hud_stats.get("AF", "N/A"))
                        st.metric("WTSD", hud_stats.get("WTSD", "N/A"))
                    with col4:
                        st.metric("W$SD", hud_stats.get("W$SD", "N/A"))
                        st.metric("BB/100", hud_stats.get("BB/100", "N/A"))
                    
                    # Positional stats
                    st.subheader("📍 Positional Statistics")
                    positional_df = replayer.stats_calculator.generate_positional_report(selected_player)
                    if not positional_df.empty:
                        st.dataframe(positional_df, use_container_width=True)
                    
                    # Leak detection
                    st.subheader("🔍 Leak Detection")
                    leaks = replayer.stats_calculator.generate_leak_report(selected_player)
                    if leaks:
                        for leak in leaks:
                            st.markdown(f'<div class="leak-warning">{leak}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="leak-success">No major leaks detected!</div>', unsafe_allow_html=True)
        
        elif analysis_mode == "Hand Analysis":
            st.subheader("📈 Overall Hand Analysis")
            
            # Create hands DataFrame
            hands_df = create_hands_dataframe(hands)
            
            # Basic statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Hands", len(hands))
            with col2:
                st.metric("Unique Players", hands_df['Hand_ID'].nunique())
            with col3:
                st.metric("Average Pot Size", f"${hands_df['Pot_Size'].mean():.2f}")
            with col4:
                st.metric("Total Rake", f"${hands_df['Rake'].sum():.2f}")
            
            # Showdown analysis
            showdown_hands = hands_df[hands_df['Went_to_Showdown'] == True]
            if not showdown_hands.empty:
                st.subheader("🎯 Showdown Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Showdown %", f"{(len(showdown_hands) / len(hands)) * 100:.1f}%")
                with col2:
                    st.metric("Heads Up %", f"{(hands_df['Is_Heads_Up'].sum() / len(hands)) * 100:.1f}%")
        
        elif analysis_mode == "Leak Detection":
            st.subheader("🔍 Leak Detection for All Players")
            
            # Get all players
            all_players = set()
            for hand in hands:
                for player in hand.players:
                    all_players.add(player.name)
            
            for player_name in all_players:
                with st.expander(f"👤 {player_name}"):
                    leaks = replayer.stats_calculator.generate_leak_report(player_name)
                    if leaks:
                        for leak in leaks:
                            st.markdown(f'<div class="leak-warning">{leak}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="leak-success">No major leaks detected!</div>', unsafe_allow_html=True)
        
        elif analysis_mode == "Export Data":
            st.subheader("💾 Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export Player Statistics"):
                    df_stats = replayer.stats_calculator.export_to_csv("player_statistics.csv")
                    csv = df_stats.to_csv(index=False)
                    st.download_button(
                        label="Download Player Stats CSV",
                        data=csv,
                        file_name="player_statistics.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("🎯 Export Actions Data"):
                    actions_df = create_actions_dataframe(hands)
                    csv = actions_df.to_csv(index=False)
                    st.download_button(
                        label="Download Actions CSV",
                        data=csv,
                        file_name="actions_data.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🃏 Export Hands Data"):
                    hands_df = create_hands_dataframe(hands)
                    csv = hands_df.to_csv(index=False)
                    st.download_button(
                        label="Download Hands CSV",
                        data=csv,
                        file_name="hands_data.csv",
                        mime="text/csv"
                    )
    
    else:
        st.info("Please load hand histories using the sidebar controls.")
        
        # Show features
        st.subheader("🚀 Features")
        st.markdown("""
        - **Comprehensive Hand Replay**: Step through actions with detailed analysis
        - **Player Statistics**: VPIP, PFR, 3Bet, CBet, AF, WTSD, and more
        - **Positional Analysis**: Stats broken down by position
        - **Leak Detection**: Identify playing weaknesses automatically
        - **HUD Statistics**: Real-time player information during replay
        - **Export Capabilities**: Export data for further analysis
        - **Advanced Metrics**: Bet sizing, pot odds, aggression factors
        """)

if __name__ == "__main__":
    main()
