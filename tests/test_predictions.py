# tests/test_predictions.py
from fastapi import status
from app import models  
import pytest
from app.services.prediction import calculate_probabilities, team_strength
from app.services import prediction


def test_create_prediction(client, sample_fixture, db, auth_headers):
    response = client.post(f"/predictions/{sample_fixture.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["fixture_id"] == sample_fixture.id
    assert data["predicted_winner"] in ["Test FC", "Away FC", "Draw"]
    assert 0 <= data["home_win_prob"] <= 1
    assert 0 <= data["away_win_prob"] <= 1
    assert 0 <= data["draw_prob"] <= 1


def test_create_duplicate_prediction(client, sample_fixture, auth_headers):
    client.post(f"/predictions/{sample_fixture.id}", headers=auth_headers)
    response = client.post(f"/predictions/{sample_fixture.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_prediction(client, sample_fixture, auth_headers):
    client.post(f"/predictions/{sample_fixture.id}", headers=auth_headers)
    response = client.get(f"/predictions/{sample_fixture.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["fixture_id"] == sample_fixture.id


def test_get_prediction_not_found(client):
    response = client.get("/predictions/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_predictions(client, sample_fixture, auth_headers):
    client.post(f"/predictions/{sample_fixture.id}", headers=auth_headers)
    response = client.get("/predictions/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1




@pytest.mark.parametrize("h", [-6, -2, 0, 1.5, 4])
@pytest.mark.parametrize("a", [-6, -2, 0, 1.5, 4])
def test_probabilities_are_valid(h, a):
    p = calculate_probabilities(h, a)
    assert all(v >= 0 for v in p.values())
    assert sum(p.values()) == pytest.approx(1.0, abs=0.011)


def test_stronger_home_team_raises_home_win():
    weak = calculate_probabilities(0, 2)["home_win"]
    strong = calculate_probabilities(2, 2)["home_win"]
    assert strong > weak


def test_equal_teams_favour_home():
    p = calculate_probabilities(1.0, 1.0)
    assert p["home_win"] > p["away_win"]


def test_no_matches_gives_none():
    assert team_strength({"matches_analyzed": 0, "points": 0, "goal_difference": 0}) is None




def _form(points, gd, n=5):
    return {"matches_analyzed": n, "points": points, "goal_difference": gd}


def test_predict_match_no_data_is_neutral(monkeypatch):
    monkeypatch.setattr(prediction, "get_team_form", lambda team_id, db, as_of=None: _form(0, 0, n=0))
    result = prediction.predict_match(1, 2, db=None)
    assert result["home_win_probability"] == 0.40
    assert result["predicted_outcome"] == "home_win"


def test_predict_match_bad_home_team_not_favoured(monkeypatch):
    forms = {1: _form(0, -8), 2: _form(13, 9)}
    monkeypatch.setattr(prediction, "get_team_form", lambda team_id, db, as_of=None: forms[team_id])
    result = prediction.predict_match(1, 2, db=None)
    assert result["predicted_outcome"] == "away_win"
    total = (result["home_win_probability"] + result["draw_probability"]
             + result["away_win_probability"])
    assert total == pytest.approx(1.0, abs=0.011)