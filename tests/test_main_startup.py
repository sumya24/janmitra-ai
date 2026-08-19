"""Tests for backend/main.py's _check_production_secrets() -- the startup safeguard that refuses
to run with ENVIRONMENT=production and a blank JWT_SECRET_KEY, rather than the previous silent
fallback to a random per-process secret (see backend/services/auth_service.py's own comment on
that fallback). Tested directly against the extracted function, not by actually booting the full
app -- see that function's own docstring for why it was factored out this way.
"""

from __future__ import annotations

import pytest

from backend.config import settings
from backend.main import _check_production_secrets


def test_refuses_to_start_in_production_with_no_jwt_secret(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "")
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        _check_production_secrets()


def test_allows_start_in_production_with_a_real_jwt_secret(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "a-real-secret-value")
    _check_production_secrets()  # must not raise


def test_allows_start_in_development_with_no_jwt_secret(monkeypatch):
    """Local dev's whole point is running with zero required config -- this check must never
    block it, matching auth_service.py's existing "warn, don't require" behavior there."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "")
    _check_production_secrets()  # must not raise


def test_allows_start_with_environment_unset_and_no_jwt_secret(monkeypatch):
    """The default value of ENVIRONMENT itself ("development") must be exactly as permissive as
    explicitly setting it -- an operator who never heard of this new setting at all must not be
    newly blocked by it."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "")
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "")
    _check_production_secrets()  # must not raise
