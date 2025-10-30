import requests


BASE_URL = "https://poker-api-v2.caduceus.lol"

# for dev
# BASE_URL = "http://localhost:8008"


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

def get_sessions():
    return requests.get(
        f"{BASE_URL}/api/v1/sessions"
    ).json()

def get_rake_pot():
    return requests.get(
        f"{BASE_URL}/api/v1/rake"
    ).json()

def get_players():
    return requests.get(
        f"{BASE_URL}/api/v1/players"
    ).json()