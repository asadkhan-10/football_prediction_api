# app/services/prediction.py
from sqlalchemy.orm import Session
from app.services.form import get_team_form




def predict_match(home_team_id: int, away_team_id: int, db: Session) -> dict:
    """
    Predict match outcome based on recent form of both teams.
    """

    home_form = get_team_form(team_id=home_team_id, db=db)
    away_form = get_team_form(team_id=away_team_id, db=db)

    # Score each team — home team gets a +3 point bonus (home advantage)
    HOME_ADVANTAGE = 3
    home_score = home_form["points"] + home_form["goal_difference"] + HOME_ADVANTAGE
    away_score = away_form["points"] + away_form["goal_difference"]

    total = home_score + away_score

    if total == 0:
        home_win_probability = 0.34
        draw_probability = 0.32
        away_win_probability = 0.34
    else:
        # Calculate raw shares
        home_raw = home_score / total        # e.g. 0.737
        away_raw = away_score / total        # e.g. 0.263

        # Scale both down by 75% to leave room for draw
        home_win_probability = round(home_raw * 0.75, 2)
        away_win_probability = round(away_raw * 0.75, 2)

        # Draw gets whatever is left — guaranteed non-negative because home + away <= 0.75
        draw_probability = round(1 - home_win_probability - away_win_probability, 2)
    # Determine predicted outcome
    probabilities = {
        "home_win": home_win_probability,
        "draw": draw_probability,
        "away_win": away_win_probability,
    }
    # Clamp to prevent negative probabilities from rounding
    home_win_probability = max(0.0, home_win_probability)
    away_win_probability = max(0.0, away_win_probability)
    draw_probability = max(0.0, draw_probability)
    predicted_outcome = max(probabilities, key=probabilities.get)  # type: ignore

    return {
        "home_team_id": home_team_id,
        "away_team_id": away_team_id,
        "home_form": home_form,
        "away_form": away_form,
        "home_win_probability": home_win_probability,
        "draw_probability": draw_probability,
        "away_win_probability": away_win_probability,
        "predicted_outcome": predicted_outcome,
    }
