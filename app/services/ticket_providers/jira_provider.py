"""Jira Cloud ticket provider (REST API v3)."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx

from app.services.ticket_providers.base import (
    CreatedTicket,
    TicketDetails,
    TicketProvider,
)
from app.utils.jira_adf import plain_text_to_adf

logger = logging.getLogger(__name__)

_FALLBACK_TYPES: tuple[str, ...] = (
    "task",
    "bug",
    "story",
    "incident",
    "request",
)


class JiraConfigurationError(Exception):
    """Jira env/config is missing or invalid."""


class JiraApiError(Exception):
    """Jira API returned an error."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class JiraProvider(TicketProvider):
    """Jira Cloud implementation of ``TicketProvider``."""

    def __init__(
        self,
        *,
        base_url: str,
        email: str,
        api_token: str,
        project_key: str,
        issue_type: str = "Bug",
        issue_type_id: str = "",
        timeout: float = 30.0,
    ) -> None:
        self._base = (base_url or "").strip().rstrip("/")
        self._email = (email or "").strip()
        self._token = (api_token or "").strip()
        self._project = (project_key or "").strip().upper()
        self._issue_type = (issue_type or "Bug").strip()
        self._issue_type_id = (issue_type_id or "").strip()
        self._timeout = timeout
        self._issuetype_field: dict[str, str] | None = None

    def _auth_header(self) -> dict[str, str]:
        raw = f"{self._email}:{self._token}".encode("utf-8")
        encoded = base64.b64encode(raw).decode("ascii")
        return {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
        }

    def _api_url(self, path: str) -> str:
        root = f"{self._base}/"
        return urljoin(root, path.lstrip("/"))

    @staticmethod
    def _parse_error_body(resp: httpx.Response) -> str:
        try:
            data = resp.json()
            msgs = list(data.get("errorMessages") or [])
            errs = data.get("errors") or {}
            msgs.extend(f"{k}: {v}" for k, v in errs.items())
            if msgs:
                return "; ".join(str(m) for m in msgs)
        except (ValueError, TypeError, AttributeError):
            pass
        return (resp.text or "")[:300]

    def validate_configuration(self) -> tuple[bool, str | None]:
        missing = []
        if not self._base:
            missing.append("JIRA_BASE_URL")
        if not self._email:
            missing.append("JIRA_EMAIL")
        if not self._token:
            missing.append("JIRA_API_TOKEN")
        if not self._project:
            missing.append("JIRA_PROJECT_KEY")
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        return True, None

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        files: list[tuple] | None = None,
        extra_headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        ok, err = self.validate_configuration()
        if not ok:
            raise JiraConfigurationError(err or "Jira not configured")

        headers = self._auth_header()
        if extra_headers:
            headers.update(extra_headers)
        if files:
            headers.pop("Accept", None)

        url = self._api_url(path)
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.request(
                    method,
                    url,
                    headers=headers,
                    json=json_body,
                    files=files,
                    params=params,
                )
        except httpx.TimeoutException as e:
            logger.error("jira_timeout | url=%s", url)
            raise JiraApiError("Jira request timed out") from e
        except httpx.RequestError as e:
            logger.error("jira_network | url=%s err=%s", url, e)
            raise JiraApiError("Jira is unavailable") from e

        if resp.status_code >= 400:
            detail = self._parse_error_body(resp)
            logger.warning(
                "jira_api_error | status=%s body=%s",
                resp.status_code,
                detail,
            )
            raise JiraApiError(
                detail or f"Jira API error ({resp.status_code})",
                status=resp.status_code,
            )
        return resp

    def _fetch_issue_types(self) -> list[dict[str, Any]]:
        """Load issue types allowed for this project (Cloud createmeta APIs)."""
        v2_path = f"/rest/api/3/issue/createmeta/{self._project}/issuetypes"
        try:
            resp = self._request("GET", v2_path)
            data = resp.json()
            items = data.get("issueTypes") or data.get("values") or []
            if isinstance(items, list) and items:
                return items
        except JiraApiError as e:
            logger.info("jira_createmeta_v2_unavailable | %s", e)

        resp = self._request(
            "GET",
            "/rest/api/3/issue/createmeta",
            params={
                "projectKeys": self._project,
                "expand": "projects.issuetypes",
            },
        )
        data = resp.json()
        for proj in data.get("projects") or []:
            if (proj.get("key") or "").upper() == self._project:
                types = proj.get("issuetypes") or []
                if isinstance(types, list):
                    return types
        return []

    def _resolve_issuetype_field(self) -> dict[str, str]:
        if self._issuetype_field is not None:
            return self._issuetype_field

        if self._issue_type_id:
            self._issuetype_field = {"id": self._issue_type_id}
            return self._issuetype_field

        types = self._fetch_issue_types()
        if not types:
            raise JiraApiError(
                f"No issue types found for project {self._project}. "
                "Set JIRA_ISSUE_TYPE_ID in .env.",
            )

        want = self._issue_type.lower()

        def _pick(match: dict[str, Any]) -> dict[str, str]:
            name = match.get("name") or self._issue_type
            field = {"id": str(match["id"])}
            logger.info(
                "jira_issuetype_resolved | project=%s type=%s id=%s",
                self._project,
                name,
                match.get("id"),
            )
            self._issuetype_field = field
            return field

        for t in types:
            if t.get("subtask"):
                continue
            if (t.get("name") or "").lower() == want:
                return _pick(t)

        for fb in _FALLBACK_TYPES:
            for t in types:
                if t.get("subtask"):
                    continue
                if (t.get("name") or "").lower() == fb:
                    logger.info(
                        "jira_issuetype_fallback | wanted=%s using=%s",
                        self._issue_type,
                        t.get("name"),
                    )
                    return _pick(t)

        for t in types:
            if not t.get("subtask"):
                logger.info(
                    "jira_issuetype_default | wanted=%s using=%s",
                    self._issue_type,
                    t.get("name"),
                )
                return _pick(t)

        raise JiraApiError(
            f"No creatable issue type for project {self._project}.",
        )

    def create_ticket(
        self,
        *,
        title: str,
        description: str,
        expected_vs_actual: str,
    ) -> CreatedTicket:
        full_desc = (
            f"{description.strip()}\n\n"
            "---\n"
            "**Expected vs actual:**\n"
            f"{expected_vs_actual.strip()}"
        )
        issuetype = self._resolve_issuetype_field()
        payload: dict[str, Any] = {
            "fields": {
                "project": {"key": self._project},
                "summary": title.strip()[:255],
                "description": plain_text_to_adf(full_desc),
                "issuetype": issuetype,
            },
        }
        logger.info(
            "jira_create_issue | project=%s issuetype=%s summary_len=%s",
            self._project,
            issuetype,
            len(title),
        )
        resp = self._request("POST", "/rest/api/3/issue", json_body=payload)
        data = resp.json()
        key = str(data.get("key") or "")
        if not key:
            raise JiraApiError("Jira did not return issue key")
        ticket_url = f"{self._base}/browse/{key}"
        logger.info("jira_create_issue_ok | key=%s", key)
        return CreatedTicket(ticket_id=key, ticket_url=ticket_url, raw=data)

    def upload_attachment(
        self,
        ticket_id: str,
        file_path: Path,
        file_name: str,
    ) -> str:
        if not file_path.is_file():
            raise JiraApiError(f"Attachment file not found: {file_path}")

        path = f"/rest/api/3/issue/{ticket_id}/attachments"
        headers = {
            "X-Atlassian-Token": "no-check",
        }
        content = file_path.read_bytes()
        files = [("file", (file_name, content))]
        logger.info(
            "jira_upload_attachment | key=%s file=%s bytes=%s",
            ticket_id,
            file_name,
            len(content),
        )
        resp = self._request(
            "POST",
            path,
            files=files,
            extra_headers=headers,
        )
        items = resp.json()
        if isinstance(items, list) and items:
            att_id = str(items[0].get("id") or file_name)
            return att_id
        return file_name

    def get_ticket(self, ticket_id: str) -> TicketDetails:
        key = (ticket_id or "").strip()
        resp = self._request("GET", f"/rest/api/3/issue/{key}")
        data = resp.json()
        fields = data.get("fields") or {}
        status = None
        st = fields.get("status")
        if isinstance(st, dict):
            status = st.get("name")
        ticket_url = f"{self._base}/browse/{key}"
        return TicketDetails(
            ticket_id=key,
            ticket_url=ticket_url,
            status=status,
            raw=data,
        )
