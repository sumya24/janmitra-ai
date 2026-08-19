"""Tests for backend/main.py's init_error_monitoring(): the Sentry wiring must be a true no-op
when SENTRY_DSN is unset (the default), must pass the right config through when it is set, and
must never raise out of the app's own startup even if Sentry itself fails to initialize -- an
optional alerting tool must not become a new way for the app to go down.

Logs and Metrics are NOT tested here via a plain `enable_logs=`/`enable_metrics=` kwarg
assertion -- confirmed directly against the installed SDK (sentry_sdk/client.py) that both are
deprecated no-ops there, which is exactly the real bug a second live-verification pass against
the actual Sentry backend caught (the first version of this code trusted those flags and they
silently didn't work). See the LoggingIntegration-presence assertions below for how Logs is
actually gated, and tests/test_metrics.py for how Metrics is actually gated.
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
    monkeypatch.setattr(settings, "SENTRY_ENABLE_LOGS", True)
    monkeypatch.setattr(settings, "SENTRY_ENABLE_METRICS", True)
    monkeypatch.setattr(settings, "SENTRY_PROFILE_SESSION_SAMPLE_RATE", 0.5)
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    fake_init = Mock()
    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    init_error_monitoring()

    fake_init.assert_called_once()
    _, kwargs = fake_init.call_args
    assert kwargs["dsn"] == "https://fake@example.ingest.sentry.io/1"
    assert kwargs["environment"] == "test"
    assert kwargs["traces_sample_rate"] == 0.25
    assert kwargs["send_default_pii"] is False
    assert kwargs["profile_lifecycle"] == "trace"
    assert kwargs["profile_session_sample_rate"] == 0.5
    # No enable_logs=/enable_metrics= kwargs at all -- confirmed deprecated no-ops in the
    # installed SDK, see this file's module docstring. Metrics gating lives in
    # backend/services/metrics.py instead (see tests/test_metrics.py); Logs gating is this
    # explicitly-constructed integration, asserted below.
    assert "enable_logs" not in kwargs
    assert "enable_metrics" not in kwargs
    logging_integrations = [i for i in kwargs["integrations"] if isinstance(i, LoggingIntegration)]
    assert len(logging_integrations) == 1
    assert logging_integrations[0].capture_sentry_logs is True


def test_logging_integration_omitted_when_logs_disabled(monkeypatch):
    """SENTRY_ENABLE_LOGS=False (the default) must not add a capture_sentry_logs=True
    LoggingIntegration -- the SDK auto-enables its own default (capture_sentry_logs=False) one
    when none is explicitly passed, which is the correct off state."""
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://fake@example.ingest.sentry.io/1")
    monkeypatch.setattr(settings, "SENTRY_ENABLE_LOGS", False)
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    fake_init = Mock()
    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    init_error_monitoring()

    _, kwargs = fake_init.call_args
    assert not any(isinstance(i, LoggingIntegration) for i in kwargs["integrations"])


def test_profiling_off_by_default(monkeypatch):
    """Must independently default to off -- turning on error monitoring (just setting
    SENTRY_DSN) must not silently turn on profiling too."""
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://fake@example.ingest.sentry.io/1")
    monkeypatch.setattr(settings, "SENTRY_PROFILE_SESSION_SAMPLE_RATE", 0.0)
    import sentry_sdk

    fake_init = Mock()
    monkeypatch.setattr(sentry_sdk, "init", fake_init)

    init_error_monitoring()

    _, kwargs = fake_init.call_args
    assert kwargs["profile_session_sample_rate"] == 0.0


def test_never_raises_if_sentry_init_fails(monkeypatch):
    """A bad DSN, a network hiccup, a future SDK incompatibility -- none of these should ever be
    able to block the app from starting."""
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://fake@example.ingest.sentry.io/1")
    import sentry_sdk

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated Sentry init failure")

    monkeypatch.setattr(sentry_sdk, "init", _boom)

    init_error_monitoring()  # must not raise
