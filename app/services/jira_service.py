"""Jira service facade with dependency-injected provider."""

from __future__ import annotations

import logging
from pathlib import Path

from app.config.settings import get_settings
from app.services.ticket_providers.base import (
    CreatedTicket,
    TicketDetails,
    TicketProvider,
)
from app.services.ticket_providers.jira_provider import (
    JiraApiError,
    JiraConfigurationError,
    JiraProvider,
)

logger = logging.getLogger(__name__)


def _first(*values: str) -> str:
    for v in values:
        t = (v or "").strip()
        if t:
            return t
    return ""


def get_jira_provider() -> JiraProvider:
    """Build provider from ``.env`` / env vars (via Settings) + ``config.yaml``."""
    s = get_settings()
    j = s.jira
    token = ""
    if s.jira_api_token is not None:
        token = (s.jira_api_token.get_secret_value() or "").strip()
    return JiraProvider(
        base_url=_first(s.jira_base_url, j.base_url),
        email=_first(s.jira_email, j.email),
        api_token=token,
        project_key=_first(s.jira_project_key, j.project_key),
        issue_type=_first(s.jira_issue_type, j.issue_type, "Bug"),
        issue_type_id=_first(s.jira_issue_type_id),
    )


class JiraService:
    """Thin service layer over ``TicketProvider`` for routes and workflow."""

    def __init__(self, provider: TicketProvider | None = None) -> None:
        self._provider = provider or get_jira_provider()

    def validate_configuration(self) -> tuple[bool, str | None]:
        return self._provider.validate_configuration()

    def create_issue(
        self,
        *,
        title: str,
        description: str,
        expected_vs_actual: str,
        attachment_paths: list[tuple[Path, str]],
    ) -> CreatedTicket:
        """
        Create issue then upload each attachment (best-effort per file).
        """
        ok, err = self.validate_configuration()
        if not ok:
            logger.error("jira_config_invalid | %s", err)
            raise JiraConfigurationError(err or "Jira not configured")

        try:
            created = self._provider.create_ticket(
                title=title,
                description=description,
                expected_vs_actual=expected_vs_actual,
            )
        except JiraApiError:
            raise
        except Exception as e:
            logger.exception("jira_create_failed")
            raise JiraApiError("Failed to create Jira ticket") from e

        for path, name in attachment_paths:
            try:
                self._provider.upload_attachment(
                    created.ticket_id,
                    path,
                    name,
                )
            except JiraApiError as e:
                logger.warning(
                    "jira_attachment_failed | key=%s file=%s err=%s",
                    created.ticket_id,
                    name,
                    e,
                )
        return created

    def upload_attachment(
        self,
        ticket_id: str,
        file_path: Path,
        file_name: str,
    ) -> str:
        return self._provider.upload_attachment(
            ticket_id,
            file_path,
            file_name,
        )

    def get_issue(self, ticket_id: str) -> TicketDetails:
        return self._provider.get_ticket(ticket_id)


def clear_jira_provider_cache_for_tests() -> None:
    """No-op; kept for tests that called the old lru_cache clear."""
