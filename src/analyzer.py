import api
import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal
import utils
import base64


class DataAnalyzer:
    def __init__(self):
        self.df = None
        self.sessions_retrieved = dict()

    def fetch_sessions(self, sessions_iterable, username):
        for session in sessions_iterable:
            if "session" == "all":
                continue
            id = session.split(" - ")[-1]
            key = f"{session}-{username}"
            try:
                # do not remove tmp variable otherwise st renders df on top of page
                tmp = st.session_state[key]
            except KeyError:
                data = api.get_player_hands(username, id)
                st.session_state[key] = pd.DataFrame.from_dict(data["data"])

    def update_hands_df(self, sessions_iterable, username):
        for session in sessions_iterable:
            if session == "all":
                continue
            key = f"{session}-{username}"
            self.df = pd.concat([self.df, st.session_state[key]])

    def display_sessions_all(self, username):
        sessions_iterable = st.session_state.poker_sessions
        self.fetch_sessions(sessions_iterable, username)
        self.update_hands_df(sessions_iterable, username)

    def display_sessions_from_select(self, username):
        sessions_iterable = st.session_state.poker_session_ids
        self.fetch_sessions(sessions_iterable, username)
        self.update_hands_df(sessions_iterable, username)

    def display_sessions(self):
        self.df = pd.DataFrame()
        username = st.session_state.player_id
        print(username)
        if "all" in st.session_state.poker_session_ids:
            self.display_sessions_all(username)
        else:
            self.display_sessions_from_select(username)

    def get_hands(self, username: str, session_id: str = None):
        if session_id in self.data.keys():
            return

        data = api.get_player_hands(username, session_id)
        df = pd.DataFrame.from_dict(data["data"])
        self.data[session_id] = df
        self.df = df

    def calculate_key_metrics(self, currency):
        """Calculate key performance metrics"""
        if self.df is None or self.df.empty:
            return {}

        self.df["timestamp"] = self.df["time"].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
        )
        self.df = self.df.sort_values("timestamp")



        # assertions
        fail_mask_1 = (
            self.df["total_collected"].apply(lambda x: Decimal(str(x)))
            - self.df["total_contributed"].apply(lambda x: Decimal(str(x)))
        ) == self.df["net_profit"].apply(lambda x: Decimal(str(x)))

        net_profit = utils.to_decimal(self.df["net_profit"])
        rake_amount = utils.to_decimal(self.df["rake_amount"])
        net_profit_before = utils.to_decimal(self.df["net_profit_before_rake"])

        positive_mask = net_profit > 0
        negative_mask = ~positive_mask

        cond1 = (
            net_profit[positive_mask] + rake_amount[positive_mask]
        ) == net_profit_before[positive_mask]
        cond2 = net_profit[negative_mask] == net_profit_before[negative_mask]

        assert cond1.all() and cond2.all()
        assert all(fail_mask_1)

        # calculations
        self.df["running_profit"] = self.df["net_profit"].cumsum()
        self.df["running_profit_before_rake"] = self.df[
            "net_profit_before_rake"
        ].cumsum()
        self.df["running_rake"] = (
            self.df["rake_amount"].where(self.df["net_profit"] > 0).cumsum()
        )
        self.df["hand_number"] = range(1, len(self.df) + 1)

        self.df["stakes"] = self.df["game"].apply(lambda x: x.split("_")[2])

        self.df["b64_text"] = self.df["text"].apply(utils._encode_base64)
        self.df["hand_review"] = ('https://sboogway.github.io/poker-hand-replayer?text=' + self.df["b64_text"].astype(str))

        total_hands = len(self.df)
        total_profit = self.df["net_profit"].sum()
        total_profit_before_rake = self.df["net_profit_before_rake"].sum()
        # total_profit_after_rake = self.df["net_profit_after_rake"].sum()
        total_rake = self.df["rake_amount"].where(self.df["net_profit"] > 0).sum()

        avg_profit = self.df["net_profit"].mean()
        avg_profit_before_rake = self.df["net_profit_before_rake"].mean()
        avg_rake = self.df["rake_amount"].mean()
        total_pot_size = self.df["total_pot_size"].sum()
        rake_percentage = (
            (total_rake / total_pot_size * 100) if total_pot_size > 0 else 0
        )
        # vpip metrics (separate from pfr)
        vpip_hands = self.df["vpip"].sum()
        vpip_rate = (vpip_hands / total_hands) * 100 if total_hands > 0 else 0

        # flop metrics
        saw_flop = self.df["saw_flop"].sum()
        flop_rate = (saw_flop / total_hands) * 100 if total_hands > 0 else 0

        won_when_saw_flop = self.df["won_when_saw_flop"].sum()
        flop_win_rate = (won_when_saw_flop / saw_flop) * 100 if saw_flop > 0 else 0

        # showdown metrics (only calculated on hands where hero saw flop)
        went_to_showdown = self.df["went_to_showdown"].sum()
        showdown_rate = (went_to_showdown / saw_flop) * 100 if saw_flop > 0 else 0

        # won at showdown (w$sd) - percentage of showdowns won
        won_at_showdown = self.df["won_at_showdown"].sum()
        won_at_showdown_rate = (
            (won_at_showdown / went_to_showdown) * 100 if went_to_showdown > 0 else 0
        )

        # preflop metrics
        preflop_raised = self.df["preflop_raised"].sum()
        preflop_raise_rate = (
            (preflop_raised / total_hands) * 100 if total_hands > 0 else 0
        )

        preflop_called = self.df["preflop_called"].sum()
        preflop_call_rate = (
            (preflop_called / total_hands) * 100 if total_hands > 0 else 0
        )

        # c-bet metrics
        cbet_flop = self.df["cbet_flop"].sum()
        cbet_turn = self.df["cbet_turn"].sum()
        cbet_river = self.df["cbet_river"].sum()


        # Calculate big blind per 100 hands metric
        if self.df is None or self.df.empty:
            bb_per_100 = 0.0
        else:
            # Parse big blind from stakes (format like "$0.01/$0.02")
            def get_bb(stakes_str):
                import re
                match = re.search(r'/' + currency + '([\d\..]+)', stakes_str)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        print(f"ValueError parsing BB from: {stakes_str}")
                        return 0.0
                return 0.0

            df_copy = self.df.copy()
            print(df_copy['stakes'])

            df_copy['bb'] = df_copy['stakes'].apply(get_bb)

            print(df_copy['bb'])
            # Filter out hands where BB is 0 or invalid
            df_copy = df_copy[df_copy['bb'] > 0]

            if df_copy.empty:
                bb_per_100 = 0.0
            else:
                # Profit in big blinds
                df_copy['profit_bb'] = df_copy['net_profit'] / df_copy['bb']

                # Total BB profit
                total_bb_profit = df_copy['profit_bb'].sum()
                total_hands = len(df_copy)

                # BB per 100 hands
                bb_per_100 = (total_bb_profit / total_hands) * 100

        return {
            "total_hands": total_hands,
            "total_profit": total_profit,
            "total_profit_before_rake": total_profit_before_rake,
            # 'total_profit_after_rake': total_profit_after_rake,
            "total_rake": total_rake,
            "avg_profit": avg_profit,
            "avg_profit_before_rake": avg_profit_before_rake,
            "avg_rake": avg_rake,
            "rake_percentage": rake_percentage,
            "vpip_hands": vpip_hands,
            "vpip_rate": vpip_rate,
            "went_to_showdown": went_to_showdown,
            "showdown_rate": showdown_rate,
            "saw_flop": saw_flop,
            "flop_rate": flop_rate,
            "won_when_saw_flop": won_when_saw_flop,
            "flop_win_rate": flop_win_rate,
            "won_at_showdown": won_at_showdown,
            "won_at_showdown_rate": won_at_showdown_rate,
            "preflop_raised": preflop_raised,
            "preflop_raise_rate": preflop_raise_rate,
            "preflop_called": preflop_called,
            "preflop_call_rate": preflop_call_rate,
            "cbet_flop": cbet_flop,
            "cbet_turn": cbet_turn,
            "cbet_river": cbet_river,
            "bb_per_100": bb_per_100,
        }


