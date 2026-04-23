# tests/test_teams.py
from fastapi import status


def test_get_teams_empty(client):
    response = client.get("/teams/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_teams_with_data(client, sample_team):
    response = client.get("/teams/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test FC"
    assert data[0]["tla"] == "TST"


def test_get_single_team(client, sample_team):
    response = client.get(f"/teams/{sample_team.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test FC"
    assert data["external_id"] == 9999


def test_get_team_not_found(client):
    response = client.get("/teams/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_team_form(client, sample_fixture, sample_team):
    response = client.get(f"/teams/{sample_team.id}/form")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["team_id"] == sample_team.id
    assert data["matches_analyzed"] == 1
    assert data["wins"] == 1
    assert data["losses"] == 0
    assert data["form_string"] == "W"