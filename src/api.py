import requests


BASE_URL = "https://poker-api.caduceus.lol"


def get_player_hands(player_id: str, session_id: str | None):
    return requests.get(
        f"{BASE_URL}/api/v1/get",
        params={"player_id": player_id, "session_id": session_id},
    ).json()
