import httpx
from app.config import settings

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": settings.football_api_key}


def get_premier_league_teams() -> dict:
    response = httpx.get(
        f"{BASE_URL}/competitions/PL/teams",
        headers=HEADERS,
        timeout=10.0
    )
    response.raise_for_status()
    return response.json()


def get_premier_league_fixtures() -> dict:
    response = httpx.get(
        f"{BASE_URL}/competitions/PL/matches",
        headers=HEADERS,
        timeout=10.0
    )
    response.raise_for_status()
    return response.json()