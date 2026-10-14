# app/services/prediction.py
from datetime import datetime

from sqlalchemy.orm import Session
from app.services.form import get_team_form

import math

HOME_ADVANTAGE = 0.3   # in points-per-match units
GD_WEIGHT = 0.5        # how much goal difference counts vs points
BASE_DRAW = 0.30       # draw probability for two equal teams
DRAW_DECAY = 0.10      # draw shrinks as teams get further apart
MIN_DRAW = 0.15


def team_strength(form: dict) -> float | None:
    """Per-match strength, so a team with 3 games isn't compared unfairly to one with 5."""
    n = form["matches_analyzed"]
    if n == 0:
        return None
    return form["points"] / n + GD_WEIGHT * (form["goal_difference"] / n)


def calculate_probabilities(home_strength: float, away_strength: float) -> dict:
    diff = home_strength - away_strength + HOME_ADVANTAGE
    draw = max(MIN_DRAW, BASE_DRAW - DRAW_DECAY * abs(diff))
    home_share = 1 / (1 + math.exp(-diff))   # always between 0 and 1, even for negative diff
    home = round((1 - draw) * home_share, 2)
    away = round((1 - draw) * (1 - home_share), 2)
    return {"home_win": home, "draw": round(1 - home - away, 2), "away_win": away}


NEUTRAL_PROBABILITIES = {"home_win": 0.40, "draw": 0.30, "away_win": 0.30}


def predict_match(home_team_id: int, away_team_id: int, db: Session,
                  as_of: datetime | None = None) -> dict:
    home_form = get_team_form(team_id=home_team_id, db=db, as_of=as_of)
    away_form = get_team_form(team_id=away_team_id, db=db, as_of=as_of)

    home_strength = team_strength(home_form)
    away_strength = team_strength(away_form)

    if home_strength is None or away_strength is None:
        # No finished matches for one team: don't invent confidence
        probabilities = NEUTRAL_PROBABILITIES
    else:
        probabilities = calculate_probabilities(home_strength, away_strength)

    predicted_outcome = max(probabilities, key=probabilities.get)  # type: ignore

    return {
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
        "home_form": home_form,
        "away_form": away_form,
        "home_win_probability": probabilities["home_win"],
        "draw_probability": probabilities["draw"],
        "away_win_probability": probabilities["away_win"],
        "predicted_outcome": predicted_outcome,
    }