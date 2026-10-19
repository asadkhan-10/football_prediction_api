from unittest.mock import MagicMock

from app import tasks
from app.tasks import heartbeat_task

URL = "https://hc-ping.com/test-uuid"


def test_heartbeat_skipped_without_url(monkeypatch):
    monkeypatch.setattr(tasks.settings, "healthcheck_url", "")
    mock_open = MagicMock()
    monkeypatch.setattr(tasks.urllib.request, "urlopen", mock_open)

    assert heartbeat_task() == "skipped"
    mock_open.assert_not_called()


def test_heartbeat_pings_url(monkeypatch):
    monkeypatch.setattr(tasks.settings, "healthcheck_url", URL)
    mock_open = MagicMock()
    monkeypatch.setattr(tasks.urllib.request, "urlopen", mock_open)

    assert heartbeat_task() == "ok"
    mock_open.assert_called_once_with(URL, timeout=10)


def test_heartbeat_survives_ping_failure(monkeypatch):
    monkeypatch.setattr(tasks.settings, "healthcheck_url", URL)
    mock_open = MagicMock(side_effect=OSError("network down"))
    monkeypatch.setattr(tasks.urllib.request, "urlopen", mock_open)

    assert heartbeat_task() == "failed"