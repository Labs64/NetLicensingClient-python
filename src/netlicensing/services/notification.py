"""Notification service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import Notification
from netlicensing.services.base import ResourceService


class NotificationService(ResourceService[Notification]):
    """CRUD operations for notifications."""

    endpoint = "notification"
    item_type = "Notification"
    model = Notification

    def create(self, notification: Notification | dict[str, Any] | None = None, **properties: Any) -> Notification:
        return self._create_resource(notification, **properties)

    def update(
        self,
        number: str,
        notification: Notification | dict[str, Any] | None = None,
        **properties: Any,
    ) -> Notification:
        return self._update_resource(number, notification, **properties)

    def delete(self, number: str, *, force_cascade: bool = False) -> bool:
        self.client._request("DELETE", f"{self.endpoint}/{number}", expected_status={200, 202, 204})
        return True
