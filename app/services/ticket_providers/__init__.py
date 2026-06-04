"""Ticket provider implementations (Jira, future GitHub, etc.)."""

from app.services.ticket_providers.base import TicketProvider
from app.services.ticket_providers.jira_provider import JiraProvider

__all__ = ["TicketProvider", "JiraProvider"]
