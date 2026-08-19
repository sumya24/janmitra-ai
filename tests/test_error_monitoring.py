"""Tests for backend/main.py's init_error_monitoring(): the Sentry wiring must be a true no-op
when SENTRY_DSN is unset (the default), must pass the right config through when it is set, and
must never raise out of the app's own startup even if Sentry itself fails to initialize -- an
optional alerting tool must not become a new way for the app to go down.
"""

from __future__ import annotations

from unittest.mock import Mock

from backend.config import settings
from backend.main import init_error_monitoring


def test_noop_when_dsn_unset(monkeypatch):
    monkeypatch.setattr(settings, "SENTRY_DSN", "")
    import sentry_sdk

    fake_init = Mock()
    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    init_error_monitoring()

    fake_init.assert_not_called()


def test_initializes_sentry_when_dsn_set(monkeypatch):
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://fake@example.ingest.sentry.io/1")
    monkeypatch.setattr(settings, "SENTRY_ENVIRONMENT", "test")
    monkeypatch.setattr(settings, "SENTRY_TRACES_SAMPLE_RATE", 0.25)
    import sentry_sdk

    fake_init = Mock()
    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    init_error_monitoring()

    fake_init.assert_called_once()
    _, kwargs = fake_init.call_args
    assert kwargs["dsn"] == "https://fake@example.ingest.sentry.io/1"
    assert kwargs["environment"] == "test"
    assert kwargs["traces_sample_rate"] == 0.25
    assert kwargs["send_default_pii"] is False


def test_never_raises_if_sentry_init_fails(monkeypatch):
    """A bad DSN, a network hiccup, a future SDK incompatibility -- none of these should ever be
    able to block the app from starting."""
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://fake@example.ingest.sentry.io/1")
    import sentry_sdk

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated Sentry init failure")

    monkeypatch.setattr(sentry_sdk, "init", _boom)

    init_error_monitoring()  # must not raise
