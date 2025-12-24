from pydantic import BaseModel
from typing import Any, Dict, Optional


class FormbricksWebhookData(BaseModel):
    id: str
    surveyId: str
    finished: bool
    data: Dict[str, Any]
    meta: Dict[str, Any]


class FormbricksWebhook(BaseModel):
    webhookId: Optional[str] = ""
    event: Optional[str] = ""
    data: Optional[FormbricksWebhookData] = None
