"""Abstract ticket provider for Jira and future integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CreatedTicket:
    ticket_id: str
    ticket_url: str
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class TicketDetails:
    ticket_id: str
    ticket_url: str
    status: str | None = None
    raw: dict[str, Any] | None = None


class TicketProvider(ABC):
    """Provider contract; chatbot logic depends only on this interface."""

    @abstractmethod
    def validate_configuration(self) -> tuple[bool, str | None]:
        """Return (ok, error_message)."""

    @abstractmethod
    def create_ticket(
        self,
        *,
        title: str,
        description: str,
        expected_vs_actual: str,
    ) -> CreatedTicket:
        """Create a ticket in the external system."""

    @abstractmethod
    def upload_attachment(
        self,
        ticket_id: str,
        file_path: Path,
        file_name: str,
    ) -> str:
        """Attach a file to an existing ticket; return attachment id or name."""

    @abstractmethod
    def get_ticket(self, ticket_id: str) -> TicketDetails:
        """Fetch ticket metadata by key or id."""
