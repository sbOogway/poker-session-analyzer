from pprint import pprint
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import streamlit_charts
import utils
import api
from analyzer import DataAnalyzer


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


def main():
    st.set_page_config(
        page_title="Poker Session analyzer",
        page_icon=":material/poker_chip:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "analyzer" not in st.session_state:
        st.session_state.analyzer = DataAnalyzer()

    # if "sessions" not in st.session_state:
    #     st.session_state.poker_session_ids = []

    analyzer = st.session_state.analyzer

    players = api.get_players()

    sessions = api.get_sessions()
    sessions = utils.format_sessions_selection(sessions)
    st.session_state.poker_sessions = sessions
    # pprint(sessions)

    c = st.columns([10, 3, 1, 1], vertical_alignment="bottom")

    with c[1]:
        username = st.selectbox(
            "player id",
            ["caduceus369"] + players,
            on_change=analyzer.display_sessions,
            key="player_id",
        )

    with c[0]:
        st.multiselect(
            "sessions",
            ["all"] + sessions,
            default=[],
            on_change=analyzer.display_sessions,
            key="poker_session_ids"
        )

    with c[2]:
        currency = st.text_input("currency", "€")

    with c[3]:
        if st.button("🔬", help="analyze data", use_container_width=True):
            response = api.analyze_hands(username)
            logger.info(response)
            st.toast(f"analyzed hands from {username}", icon="✅")

    tabs = st.tabs(
        [
            "📈 Overview",
            "💰 Results",
            "📍 Position",
            "💵 Stakes analysis",
            "📋 Detailed hand data",
            "💾 Upload/Export data",
            "🃏 Hand replayer",
            "🛠️ Analysis tools",
            "🪓 Overral rake",
        ]
    )

    if analyzer.df is not None and not analyzer.df.empty:
        metrics = analyzer.calculate_key_metrics()
        metrics['bb_per_100'] = streamlit_charts.calculate_bb_per_100(analyzer.df, currency)

        with tabs[0]:
            streamlit_charts.render_overview_metrics(metrics)

        with tabs[1]:
            streamlit_charts.render_results_chart(analyzer.df, currency=currency)

        with tabs[2]:
            streamlit_charts.render_position_analysis(analyzer.df)

        with tabs[3]:
            streamlit_charts.render_stakes_analysis(analyzer.df)

        with tabs[4]:
            streamlit_charts.render_detailed_data(analyzer.df)

    with tabs[5]:
        streamlit_charts.export_data(analyzer.df)

    with tabs[6]:
        streamlit_charts.render_hand_replayer()

    with tabs[7]:
        streamlit_charts.render_external_tools()

    with tabs[8]:
        streamlit_charts.render_overrall_rake()


if __name__ == "__main__":
    main()
