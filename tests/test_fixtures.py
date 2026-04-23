# tests/test_fixtures.py
from fastapi import status


def test_get_fixtures_empty(client):
    response = client.get("/fixtures/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_fixtures_with_data(client, sample_fixture):
    response = client.get("/fixtures/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["external_id"] == 7777
    assert data[0]["home_score"] == 2
    assert data[0]["away_score"] == 1


def test_get_single_fixture(client, sample_fixture):
    response = client.get(f"/fixtures/{sample_fixture.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "FINISHED"
    assert data["external_id"] == 7777


def test_get_fixture_not_found(client):
    response = client.get("/fixtures/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND