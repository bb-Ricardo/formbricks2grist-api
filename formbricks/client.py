import requests
from app.settings import FormbricksConfig
from app.models import InternalWebhookContent, InternalWebhookField
from formbricks.models import FormbricksWebhook
from app.lib import grab, strip_tags


class FormbricksClient:
    """
    Minimal Python client for the Formbricks Management API.
    Works with Formbricks Cloud or self-hosted installations.
    """

    def __init__(self, settings: FormbricksConfig):
        self.api_key = settings.api_key.get_secret_value()
        self.base_url = f"https://{settings.host_name}"
        self.timeout = settings.timeout_seconds
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        if self.get_health().get("status") != "ok":
            raise ValueError("Formbricks is unhealthy")

        self.check_me()

    # ---------------------------
    # Internal helpers
    # ---------------------------
    def _get(self, path: str):
        url = f"{self.base_url}{path}"
        res = requests.get(url, headers=self.headers, timeout=self.timeout)
        res.raise_for_status()
        return res.json()

    # ---------------------------
    # Surveys
    # ---------------------------
    def list_surveys(self):
        return self._get("/api/v1/management/surveys")

    def get_survey(self, survey_id: str):
        return self._get(f"/api/v1/management/surveys/{survey_id}")

    def get_health(self):
        return self._get("/health")

    def check_me(self):
        url = f"{self.base_url}/api/v1/management/me"
        res = requests.get(url, headers=self.headers, timeout=self.timeout)
        res.raise_for_status()
        if res.status_code != 200:
            raise ValueError(
                f"failed to connect to Formbricks: status {res.status_code}: error: {res.json().get('message')}")

    # ---------------------------
    # Responses
    # ---------------------------
    def list_responses(self, survey_id: str):
        return self._get(f"/api/v1/management/surveys/{survey_id}/responses")
