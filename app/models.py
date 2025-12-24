from __future__ import annotations

from typing import Any, Optional, List, Union

from pydantic import BaseModel

from formbricks.models import FormbricksWebhook


class QueueItem(BaseModel):
    """contains a queue item"""
    data: Any
    retries: Optional[int] = 0


class QueueItemWebhookIncoming(QueueItem):
    data: FormbricksWebhook
    pass


class QueueItemWebhookNormalized(QueueItem):
    data: InternalWebhookContent
    pass


class QueueItemWebhookStored(QueueItem):
    data: InternalWebhookContent
    pass


class InternalWebhookField(BaseModel):
    id: Optional[str] = ""
    value: Optional[Any] = ""
    label: Optional[str] = ""
    type: Optional[str] = ""


class InternalWebhookContent(BaseModel):
    webhook_id: Optional[str] = ""
    survey_id: Optional[str] = ""
    survey_name: Optional[str] = ""
    data: Optional[List[InternalWebhookField]] = list()

    def get_item_by_id(self, needle: str) -> Union[InternalWebhookField | None]:
        for item in self.data:
            if item.id == needle:
                return item

    def get_item_by_label(self, needle: str) -> Union[InternalWebhookField | None]:
        for item in self.data:
            if item.label == needle:
                return item
