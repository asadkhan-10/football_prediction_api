# tests/test_form_as_of.py
from datetime import datetime, timedelta, timezone

import pytest

from app import models
from app.services.form import get_team_form

BASE = datetime(2026, 1, 1, 15, 0, tzinfo=timezone.utc)


def match_day(i: int) -> datetime:
    """Match i is played i weeks after BASE."""
    return BASE + timedelta(weeks=i)


@pytest.fixture()
def team_with_six_matches(db):
    """
    One team (home in all 6 fixtures). Matches 0-4 are wins (2-0),
    match 5 (the latest) is a loss (0-3).
    """
    team = models.Team(external_id=1001, name="Form FC", short_name="Form", tla="FRM")
    opponent = models.Team(external_id=1002, name="Opp FC", short_name="Opp", tla="OPP")
    db.add_all([team, opponent])
    db.commit()
    db.refresh(team)
    db.refresh(opponent)

    for i in range(6):
        home_score, away_score = (2, 0) if i < 5 else (0, 3)
        db.add(models.Fixture(
            external_id=2000 + i,
            home_team_id=team.id,
            away_team_id=opponent.id,
            match_date=match_day(i),
            home_score=home_score,
            away_score=away_score,
            status="FINISHED",
        ))
    db.commit()
    return team


def test_as_of_excludes_the_match_itself(db, team_with_six_matches):
    # Predicting match 5: its own loss must not be in the form
    form = get_team_form(team_with_six_matches.id, db, as_of=match_day(5))
    assert form["matches_analyzed"] == 5
    assert form["form_string"] == "WWWWW"
    assert form["losses"] == 0


def test_as_of_after_all_matches_includes_latest(db, team_with_six_matches):
    # Same team, cutoff after everything: latest 5 are matches 5,4,3,2,1
    form = get_team_form(team_with_six_matches.id, db, as_of=match_day(100))
    assert form["matches_analyzed"] == 5
    assert form["form_string"] == "LWWWW"


def test_as_of_with_fewer_than_five_prior_matches(db, team_with_six_matches):
    # Cutoff at match 2's kickoff: only matches 0 and 1 count (strictly before)
    form = get_team_form(team_with_six_matches.id, db, as_of=match_day(2))
    assert form["matches_analyzed"] == 2
    assert form["form_string"] == "WW"


def test_naive_as_of_is_rejected(db, team_with_six_matches):
    with pytest.raises(ValueError):
        get_team_form(team_with_six_matches.id, db, as_of=datetime(2026, 3, 1))