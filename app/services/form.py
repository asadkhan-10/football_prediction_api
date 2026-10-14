# app/services/form.py
import logging
from datetime import datetime

from sqlalchemy.orm import Session
from app import models
from app.services.cache import get_cached, set_cached

logger = logging.getLogger(__name__)

def get_team_form(team_id: int, db: Session, last_n: int = 5,
                  as_of: datetime | None = None) -> dict:
    """
    Calculate a team's form based on their last N completed fixtures.
    If as_of is given, only fixtures played before that moment are used
    (needed to evaluate past predictions without leaking the result).
    Returns a dict with:
    - wins, draws, losses
    - goals_scored, goals_conceded
    - form_string: e.g. "WDLWW"
    - points: 3 per win, 1 per draw
    """
    if as_of is not None and as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware (use datetime.now(timezone.utc) or similar)")
    cache_key = f"team_form:{team_id}:{last_n}"

    # Cache is only for live requests. Historical (as_of) calls skip it.
    if as_of is None:
        cached = get_cached(cache_key)
        if cached:
            logger.debug("Cache HIT for %s", cache_key)
            return cached
        logger.debug("Cache MISS for %s", cache_key)

    # Fixtures where this team played (home or away) and the match has a result
    query = db.query(models.Fixture).filter(
        (models.Fixture.home_team_id == team_id) |
        (models.Fixture.away_team_id == team_id),
        models.Fixture.home_score != None,
        models.Fixture.away_score != None,
    )

    # Strictly before as_of, so the match being predicted is never included
    if as_of is not None:
        query = query.filter(models.Fixture.match_date < as_of)

    fixtures = query.order_by(models.Fixture.match_date.desc()).limit(last_n).all()

    wins = draws = losses = goals_scored = goals_conceded = 0
    form_string = ""

    for fixture in fixtures:
        if fixture.home_team_id == team_id:  # type: ignore
            scored = fixture.home_score
            conceded = fixture.away_score
        else:
            scored = fixture.away_score
            conceded = fixture.home_score

        goals_scored += scored
        goals_conceded += conceded

        if scored > conceded:  # type: ignore
            wins += 1
            form_string += "W"
        elif scored == conceded:  # type: ignore
            draws += 1
            form_string += "D"
        else:
            losses += 1
            form_string += "L"

    points = (wins * 3) + (draws * 1)

    result = {
        "team_id": team_id,
        "matches_analyzed": len(fixtures),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,
        "goal_difference": goals_scored - goals_conceded,
        "points": points,
        "form_string": form_string,  # most recent first, e.g. "WDLWW"
    }

    if as_of is None:
        set_cached(cache_key, result)
    return result