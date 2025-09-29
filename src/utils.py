import re


class CardRank:

    _order = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "T": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
    }

    @classmethod
    def value(cls, rank: str) -> int:
        """Return the numeric value of a rank symbol."""
        if rank not in cls._order:
            raise ValueError(f"Invalid rank: {rank!r}")
        return cls._order[rank]

    @classmethod
    def compare(cls, r1: str, r2: str) -> int:
        """
        Compare two rank symbols.

        Returns:
            -1 if r1 < r2
             0 if r1 == r2
             1 if r1 > r2
        """
        v1, v2 = cls.value(r1), cls.value(r2)
        return (v1) - (v2) if v1 != v2 else 0

    @classmethod
    def sort(cls, ranks: list[str]) -> list[str]:
        """Return a new list of rank symbols sorted from lowest to highest."""
        return sorted(ranks, key=lambda r: cls.value(r))

    @classmethod
    def __lt__(cls, other):
        """Enable direct comparison of rank symbols using <, <=, >, >=."""
        return cls.value(cls) < cls.value(other)


def categorize_hand(hand: str) -> str:
    if len(hand) < 5:
        return ""

    c1, c2 = hand.split()

    if CardRank.compare(c1[0], c2[0]) == 0:
        return c1[0] + c1[0]

    elif CardRank.compare(c1[0], c2[0]) <= -1:
        if c1[1] == c2[1]:
            return c2[0] + c1[0] + "s"
        else:
            return c2[0] + c1[0] + "o"

    elif CardRank.compare(c1[0], c2[0]) >= 1:
        if c1[1] == c2[1]:
            return c1[0] + c2[0] + "s"
        else:
            return c1[0] + c2[0] + "o"
