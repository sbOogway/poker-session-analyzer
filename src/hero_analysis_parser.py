import os
import glob
import re
import pandas as pd
import logging
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from pprint import pprint, pformat
import traceback


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(f"logs/{datetime.now().isoformat()}.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)


logger.addHandler(file_handler)
logger.addHandler(console_handler)


@dataclass
class HeroData:
    """Streamlined Hero-specific data for analysis"""

    hand_id: str
    timestamp: datetime
    site: str
    stakes: str
    table_name: str
    position: str
    hole_cards: List[str]

    # Key analysis metrics
    went_to_showdown: bool = False
    won_at_showdown: bool = False  # W$SD - Won at Showdown (boolean)
    won_when_saw_flop: bool = False
    saw_flop: bool = False

    # Financial data
    total_contributed: float = 0.0
    total_collected: float = 0.0
    net_profit: float = 0.0

    # Rake analysis
    rake_amount: float = 0.0
    net_profit_before_rake: float = 0.0
    net_profit_after_rake: float = 0.0
    total_pot_size: float = 0.0

    # Hand progression
    preflop_actions: int = 0
    flop_actions: int = 0
    turn_actions: int = 0
    river_actions: int = 0

    # Board cards
    flop_cards: List[str] = field(default_factory=list)
    turn_card: str = ""
    river_card: str = ""

    # Hand strength indicators
    preflop_raised: bool = False
    preflop_called: bool = False
    vpip: bool = False  # Voluntarily Put money In Pot (excluding blinds)
    cbet_flop: bool = False
    cbet_turn: bool = False
    cbet_river: bool = False
    cbet_flop_opportunity: bool = False  # Hero was aggressor on previous street
    cbet_turn_opportunity: bool = False
    cbet_river_opportunity: bool = False


class HeroAnalysisParser:
    """Streamlined parser focused on Hero data analysis only"""

    def __init__(self):
        self.site_patterns = {
            "PokerStars": r"PokerStars",
            "888poker": r"888poker|888 Poker",
            "ACR": r"Americas Cardroom|ACR",
            "GGPoker": r"GGPoker|GG Poker",
            "PartyPoker": r"PartyPoker|Party Poker",
            "Winamax": r"Winamax",
            "Unibet": r"Unibet",
            "Bet365": r"Bet365",
            "William Hill": r"William Hill",
        }

    def extract_site(self, hand_text: str) -> str:
        """Extract poker site from hand text"""
        for site, pattern in self.site_patterns.items():
            if re.search(pattern, hand_text, re.IGNORECASE):
                return site
        return "Unknown"

    def extract_hand_id(self, hand_text: str) -> str:
        """Extract hand ID from the header"""
        m = re.search(r"Hand #([A-Z0-9]+)", hand_text)
        return m.group(1) if m else ""

    def extract_timestamp(self, hand_text: str) -> datetime:
        """Extract timestamp from the header"""
        m = re.search(r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})", hand_text)
        if m:
            return datetime.strptime(m.group(1), "%Y/%m/%d %H:%M:%S")
        return datetime.now()

    def extract_table_name(self, hand_text: str) -> str:
        """Extract table name from the header"""
        m = re.search(r"Table '([^']+)'", hand_text)
        return m.group(1) if m else ""

    def extract_stakes(self, hand_text: str, currency: str) -> str:
        """Extract stakes from the header"""
        if currency == "$":
            m = re.search(r"\((\$[\d\.]+\/\$[\d\.]+)\)", hand_text)
        else:
            m = re.search(
                r"\((" + currency + r"[\d\.]+\/" + currency + r"[\d\.]+)\)", hand_text
            )
        # print(hand_text)
        if m:
            return m.group(1)
        else:
            # pprint(hand_text)
            logger.debug("stakes not found")
            return ""

    def extract_hero_position(self, hand_text: str, username: str) -> str:
        """Extract Hero's position"""
        # Find Hero's seat
        hero_seat = None
        button_seat = 1

        # Extract button seat
        m = re.search(r"Seat #(\d+) is the button", hand_text, re.IGNORECASE)
        if m:
            button_seat = int(m.group(1))

        # Find Hero's seat
        m = re.search(r"Seat (\d+): " + username, hand_text, re.IGNORECASE)
        if m:
            hero_seat = int(m.group(1))

        if hero_seat:
            positions = [
                "Button",
                "Small Blind",
                "Big Blind",
                "UTG",
                "Hijack",
                "Cutoff",
            ]
            index = (hero_seat - button_seat) % len(positions)
            return positions[index]

        return "Unknown"

    def extract_hero_hole_cards(self, hand_text: str, username: str) -> List[str]:
        """Extract Hero's hole cards"""
        m = re.search(
            r"Dealt to " + username + r"\s*\[([^\]]+)\]", hand_text, re.IGNORECASE
        )
        if m:
            return m.group(1).strip().split()
        # pprint(hand_text)
        logger.debug("error extracting hero hole cards")
        return []

    def extract_board_cards(
        self, hand_text: str
    ) -> Tuple[List[str], List[str], str, str]:
        """Extract board cards with street separation"""
        flop_cards = []
        turn_card = ""
        river_card = ""

        # Extract flop
        m = re.search(r"\*\*\* FLOP \*\*\*\s*\[([^\]]+)\]", hand_text, re.IGNORECASE)
        if m:
            flop_cards = m.group(1).strip().split()

        # Extract turn
        m = re.search(
            r"\*\*\* TURN \*\*\*\s*\[[^\]]+\]\s*\[([^\]]+)\]", hand_text, re.IGNORECASE
        )
        if m:
            turn_card = m.group(1).strip()

        # Extract river
        m = re.search(
            r"\*\*\* RIVER \*\*\*\s*\[[^\]]+\]\s*\[([^\]]+)\]", hand_text, re.IGNORECASE
        )
        if m:
            river_card = m.group(1).strip()

        board_cards = (
            flop_cards
            + ([turn_card] if turn_card else [])
            + ([river_card] if river_card else [])
        )
        return board_cards, flop_cards, turn_card, river_card

    def extract_rake_info(self, hand_text: str, currency: str) -> Tuple[float, float]:
        """Extract total rake amount (including jackpot and other fees) and total pot size from summary"""
        total_rake_amount = 0.0
        total_pot_size = 0.0

        # Look for comprehensive summary line with all fees
        # Format: "Total pot $X.XX | Rake $Y.YY | Jackpot $Z.ZZ | Bingo $A.AA | Fortune $B.BB | Tax $C.CC"
        comprehensive_pattern = r"Total pot\s*\$([\d.]+)\s*\|\s*Rake\s*\$([\d.]+)(?:\s*\|\s*Jackpot\s*\$([\d.]+))?(?:\s*\|\s*Bingo\s*\$([\d.]+))?(?:\s*\|\s*Fortune\s*\$([\d.]+))?(?:\s*\|\s*Tax\s*\$([\d.]+))?"

        # if currency == "€":
        #     comprehensive_pattern = r"Total pot\s€[\d.]+\s\|\sRake\s[\d.]+"

        m = re.search(comprehensive_pattern, hand_text, re.IGNORECASE)

        if m:
            total_pot_size = float(m.group(1))
            rake_amount = float(m.group(2))
            jackpot_amount = float(m.group(3)) if m.group(3) else 0.0
            bingo_amount = float(m.group(4)) if m.group(4) else 0.0
            fortune_amount = float(m.group(5)) if m.group(5) else 0.0
            tax_amount = float(m.group(6)) if m.group(6) else 0.0

            # Sum all fees as total rake
            total_rake_amount = (
                rake_amount
                + jackpot_amount
                + bingo_amount
                + fortune_amount
                + tax_amount
            )
        else:
            # Fallback: Look for individual fee patterns
            fee_patterns = [
                (r"Rake\s*\$([\d.]+)", "rake"),
                (r"Jackpot\s*\$([\d.]+)", "jackpot"),
                (r"Bingo\s*\$([\d.]+)", "bingo"),
                (r"Fortune\s*\$([\d.]+)", "fortune"),
                (r"Tax\s*\$([\d.]+)", "tax"),
                (r"Rake taken:\s*\$([\d.]+)", "rake"),
                (r"Rake:\s*\$([\d.]+)", "rake"),
                (r"Rake:\s*" + currency + r"([\d.]+)", "rake"),
                (r"Rake " + currency + r"([\d.]+)", "rake"),
            ]

            for pattern, fee_type in fee_patterns:
                m = re.search(pattern, hand_text, re.IGNORECASE)
                if m:
                    amount = float(m.group(1))
                    total_rake_amount += amount

            # Try to find total pot size separately
            pot_patterns = [
                r"Total pot\s*\$([\d.]+)",
                r"Pot size\s*\$([\d.]+)",
                r"Total\s*\$([\d.]+)",
                r"Total pot " + currency + r"([\d.]+)"
            ]

            for pattern in pot_patterns:
                m = re.search(pattern, hand_text, re.IGNORECASE)
                if m:
                    total_pot_size = float(m.group(1))
                    break

        logger.debug(f"rake and pot size debug {total_rake_amount} {total_pot_size}")

        return total_rake_amount, total_pot_size

    def detect_multi_player_showdown(self, hand_text: str, username: str) -> bool:
        """Detect if there was a multi-player showdown (2+ players showed cards)"""
        showdown_players = 0

        # Look for "shows" or "showed" patterns for all players
        showdown_patterns = [
            r"(?mi)^(?:"
            + username
            + r"\b|Seat\s+\d+:\s*"
            + username
            + r"\b).*?(shows|showed)",
            r"(?mi)^(?:Seat\s+\d+:\s*[^H][^e][^r][^o]\w*).*?(shows|showed)",
            r"(?mi)^(?:Seat\s+\d+:\s*\w+).*?(shows|showed)",
        ]

        for pattern in showdown_patterns:
            matches = re.findall(pattern, hand_text)
            showdown_players += len(matches)

        return showdown_players >= 2

    def analyze_hero_actions(self, hand_text: str, username: str, currency: str) -> Dict[str, Any]:
        """Clean version of analyze_hero_actions without debug output"""
        hero_pattern = re.compile(
            username + r": |^(?:" + username + r"\b|Seat\s+\d+:\s*" + username + r"\b)", re.IGNORECASE
        )
        street_marker = re.compile(r"^\*\*\*")

        actions = {
            "total_contributed": 0.0,
            "total_collected": 0.0,
            "preflop_actions": 0,
            "flop_actions": 0,
            "turn_actions": 0,
            "river_actions": 0,
            "preflop_raised": False,
            "preflop_called": False,
            "vpip": False,  # Voluntarily Put money In Pot (excluding blinds)
            "cbet_flop": False,
            "cbet_turn": False,
            "cbet_river": False,
            "cbet_flop_opportunity": False,  # Hero was aggressor on previous street
            "cbet_turn_opportunity": False,
            "cbet_river_opportunity": False,
            "went_to_showdown": False,
            "won_at_showdown": False,  # W$SD - Won at Showdown (boolean)
            "saw_flop": False,
            "rake_amount": 0.0,
            "total_pot_size": 0.0,
        }

        current_street = "preflop"
        current_round = 0.0

        # C-bet tracking variables
        last_aggressor_by_street = {"preflop": "", "flop": "", "turn": "", "river": ""}
        first_bet_made_by_street = {"flop": False, "turn": False, "river": False}

        for line in hand_text.splitlines():

            line = line.strip()
            logger.debug(f"line => {line}")
            if not line:
                continue

            # Detect street changes
            if street_marker.match(line):
                if "HOLE CARDS" not in line.upper():
                    # Extract street name from markers like "*** FIRST FLOP ***", "*** TURN ***", etc.
                    street_line = line.replace("***", "").replace("*", "").strip()

                    # Normalize street names
                    if "flop" in street_line.lower():
                        current_street = "flop"
                        # C-bet opportunity on flop if Hero was last aggressor on preflop
                        actions["cbet_flop_opportunity"] = (
                            last_aggressor_by_street.get("preflop") == username
                        )
                    elif "turn" in street_line.lower():
                        current_street = "turn"
                        # C-bet opportunity on turn if Hero was last aggressor on flop
                        actions["cbet_turn_opportunity"] = (
                            last_aggressor_by_street.get("flop") == username
                        )
                    elif "river" in street_line.lower():
                        current_street = "river"
                        # C-bet opportunity on river if Hero was last aggressor on turn
                        actions["cbet_river_opportunity"] = (
                            last_aggressor_by_street.get("turn") == username
                        )
                    elif "showdown" in street_line.lower():
                        current_street = "showdown"
                    else:
                        current_street = street_line.lower()

                    current_round = 0.0
                continue

            if hero_pattern.search(line):
                logger.debug("hero pattern found")
                # Track street-specific actions
                if current_street == "preflop":
                    actions["preflop_actions"] += 1
                elif current_street == "flop":
                    actions["flop_actions"] += 1
                    actions["saw_flop"] = True
                elif current_street == "turn":
                    actions["turn_actions"] += 1
                elif current_street == "river":
                    actions["river_actions"] += 1

                # Analyze specific actions
                if "collected" in line and "from pot" in line:
                    m = re.search(r"collected\s*\(?\$([\d.]+)\)?", line, re.IGNORECASE)

                    if currency != "$":
                        m = re.search(r"collected\s*" + currency+ r"([\d.]+)", line, re.IGNORECASE)

                    if m:
                        amount = float(m.group(1))
                        actions["total_collected"] += amount
                        # W$SD only counts if there was a multi-player showdown
                        # This will be set later when we detect showdown patterns

                elif "posts" in line:
                    m = re.search(r"\$([\d.]+)", line)

                    if currency != "$":
                        m = re.search(currency+ r"([\d.]+)", line, re.IGNORECASE)

                    if m:
                        amount = float(m.group(1))
                        actions["total_contributed"] += amount
                        current_round += amount

                elif "calls" in line:
                    actions["preflop_called"] = True
                    actions["vpip"] = True  # VPIP: voluntarily put money in pot
                    m = re.search(r"\$([\d.]+)", line)
                    if currency != "$":
                        m = re.search(currency+ r"([\d.]+)", line, re.IGNORECASE)
                    if m:
                        amount = float(m.group(1))
                        actions["total_contributed"] += amount
                        current_round += amount

                elif "bets" in line:
                    actions["vpip"] = True  # VPIP: voluntarily put money in pot
                    m = re.search(r"\$([\d.]+)", line)
                    if currency != "$":
                        m = re.search(currency+ r"([\d.]+)", line, re.IGNORECASE)
                    if m:
                        amount = float(m.group(1))
                        actions["total_contributed"] += amount
                        current_round += amount

                        # Check for continuation bets: must be first bet on street and Hero was prior street aggressor
                        if current_street in ("flop", "turn", "river"):
                            if not first_bet_made_by_street[current_street]:
                                if (
                                    current_street == "flop"
                                    and actions["cbet_flop_opportunity"]
                                ):
                                    actions["cbet_flop"] = True
                                elif (
                                    current_street == "turn"
                                    and actions["cbet_turn_opportunity"]
                                ):
                                    actions["cbet_turn"] = True
                                elif (
                                    current_street == "river"
                                    and actions["cbet_river_opportunity"]
                                ):
                                    actions["cbet_river"] = True
                                first_bet_made_by_street[current_street] = True
                            # Any bet sets last aggressor for this street
                            last_aggressor_by_street[current_street] = username

                elif "raises" in line:
                    actions["preflop_raised"] = True
                    actions["vpip"] = True  # VPIP: voluntarily put money in pot
                    m = re.search(r"to\s*\$([\d.]+)", line, re.IGNORECASE)
                    if currency != "$":
                        m = re.search(r"to " +currency+ r"([\d.]+)", line, re.IGNORECASE)
                    if m:
                        new_total = float(m.group(1))
                        additional = new_total - current_round
                        if additional < 0:
                            additional = 0
                        actions["total_contributed"] += additional
                        current_round = new_total
                        # A raise is aggressive action; mark hero last aggressor on this street
                        if current_street in last_aggressor_by_street:
                            last_aggressor_by_street[current_street] = username

                elif "shows" in line or "showed" in line:
                    actions["went_to_showdown"] = True

            # Track any player's aggressive action to maintain last aggressor and first bet flags
            # This runs after Hero action processing to avoid interfering with c-bet logic
            generic_aggr = re.match(r"^[^:]+:\s+(bets|raises)\b", line, re.IGNORECASE)
            if generic_aggr and current_street in ("preflop", "flop", "turn", "river"):
                # Only track non-Hero players to avoid interfering with Hero's c-bet logic
                is_hero_actor = bool(hero_pattern.match(line))
                if not is_hero_actor:
                    # Mark first bet on street for non-Hero players
                    if generic_aggr.group(1).lower() == "bets":
                        if (
                            current_street in ("flop", "turn", "river")
                            and not first_bet_made_by_street[current_street]
                        ):
                            first_bet_made_by_street[current_street] = True

                    # Update last aggressor for non-Hero players
                    last_aggressor_by_street[current_street] = "villain"

            # Handle uncalled bet returns FIRST (before Hero action processing)
            # This covers scenarios where Hero bets and villain folds
            elif "uncalled bet" in line.lower() and f"returned to {username}" in line.lower():
                # Multiple patterns to catch different formats
                patterns = [
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to " + username,
                    r"Uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to " + username,
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to " + username,
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to "
                    + username
                    + r"\b",
                    r"uncalled bet\s*\(?\$([\d.]+)\)?\s*returned to "
                    + username
                    + r"\s*$",

                    r"Uncalled bet\s*\(?"+ currency + r"([\d.]+)\)?\s*returned to " + username,
                ]

                for pattern in patterns:
                    m = re.search(pattern, line, re.IGNORECASE)
                    if m:
                        amount = float(m.group(1))
                        actions["total_collected"] += amount
                        break  # Found match, stop searching

        # Check if went to showdown
        if not actions["went_to_showdown"]:
            actions["went_to_showdown"] = bool(
                re.search(
                    r"(?mi)^(?:" + username + r"\b|Seat\s+\d+:\s*" + username + r"\b).*?(shows|showed)|" + username + r": show", hand_text
                )
            )

        # Extract rake information
        rake_amount, total_pot_size = self.extract_rake_info(hand_text, currency=currency)
        actions["rake_amount"] = rake_amount
        actions["total_pot_size"] = total_pot_size

        # Calculate net profit
        actions["net_profit"] = (
            actions["total_collected"] - actions["total_contributed"]
        )

        # Calculate net profit after rake (only add rake back if Hero collected money)
        if actions["total_collected"] > 0:
            # Hero won money, so rake was taken from their winnings
            actions["net_profit_before_rake"] = actions["net_profit"] + rake_amount
        else:
            # Hero lost, so rake was taken from other players, not from Hero
            actions["net_profit_before_rake"] = actions["net_profit"]
            actions["rake_amount"] = 0

        # Determine if won when saw flop
        actions["won_when_saw_flop"] = actions["saw_flop"] and actions["net_profit"] > 0

        # Check for multi-player showdown (W$SD only counts when 2+ players show cards)
        if actions["went_to_showdown"]:
            multi_player_showdown = self.detect_multi_player_showdown(hand_text, username=username)
            # W$SD only counts if there was a multi-player showdown AND Hero won money
            if multi_player_showdown and actions["total_collected"] > 0:
                actions["won_at_showdown"] = (
                    True  # W$SD - Hero won at multi-player showdown
                )

        logger.debug(pformat(actions))

        return actions

    def parse_hand(self, hand_text: str, currency: str, username: str) -> HeroData:
        """Parse a single hand and extract Hero-specific data"""
        try:
            # Extract basic info
            hand_id = self.extract_hand_id(hand_text)
            timestamp = self.extract_timestamp(hand_text)
            site = self.extract_site(hand_text)
            table_name = self.extract_table_name(hand_text)
            stakes = self.extract_stakes(hand_text, currency)
            position = self.extract_hero_position(hand_text, username)
            hole_cards = self.extract_hero_hole_cards(hand_text, username)

            # Extract board cards
            board_cards, flop_cards, turn_card, river_card = self.extract_board_cards(
                hand_text
            )

            # Analyze Hero's actions - USE CLEAN VERSION
            action_data = self.analyze_hero_actions(hand_text, username=username, currency=currency)

            return HeroData(
                hand_id=hand_id,
                timestamp=timestamp,
                site=site,
                stakes=stakes,
                table_name=table_name,
                position=position,
                hole_cards=hole_cards,
                went_to_showdown=action_data["went_to_showdown"],
                won_at_showdown=action_data["won_at_showdown"],
                won_when_saw_flop=action_data["won_when_saw_flop"],
                saw_flop=action_data["saw_flop"],
                total_contributed=action_data["total_contributed"],
                total_collected=action_data["total_collected"],
                net_profit=action_data["net_profit"],
                rake_amount=action_data["rake_amount"],
                net_profit_before_rake=action_data["net_profit_before_rake"],
                # net_profit_after_rake=action_data["net_profit_after_rake"],
                total_pot_size=action_data["total_pot_size"],
                preflop_actions=action_data["preflop_actions"],
                flop_actions=action_data["flop_actions"],
                turn_actions=action_data["turn_actions"],
                river_actions=action_data["river_actions"],
                flop_cards=flop_cards,
                turn_card=turn_card,
                river_card=river_card,
                preflop_raised=action_data["preflop_raised"],
                preflop_called=action_data["preflop_called"],
                vpip=action_data["vpip"],
                cbet_flop=action_data["cbet_flop"],
                cbet_turn=action_data["cbet_turn"],
                cbet_river=action_data["cbet_river"],
                cbet_flop_opportunity=action_data["cbet_flop_opportunity"],
                cbet_turn_opportunity=action_data["cbet_turn_opportunity"],
                cbet_river_opportunity=action_data["cbet_river_opportunity"],
            )

        except Exception as e:
            print(traceback.print_exc())
            logger.error(f"Error parsing hand: {e}")
            return HeroData(
                hand_id="",
                timestamp=datetime.now(),
                site="Unknown",
                stakes="",
                table_name="",
                position="Unknown",
                hole_cards=[],
            )

    def parse_file(self, text: str, currency: str, username: str) -> List[HeroData]:
        """Parse a file containing multiple hands"""
        try:
            # TODO FIXME BRUV HOT FIX FOR DEBUG
            # FIXME
            # FIXME

            if currency == "$":
                hands = re.split(r"(?=Poker Hand #)", text)
            else:
                hands = re.split(r"(?=PokerStars Zoom Hand #)", text)

            # FIXME
            # FIXME
            # FIXME

            results = []
            # del hands[0]
            for hand in hands:
                if hand.strip():
                    result = self.parse_hand(hand, currency=currency, username=username)
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            return []

    def process_files(
        self, folder_path: str, currency: str, username: str
    ) -> pd.DataFrame:
        """Process all hand history files and return a DataFrame"""
        try:
            file_pattern = os.path.join(folder_path, "**", "*.txt")
            all_files = glob.glob(file_pattern, recursive=True)

            if not all_files:
                logger.warning(f"No .txt files found in {folder_path}")
                return pd.DataFrame()

            logger.info(f"Found {len(all_files)} files to process")

            all_hands = []

            for filepath in all_files:
                try:
                    logger.info(f"Processing file: {os.path.basename(filepath)}")
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()

                    hands = self.parse_file(text, currency=currency, username=username)
                    all_hands.extend(hands)

                except Exception as e:
                    logger.error(f"Error processing file {filepath}: {e}")
                    continue

            if not all_hands:
                logger.warning("No hands processed")
                return pd.DataFrame()

            # Convert to DataFrame
            data = []
            for hand in all_hands:
                data.append(
                    {
                        "Hand_ID": hand.hand_id,
                        "Timestamp": hand.timestamp,
                        "Site": hand.site,
                        "Stakes": hand.stakes,
                        "Table_Name": hand.table_name,
                        "Position": hand.position,
                        "Hole_Cards": " ".join(hand.hole_cards),
                        "Went_to_Showdown": hand.went_to_showdown,
                        "Won_at_Showdown": hand.won_at_showdown,
                        "Won_When_Saw_Flop": hand.won_when_saw_flop,
                        "Saw_Flop": hand.saw_flop,
                        "Total_Contributed": hand.total_contributed,
                        "Total_Collected": hand.total_collected,
                        "Net_Profit": hand.net_profit,
                        "Rake_Amount": hand.rake_amount,
                        "Net_Profit_Before_Rake": hand.net_profit_before_rake,
                        "Net_Profit_After_Rake": hand.net_profit_after_rake,
                        "Total_Pot_Size": hand.total_pot_size,
                        "Preflop_Actions": hand.preflop_actions,
                        "Flop_Actions": hand.flop_actions,
                        "Turn_Actions": hand.turn_actions,
                        "River_Actions": hand.river_actions,
                        "Flop_Cards": " ".join(hand.flop_cards),
                        "Turn_Card": hand.turn_card,
                        "River_Card": hand.river_card,
                        "Preflop_Raised": hand.preflop_raised,
                        "Preflop_Called": hand.preflop_called,
                        "VPIP": hand.vpip,
                        "CBet_Flop": hand.cbet_flop,
                        "CBet_Turn": hand.cbet_turn,
                        "CBet_River": hand.cbet_river,
                        "CBet_Flop_Opportunity": hand.cbet_flop_opportunity,
                        "CBet_Turn_Opportunity": hand.cbet_turn_opportunity,
                        "CBet_River_Opportunity": hand.cbet_river_opportunity,
                    }
                )

            df = pd.DataFrame(data)
            df = df.sort_values("Timestamp")

            # Add running totals
            df["Running_Profit"] = df["Net_Profit"].cumsum()
            df["Running_Profit_Before_Rake"] = df["Net_Profit_Before_Rake"].cumsum()
            df["Running_Rake"] = df["Rake_Amount"].cumsum()
            df["Hand_Number"] = range(1, len(df) + 1)

            logger.info(f"Successfully processed {len(df)} hands")
            return df

        except Exception as e:
            logger.error(f"Error in process_files: {e}")
            return pd.DataFrame()


def main():
    """Main function for testing the parser"""

if __name__ == "__main__":
    main()
