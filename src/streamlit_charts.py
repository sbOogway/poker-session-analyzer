import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import config, utils
import math
from bankroll_growth import calc_growth_rate
from jinja2 import Environment, FileSystemLoader
import streamlit.components.v1 as components


def render_profit_chart(self):
    """Render profit over time chart"""
    if self.df is None or self.df.empty:
        return

    fig = px.line(
        self.df,
        x="Hand_Number",
        y="Running_Profit",
        title="Cumulative Profit Over Time",
        labels={
            "Hand_Number": "Hand Number",
            "Running_Profit": "Cumulative Profit ($)",
        },
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)

    fig.update_layout(
        xaxis_title="Hand Number",
        yaxis_title="Cumulative Profit ($)",
        hovermode="x unified",
    )

    st.plotly_chart(fig, width="stretch")

def render_results_chart(df: pd.DataFrame, currency):
    """Render rake analysis chart comparing profit with and without rake"""
    if df is None or df.empty:
        return

    # Create subplot with two y-axes
    fig = make_subplots(
        rows=1,
        cols=1,
        subplot_titles=(
            "Result over hands",
            # "Total Rake Paid Over Time (Incl. Jackpot)",
        ),
        vertical_spacing=0.1,
    )

    # Add profit lines
    fig.add_trace(
        go.Scatter(
            x=df["hand_number"],
            y=df["running_profit"],
            name="Result (After Rake)",
            line=dict(color="#6adcff", width=2),
        ),
        row=1,
        col=1,
    )

    # Add zero line
    fig.add_hline(
        y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1
    )

    # Add rake line
    fig.add_trace(
        go.Scatter(
            x=df["hand_number"],
            y=df["running_rake"],
            name="Cumulative Rake Paid",
            line=dict(color="orange", width=2),
            fill="tozeroy",
        ),
        row=1,
        col=1,
    )

    fig.update_layout(height=600, showlegend=False, hovermode="x unified")

    fig.update_xaxes(title_text="Hand Number", row=1, col=1)
    fig.update_yaxes(title_text=f"Amount in {currency}", row=1, col=1)

    st.plotly_chart(fig, config=dict(width="stretch"))

def render_overview_metrics(metrics):
    """Render overview metrics"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Hands", f"{metrics['total_hands']:,}", border=True)
        st.metric("Total Profit ", f"{metrics['total_profit']:.2f}", border=True)

    with col2:
        st.metric(
            "Total Profit (Before Rake)",
            f"{metrics['total_profit_before_rake']:.2f}",
            border=True
        )
        st.metric(
            "Total Rake Paid", f"{metrics['total_rake']:.2f}", border=True
        )
    
    with col3:
        st.metric("Avg Profit/Hand (After Rake)", f"{metrics['avg_profit']:.2f}", border=True)
        st.metric(
            "Avg Profit/Hand (Before Rake)",
            f"{metrics['avg_profit_before_rake']:.2f}", border=True)

        

    st.header("🎯 Detailed Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("VPIP Rate", f"{metrics['vpip_rate']:.1f}%")
        st.metric("Preflop Raise Rate", f"{metrics['preflop_raise_rate']:.1f}%")
        st.metric("Preflop Call Rate", f"{metrics['preflop_call_rate']:.1f}%")

    with col2:
        st.metric("Saw Flop Rate", f"{metrics['flop_rate']:.1f}%")
        st.metric("Flop Win Rate", f"{metrics['flop_win_rate']:.1f}%")
        st.metric(
            "C-Bet Flop Rate",
            f"{(metrics['cbet_flop'] / metrics['total_hands'] * 100) if metrics['total_hands'] > 0 else 0:.1f}%",
        )

    with col3:
        st.metric("Showdown Rate (of Flop)", f"{metrics['showdown_rate']:.1f}%")
        st.metric(
            "W$SD (Won at Showdown)", f"{metrics['won_at_showdown_rate']:.1f}%"
        )
        st.metric(
            "Won at Showdown Count", f"{metrics['won_at_showdown']} times"
        )

    with col4:
        st.metric(
            "C-Bet Turn Rate",
            f"{(metrics['cbet_turn'] / metrics['total_hands'] * 100) if metrics['total_hands'] > 0 else 0:.1f}%",
        )
        st.metric(
            "C-Bet River Rate",
            f"{(metrics['cbet_river'] / metrics['total_hands'] * 100) if metrics['total_hands'] > 0 else 0:.1f}%",
        )
        st.metric("Total Hands", f"{metrics['total_hands']:,}")

    

    

def render_position_analysis(df: pd.DataFrame):
    """Render position-based analysis"""
    if df is None or df.empty:
        return

    position_stats = (
        df.groupby("position")
        .agg(
            {
                "net_profit": ["count", "sum", "mean"],
                "went_to_showdown": "mean",
                "won_when_saw_flop": "mean",
                "preflop_raised": "mean",
                "cbet_flop": "mean",
            }
        )
        .round(3)
    )

    position_stats.columns = [
        "hands",
        "total profit",
        "avg profit",
        "showdown rate",
        "flop win rate",
        "preflop raise rate",
        "cbet rate",
    ]

    st.dataframe(position_stats, width="stretch")

    df["hand_range_bucket"] = df["hole_cards"].apply(
        lambda x: utils.categorize_hand(" ".join(x))
    )

    # print(self.df[""])

    hands_by_position = df.groupby("position")

    hands_bucket = {
        hand: {
            "name": hand,
            "fold": 0,
            "call": 0,
            "raise": 0,
            "free_flop": 0,
            "fold_frequency": 0,
            "call_frequency": 0,
            "raise_frequency": 0,
            "not_dealt_frequency": 0,
            "total": 0,
        }
        for hand in config.HANDS
    }

    for idx, hand in df.iterrows():
        if hand["hand_range_bucket"] == "":
            continue

        hands_bucket[hand["hand_range_bucket"]]["total"] += 1

        if hand["limped"] or hand["called"] or hand["serial_caller"]:
            hands_bucket[hand["hand_range_bucket"]]["call"] += 1
            continue

        if (
            hand["single_raised_pot"]
            or hand["three_bet"]
            or hand["four_bet"]
            or hand["five_bet"]
        ):
            hands_bucket[hand["hand_range_bucket"]]["raise"] += 1
            continue

        if hand["preflop_folded"]:
            hands_bucket[hand["hand_range_bucket"]]["fold"] += 1
            continue

        hands_bucket[hand["hand_range_bucket"]]["free_flop"] += 1

    for name, hand in hands_bucket.items():
        if hand["total"] == 0:
            hands_bucket[name]["not_dealt_frequency"] = 100
            continue

        hands_bucket[name]["fold_frequency"] = round(
            hand["fold"] / hand["total"] * 100, 2
        )
        hands_bucket[name]["call_frequency"] = round(
            hand["call"] / hand["total"] * 100, 2
        )
        hands_bucket[name]["raise_frequency"] = round(
            hand["raise"] / hand["total"] * 100, 2
        )
        hands_bucket[name]["free_flop_frequency"] = round(
            hand["free_flop"] / hand["total"] * 100, 2
        )

    hands_bucket = hands_bucket.values()

    absolute = {
        "fold": sum(hand.get("fold", 0) for hand in hands_bucket),
        "call": sum(hand.get("call", 0) for hand in hands_bucket),
        "raise": sum(hand.get("raise", 0) for hand in hands_bucket),
        "check": sum(hand.get("free_flop", 0) for hand in hands_bucket),
    }

    absolute["total"] = (
        absolute["fold"] + absolute["call"] + absolute["raise"] + absolute["check"]
    )


    env = Environment(loader=FileSystemLoader("templates"))
    range_template = env.get_template("range.html.j2")

    # it doesnt work with villains because we don t know hole cards
    try:
        absolute["call_frequency"] = round(
            absolute["call"] / absolute["total"] * 100, 2
        )
        absolute["fold_frequency"] = round(
            absolute["fold"] / absolute["total"] * 100, 2
        )
        absolute["raise_frequency"] = round(
            absolute["raise"] / absolute["total"] * 100, 2
        )
        absolute["check_frequency"] = round(
            absolute["check"] / absolute["total"] * 100, 2
        )

        range_html = range_template.render(
            {"hands": hands_bucket, "absolute": absolute}
        )

        components.html(html=range_html, height=700)

    except ZeroDivisionError:
        print("error division 0 visualizer")
        pass

    # pprint(self.df)
    # pprint(hands_bucket)
    # range visualizer

    # st.table(self.df)

def render_expected_bankroll_chart():
    st.header("💰 Expected bankroll growth")

    col1, col2, col3 = st.columns(3)

    with col1:
        p_of_win = st.number_input("Probability of winning", 0.0, 1.0, value=0.5)

    with col2:
        pot_size = st.number_input("Pot size", 0.01)
    with col3:
        call_amount = st.number_input("Amount to call", 0.01)

    # kelly bankroll
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Expected bankroll growth",),
        specs=[[{"type": "scatter"}, {"type": "table"}]],
    )

    x_bankroll = [i for i in range(100)]
    y_bankroll = [
        math.log(calc_growth_rate(i / 100, 1, pot_size / call_amount, p_of_win))
        * 100
        for i in x_bankroll
    ]

    optimal_bet_size = round(x_bankroll[y_bankroll.index(max(y_bankroll))], 2)
    optimal_growth_rate = round(max(y_bankroll), 2)
    positives = list(filter(lambda x: x > 0, y_bankroll))
    break_even_bet_size = len(positives)

    fig.add_trace(
        go.Scatter(
            x=x_bankroll,
            y=y_bankroll,
            name="",
            line=dict(color="#6adcff", width=2),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Table(
            cells=dict(
                values=[
                    [
                        "optimal bet size",
                        "optimal growth rate",
                        "break even bet size",
                    ],
                    [
                        f"{optimal_bet_size:.2f}",
                        f"{optimal_growth_rate:.2f}",
                        f"{break_even_bet_size:.2f}",
                    ],
                ]
            )
        ),
        row=1,
        col=2,
    )

    st.plotly_chart(fig)

def render_stakes_analysis(df: pd.DataFrame):
    """Render stakes-based analysis"""
    if df is None or df.empty:
        return

    stakes_stats = (
        df.groupby("stakes")
        .agg(
            {
                "net_profit": ["count", "sum", "mean"],
                "went_to_showdown": "mean",
                "won_when_saw_flop": "mean",
            }
        )
        .round(3)
    )

    stakes_stats.columns = [
        "hands",
        "total_profit",
        "avg_profit",
        "showdown_rate",
        "flop_win_rate",
    ]

    st.dataframe(stakes_stats, width="stretch")

def render_hand_strength_analysis(df: pd.DataFrame):
    """Render hand strength analysis"""
    if df is None or df.empty:
        return

    # Analyze by hole cards (simplified)
    df_with_cards = df[df["hole_cards"] != ""].copy()

    if df_with_cards.empty:
        st.info("No hole card data available for analysis")
        return

    # Group by card suits and values for basic analysis
    df_with_cards["Card1"] = df_with_cards["Hole_Cards"].str.split().str[0]
    df_with_cards["Card2"] = df_with_cards["Hole_Cards"].str.split().str[1]

    # Create hand type categories
    def categorize_hand(card1, card2):
        if pd.isna(card1) or pd.isna(card2):
            return "Unknown"

        # Extract values and suits
        val1, suit1 = card1[:-1], card1[-1]
        val2, suit2 = card2[:-1], card2[-1]

        # Convert face cards to numbers
        face_values = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        val1_num = face_values.get(val1, int(val1))
        val2_num = face_values.get(val2, int(val2))

        if suit1 == suit2:
            if val1_num == val2_num:
                return "Pocket Pair"
            else:
                return "Suited"
        else:
            if val1_num == val2_num:
                return "Pocket Pair"
            else:
                return "Offsuit"

    df_with_cards["Hand_Type"] = df_with_cards.apply(
        lambda row: categorize_hand(row["Card1"], row["Card2"]), axis=1
    )

    hand_type_stats = (
        df_with_cards.groupby("Hand_Type")
        .agg(
            {
                "Net_Profit": ["count", "sum", "mean"],
                "Went_to_Showdown": "mean",
                "Won_When_Saw_Flop": "mean",
            }
        )
        .round(3)
    )

    hand_type_stats.columns = [
        "hands",
        "total_profit",
        "avg_profit",
        "showdown_rate",
        "flop_win_rate",
    ]

    st.dataframe(hand_type_stats, width="stretch")

def render_detailed_data(df: pd.DataFrame):
    """Render detailed hand data"""
    if df is None or df.empty:
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        positions = ["all"] + list(df["position"].unique())
        selected_position = st.selectbox("filter by position", positions)

    with col2:
        stakes = ["all"] + list(df["stakes"].unique())
        selected_stakes = st.selectbox("filter by stakes", stakes)

    with col3:
        show_showdown_only = st.checkbox("show showdown hands only")

    # apply filters
    filtered_df = df.copy()

    if selected_position != "all":
        filtered_df = filtered_df[filtered_df["position"] == selected_position]

    if selected_stakes != "all":
        filtered_df = filtered_df[filtered_df["stakes"] == selected_stakes]

    if show_showdown_only:
        filtered_df = filtered_df[filtered_df["went_to_showdown"] == True]

    # Display data
    st.dataframe(
        filtered_df[
            [
                "hand_id",
                "time",
                "position",
                "stakes",
                "hole_cards",
                "net_profit",
                "net_profit_before_rake",
                "rake_amount",
                "total_pot_size",
                "total_contributed",
                "total_collected",
                "went_to_showdown",
                "won_when_saw_flop",
                "preflop_raised",
                "cbet_flop",
            ]
        ],
        width="stretch",
    )

def export_data(df: pd.DataFrame):
    """Export data to CSV"""
    if df is None or df.empty:
        return

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Hero Analysis Data (CSV)",
        data=csv,
        file_name=f"hero_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


def render_external_tools():
    st.header("🃏 Hand Replayer")
    # riropo
    st.components.v1.html(
        """
        
        <button onclick="handleClick()">
        click me
        </button>

        <script>
        function handleClick() {
            localStorage.setItem("hh_hard_drive", 
            "UG9rZXJTdGFycyBIYW5kICMyMjQ1NjAzMzY2Mzc6ICBIb2xkJ2VtIE5vIExpbWl0IChcdTIwQUMwLjAxL1x1MjBBQzAuMDIgRVVSKSAtIDIwMjEvMDMvMDcgMTc6MzI6MjQgV0VUIFsyMDIxLzAzLzA3IDEyOjMyOjI0IEVUXQ0KVGFibGUgJ0dyb2dsZXInIDYtbWF4IFNlYXQgIzUgaXMgdGhlIGJ1dHRvbg0KU2VhdCAxOiByZWxpYXMyMjA1IChcdTIwQUMzLjIzIGluIGNoaXBzKSANClNlYXQgMjogQ2Fzw6kzIChcdTIwQUMwLjcwIGluIGNoaXBzKSANClNlYXQgMzogdmlrY2NoIChcdTIwQUMzLjk4IGluIGNoaXBzKSANClNlYXQgNDogWWFubmlja1BhenluIChcdTIwQUMyLjIwIGluIGNoaXBzKSANClNlYXQgNTogbXUzMGpvIChcdTIwQUMyLjEzIGluIGNoaXBzKSANClNlYXQgNjogUsO6YmVuIEJhYmF1IChcdTIwQUMyLjAxIGluIGNoaXBzKSANClLDumJlbiBCYWJhdTogcG9zdHMgc21hbGwgYmxpbmQgXHUyMEFDMC4wMQ0KcmVsaWFzMjIwNTogcG9zdHMgYmlnIGJsaW5kIFx1MjBBQzAuMDINCioqKiBIT0xFIENBUkRTICoqKg0KRGVhbHQgdG8gdmlrY2NoIFs3YyA1aF0NCkNhc8OpMyBoYXMgdGltZWQgb3V0DQpDYXPDqTM6IGZvbGRzIA0KdmlrY2NoIGhhcyB0aW1lZCBvdXQNCnZpa2NjaDogZm9sZHMgDQpZYW5uaWNrUGF6eW46IGZvbGRzIA0KbXUzMGpvOiBmb2xkcyANClLDumJlbiBCYWJhdTogcmFpc2VzIFx1MjBBQzAuMDQgdG8gXHUyMEFDMC4wNg0KcmVsaWFzMjIwNTogZm9sZHMgDQpVbmNhbGxlZCBiZXQgKFx1MjBBQzAuMDQpIHJldHVybmVkIHRvIFLDumJlbiBCYWJhdQ0KUsO6YmVuIEJhYmF1IGNvbGxlY3RlZCBcdTIwQUMwLjA0IGZyb20gcG90DQpSw7piZW4gQmFiYXU6IGRvZXNuJ3Qgc2hvdyBoYW5kIA0KKioqIFNVTU1BUlkgKioqDQpUb3RhbCBwb3QgXHUyMEFDMC4wNCB8IFJha2UgXHUyMEFDMCANClNlYXQgMTogcmVsaWFzMjIwNSAoYmlnIGJsaW5kKSBmb2xkZWQgYmVmb3JlIEZsb3ANClNlYXQgMjogQ2Fzw6kzIGZvbGRlZCBiZWZvcmUgRmxvcCAoZGlkbid0IGJldCkNClNlYXQgMzogdmlrY2NoIGZvbGRlZCBiZWZvcmUgRmxvcCAoZGlkbid0IGJldCkNClNlYXQgNDogWWFubmlja1BhenluIGZvbGRlZCBiZWZvcmUgRmxvcCAoZGlkbid0IGJldCkNClNlYXQgNTogbXUzMGpvIChidXR0b24pIGZvbGRlZCBiZWZvcmUgRmxvcCAoZGlkbid0IGJldCkNClNlYXQgNjogUsO6YmVuIEJhYmF1IChzbWFsbCBibGluZCkgY29sbGVjdGVkIChcdTIwQUMwLjA0KQ0KDQoNCg0KDQo=");
            console.debug("debug hh_hard_drive")
        }
        </script>
        <div style=\"display: flex;\">
            <iframe src="https://sboogway.github.io/riropo" width="1066" height="714" style="border: none"></iframe>
            <iframe src="https://sboogway.github.io/pokertools/odds" width="500" height="714" style="border: none"></iframe>
        </div>
        """,
        height=600,
    )

    st.markdown(
        " thanks to [vikcch](https://github.com/vikcch) for the [hand replayer](https://github.com/vikcch/riropo) ❤️"
    )

    render_expected_bankroll_chart()

    st.header("🎚️ Range Analysis")

    st.components.v1.html(
        f'<iframe src="https://sboogway.github.io/pokertools" width="1104" height="669" style="border: none"></iframe>',
        height=669,
    )

    st.header("Odds calulator")

    st.components.v1.html(
        f"",
        height=669,
    )