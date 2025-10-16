from pprint import pprint
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from decimal import Decimal
import streamlit_charts
import utils
import api

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(log_format)

# logger.addHandler(console_handler)


# Page configuration
st.set_page_config(
    page_title="Hero Poker Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


class HeroDataAnalyzer:
    def __init__(self):
        self.df = None

    def get_hands(self, username: str, session_id: str = None):
        data = api.get_player_hands(username, session_id)
        # pprint(data)
        df = pd.DataFrame.from_dict(data["data"])
        self.df = df

    def calculate_key_metrics(self):
        """Calculate key performance metrics"""
        if self.df is None or self.df.empty:
            return {}

        self.df["timestamp"] = self.df["time"].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
        )
        self.df = self.df.sort_values("timestamp")


        # assertions
        fail_mask_1 = (
            (self.df["total_collected"].apply(lambda x: Decimal(str(x))) - self.df["total_contributed"].apply(lambda x : Decimal(str(x))))
            == self.df["net_profit"].apply(lambda x: Decimal(str(x)))
        )

        net_profit          = utils.to_decimal(self.df["net_profit"])
        rake_amount         = utils.to_decimal(self.df["rake_amount"])
        net_profit_before   = utils.to_decimal(self.df["net_profit_before_rake"])

        positive_mask = net_profit > 0
        negative_mask = ~positive_mask

        cond1 = (net_profit[positive_mask] + rake_amount[positive_mask]) == net_profit_before[positive_mask]
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
        }

    
def main():

    
    st.title("📊 Poker Session Analyzer")

    if "analyzer" not in st.session_state:
        st.session_state.analyzer = HeroDataAnalyzer()

    analyzer = st.session_state.analyzer

    # Sidebar controls
    with st.sidebar:
        st.header("📁 Data Controls")

        files = st.file_uploader("📤 Upload file", accept_multiple_files=True)

        currency = st.text_input("currency", "€")
        username = st.text_input("Your username", "caduceus369")
        session_id = st.text_input("Session id", "M62C33044BB297NJ")
        st.selectbox("sessions", ("All", "yoofhewofhweuiofhouwehfuiwehfoiuewhfiouhweioufhioweuhfoiwehfiwehfiuwehfo", "test"))

        if st.button("🔄 Upload Data"):
            for file in files:
                response = api.upload_hands(
                    {"file": (file.name, file.getvalue(), "text/plain")}
                )
                if response["status"] != "got em":
                    st.toast("error uploading data", icon="❌")
                logger.info(response)
            st.toast(f"uploaded {len(files)} hand files to database", icon="✅")

        if st.button("🔁 Reload Data"):
            if session_id:
                analyzer.get_hands(username, session_id)
            else:
                analyzer.get_hands(username, "all")
            st.toast(f"retrieved {len(analyzer.df)} hands from database", icon="✅")

        if st.button("🔬 Analyze Data"):
            response = api.analyze_hands(username)
            logger.info(response)
            st.toast(f"analyzed hands from {username}", icon="✅")


        st.header("📊 Analysis Options")

        show_overview = st.checkbox("Overview Metrics", value=True)
        show_profit_chart = st.checkbox("Profit Chart", value=True)
        show_rake_analysis = st.checkbox("Rake Analysis", value=True)
        show_position_analysis = st.checkbox("Position Analysis", value=True)
        show_stakes_analysis = st.checkbox("Stakes Analysis", value=True)
        show_hand_analysis = st.checkbox("Hand Type Analysis", value=False)
        show_detailed_data = st.checkbox("Detailed Data", value=True)

        # st.page_link("#range-analysis", label="Range Analysis")

        st.markdown(
            """
            [🎚️ Range analysis](#range-analysis)

            [💰 Expected bankroll growth](#expected-bankroll-growth)
            """
        )
    # Main content
    if analyzer.df is not None and not analyzer.df.empty:
        metrics = analyzer.calculate_key_metrics()

        if show_overview:
            
            streamlit_charts.render_overview_metrics(metrics)

            # Additional Statistics Section
            

        # if show_profit_chart:
        # st.header("💰 Profit Analysis")
        # analyzer.render_profit_chart()

        if show_rake_analysis:
            st.header("💰 Results")
            streamlit_charts.render_results_chart(analyzer.df, currency=currency)

        if show_position_analysis:
            st.header("📍 Position Analysis")
            streamlit_charts.render_position_analysis(analyzer.df)

        if show_stakes_analysis:
            st.header("💵 Stakes Analysis")
            streamlit_charts.render_stakes_analysis(analyzer.df)

        if show_hand_analysis:
            st.header("🃏 Hand Type Analysis")
            streamlit_charts.render_hand_strength_analysis(analyzer.df)

        if show_detailed_data:
            st.header("📋 Detailed Hand Data")
            streamlit_charts.render_detailed_data(analyzer.df)

        # Export section
        st.header("💾 Export Data")
        streamlit_charts.export_data(analyzer.df)

    else:
        st.info("Please load hand histories using the sidebar controls.")

    streamlit_charts.render_external_tools()


if __name__ == "__main__":
    main()
