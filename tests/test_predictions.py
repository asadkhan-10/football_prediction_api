# tests/test_predictions.py
from fastapi import status
from app import models


def test_create_prediction(client, sample_fixture, db):
    # Need more fixtures for form calculation to work
    # Add a loss for away team so prediction has data
    response = client.post(f"/predictions/{sample_fixture.id}")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["fixture_id"] == sample_fixture.id
    assert data["predicted_winner"] in ["Test FC", "Away FC", "Draw"]
    assert 0 <= data["home_win_prob"] <= 1
    assert 0 <= data["away_win_prob"] <= 1
    assert 0 <= data["draw_prob"] <= 1


def test_create_duplicate_prediction(client, sample_fixture):
    client.post(f"/predictions/{sample_fixture.id}")
    response = client.post(f"/predictions/{sample_fixture.id}")
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_prediction(client, sample_fixture):
    client.post(f"/predictions/{sample_fixture.id}")
    response = client.get(f"/predictions/{sample_fixture.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["fixture_id"] == sample_fixture.id


def test_get_prediction_not_found(client):
    response = client.get("/predictions/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_predictions(client, sample_fixture):
    client.post(f"/predictions/{sample_fixture.id}")
    response = client.get("/predictions/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    