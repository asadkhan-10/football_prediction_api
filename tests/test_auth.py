from types import SimpleNamespace

import pytest

from app.config import settings
from app.routers import fixtures, teams

PROTECTED = ["/teams/sync", "/fixtures/sync", "/predictions/1"]


class FakeTask:
    def delay(self):
        return SimpleNamespace(id="fake-task-id")


@pytest.fixture()
def fake_tasks(monkeypatch):
    # No Redis or Celery broker needed, and no real sync can ever start
    monkeypatch.setattr(teams, "sync_teams_task", FakeTask())
    monkeypatch.setattr(fixtures, "sync_fixtures_task", FakeTask())


# auth_headers also sets the server key to "testkey"; in the rejection
# tests below we deliberately do not send it.
@pytest.mark.parametrize("path", PROTECTED)
def test_missing_key_is_rejected(client, auth_headers, fake_tasks, path):
    assert client.post(path).status_code == 401


@pytest.mark.parametrize("path", PROTECTED)
def test_wrong_key_is_rejected(client, auth_headers, fake_tasks, path):
    response = client.post(path, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


@pytest.mark.parametrize("path", PROTECTED)
@pytest.mark.parametrize("sent", ["testkey", ""])
def test_unconfigured_server_rejects_everything(
    client, monkeypatch, fake_tasks, path, sent
):
    monkeypatch.setattr(settings, "admin_api_key", "")
    response = client.post(path, headers={"X-API-Key": sent})
    assert response.status_code == 401


def test_non_ascii_key_is_a_401_not_a_500(client, auth_headers, fake_tasks):
    response = client.post(
        "/teams/sync", headers={"X-API-Key": "é".encode("utf-8")}
    )
    assert response.status_code == 401


def test_teams_sync_with_key(client, auth_headers, fake_tasks):
    response = client.post("/teams/sync", headers=auth_headers)
    assert response.status_code == 202


def test_fixtures_sync_with_key(client, auth_headers, fake_tasks):
    response = client.post("/fixtures/sync", headers=auth_headers)
    assert response.status_code == 202


def test_prediction_with_key(client, auth_headers, sample_fixture):
    response = client.post(f"/predictions/{sample_fixture.id}", headers=auth_headers)
    assert response.status_code == 201


@pytest.mark.parametrize("path", ["/teams/", "/fixtures/", "/predictions/"])
def test_read_routes_stay_public(client, auth_headers, path):
    assert client.get(path).status_code == 200