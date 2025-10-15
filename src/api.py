import requests


BASE_URL = "https://poker-api.caduceus.lol"


def get_player_hands(player_id: str, session_id: str | None):
    return requests.get(
        f"{BASE_URL}/api/v1/get",
        params={"player_id": player_id, "session_id": session_id},
    ).json()

def upload_hands(file):
    return requests.post(
        f"{BASE_URL}/api/v1/upload",
        files=file
    ).json()

def analyze_hands(player_id):
    return requests.post(
        f"{BASE_URL}/api/v1/analyze", params=dict(username=player_id)
    ).json()