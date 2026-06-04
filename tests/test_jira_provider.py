"""Unit tests for Jira provider configuration validation."""

from __future__ import annotations

from app.services.ticket_providers.jira_provider import JiraProvider


def test_validate_configuration_missing_env():
    provider = JiraProvider(
        base_url="",
        email="",
        api_token="",
        project_key="",
    )
    ok, err = provider.validate_configuration()
    assert not ok
    assert err is not None
    assert "JIRA_BASE_URL" in err


def test_validate_configuration_ok():
    provider = JiraProvider(
        base_url="https://example.atlassian.net",
        email="user@example.com",
        api_token="token",
        project_key="ABC",
    )
    ok, err = provider.validate_configuration()
    assert ok
    assert err is None
