import os
from supabase import create_client, Client
from dotenv import load_dotenv



def get_supabase_client() -> Client:
    load_dotenv()
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def test_client():
    client = get_supabase_client()
    response = client.rpc("hello_world").execute()
    print(response)
    response = client.rpc("echo", {"say": "yo dawg"}).execute()
    print(response)
    response = client.rpc("create_user_table", {"user_name": "test1212"}).execute()
    print(response)



if __name__ == "__main__":
    test_client()