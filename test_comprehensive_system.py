#!/usr/bin/env python3
"""
Test script for the comprehensive poker analysis system
"""

import os
import sys
from comprehensive_parser import parse_file_comprehensive, ComprehensiveParser
from poker_statistics import PokerStatisticsCalculator, create_actions_dataframe, create_hands_dataframe

def test_parser():
    """Test the comprehensive parser"""
    print("🧪 Testing Comprehensive Parser...")
    
    # Create a sample hand history
    sample_hand = """
Poker Hand #123456789
Table 'Test Table' 6-max Seat #1 is the button
Seat 1: Hero ($100.00 in chips)
Seat 2: Player2 ($95.50 in chips)
Seat 3: Player3 ($87.25 in chips)
Seat 4: Player4 ($102.75 in chips)
Seat 5: Player5 ($89.00 in chips)
Seat 6: Player6 ($91.50 in chips)
Player6: posts small blind $0.50
Player1: posts big blind $1.00
*** HOLE CARDS ***
Dealt to Hero [Ah Kh]
Player2: folds
Player3: calls $1.00
Player4: folds
Player5: raises $3.00 to $4.00
Player6: folds
Hero: calls $3.00
Player3: calls $3.00
*** FLOP *** [2c 7h 9s]
Hero: checks
Player3: checks
Player5: bets $6.00
Hero: calls $6.00
Player3: folds
*** TURN *** [2c 7h 9s] [Jd]
Hero: checks
Player5: bets $12.00
Hero: calls $12.00
*** RIVER *** [2c 7h 9s Jd] [3h]
Hero: checks
Player5: bets $24.00
Hero: calls $24.00
*** SHOWDOWN ***
Player5: shows [Ac Kc] (a pair of Kings)
Hero: shows [Ah Kh] (a pair of Kings)
Hero collected $89.00 from pot
*** SUMMARY ***
Total pot $89.00 | Rake $3.00
Board [2c 7h 9s Jd 3h]
Seat 1: Hero (big blind) showed [Ah Kh] and won ($89.00) with a pair of Kings
Seat 3: Player3 (button) folded on the Turn
Seat 5: Player5 showed [Ac Kc] and lost with a pair of Kings
"""
    
    try:
        parser = ComprehensiveParser()
        hand_data = parser.parse_hand_comprehensive(sample_hand)
        
        print(f"✅ Hand ID: {hand_data.hand_id}")
        print(f"✅ Players: {len(hand_data.players)}")
        print(f"✅ Actions: {len(hand_data.actions)}")
        print(f"✅ Board: {hand_data.board_cards}")
        print(f"✅ Winner: {hand_data.winner}")
        print(f"✅ Pot Size: ${hand_data.pot_size}")
        
        return hand_data
        
    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        return None

def test_statistics(hand_data):
    """Test the statistics calculator"""
    print("\n📊 Testing Statistics Calculator...")
    
    try:
        calculator = PokerStatisticsCalculator()
        calculator.load_hands([hand_data])
        stats = calculator.calculate_all_stats()
        
        print(f"✅ Calculated stats for {len(stats)} players")
        
        for player_name, player_stats in stats.items():
            print(f"  - {player_name}: {player_stats.hands_played} hands, VPIP: {player_stats.vpip:.1f}%")
        
        # Test HUD stats
        if hand_data.players:
            hero_name = next((p.name for p in hand_data.players if p.is_hero), None)
            if hero_name:
                hud_stats = calculator.generate_hud_stats(hero_name)
                print(f"✅ HUD stats for {hero_name}: {hud_stats}")
        
        return calculator
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return None

def test_dataframes(hands):
    """Test DataFrame creation"""
    print("\n📋 Testing DataFrame Creation...")
    
    try:
        # Test actions DataFrame
        actions_df = create_actions_dataframe(hands)
        print(f"✅ Actions DataFrame: {len(actions_df)} rows, {len(actions_df.columns)} columns")
        
        # Test hands DataFrame
        hands_df = create_hands_dataframe(hands)
        print(f"✅ Hands DataFrame: {len(hands_df)} rows, {len(hands_df.columns)} columns")
        
        # Test CSV export
        calculator = PokerStatisticsCalculator()
        calculator.load_hands(hands)
        calculator.calculate_all_stats()
        stats_df = calculator.export_to_csv("test_stats.csv")
        print(f"✅ Stats CSV export: {len(stats_df)} rows")
        
        # Clean up test file
        if os.path.exists("test_stats.csv"):
            os.remove("test_stats.csv")
        
        return True
        
    except Exception as e:
        print(f"❌ DataFrame test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Poker Analysis System Tests\n")
    
    # Test 1: Parser
    hand_data = test_parser()
    if not hand_data:
        print("❌ Parser test failed, stopping tests")
        return
    
    # Test 2: Statistics
    calculator = test_statistics(hand_data)
    if not calculator:
        print("❌ Statistics test failed, stopping tests")
        return
    
    # Test 3: DataFrames
    success = test_dataframes([hand_data])
    if not success:
        print("❌ DataFrame test failed")
        return
    
    print("\n🎉 All tests passed! The comprehensive poker analysis system is working correctly.")
    print("\n📝 To run the full application:")
    print("   py -3.13 -m streamlit run comprehensive_replayer.py")

if __name__ == "__main__":
    main()

