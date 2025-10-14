import requests


BASE_URL = "https://poker-api.caduceus.lol"

def get_player_hands(player_id: str):
    return requests.get(f"{BASE_URL}/api/v1/get?username={player_id}").json()