"""Tests for backend/services/metrics.py -- the wrapper that actually respects
SENTRY_ENABLE_METRICS, since the installed sentry-sdk's own `enable_metrics` init() option is a
confirmed no-op (see backend/main.py's init_error_monitoring() docstring). Without this wrapper,
sentry_sdk.metrics.count() would always send once Sentry is initialized at all, regardless of
the setting -- the exact bug a live-verification pass against the real Sentry backend caught.
"""

from __future__ import annotations

from unittest.mock import Mock

from backend.config import settings
from backend.services import metrics


def test_noop_when_metrics_disabled(monkeypatch):
    monkeypatch.setattr(settings, "SENTRY_ENABLE_METRICS", False)
    fake_count = Mock()
    monkeypatch.setattr(metrics, "_sentry_metrics", Mock(count=fake_count))

    metrics.count("complaint.created", 1, attributes={"ward": "Ward 1"})

    fake_count.assert_not_called()


def test_forwards_to_sentry_sdk_when_metrics_enabled(monkeypatch):
    monkeypatch.setattr(settings, "SENTRY_ENABLE_METRICS", True)
    fake_count = Mock()
    monkeypatch.setattr(metrics, "_sentry_metrics", Mock(count=fake_count))

    metrics.count("complaint.created", 1, attributes={"ward": "Ward 1"})

    fake_count.assert_called_once_with("complaint.created", 1, attributes={"ward": "Ward 1"})
