from typing import Dict, List

from pygrister.api import GristApi

from app.settings import GristConfig


class GristClient:

    def __init__(self, settings: GristConfig):
        self.settings = settings
        self.document_id = None
        self._client = GristApi(self.build_config())

        self.set_document_id()
        if self.document_id is None:
            raise ValueError(f"document '{self.settings.document_name}' not found for team '{self.settings.team_name}'")

    def build_config(self):

        return {
            "GRIST_API_KEY": self.settings.api_key.get_secret_value(),
            "GRIST_SELF_MANAGED": "Y",
            "GRIST_SELF_MANAGED_HOME": f"https://{self.settings.host_name}",
            "GRIST_SELF_MANAGED_SINGLE_ORG": "Y",
            "GRIST_TEAM_SITE": self.settings.team_name
        }

    def set_document_id(self):

        result, workspace_data = self._client.list_workspaces(self.settings.team_name)

        for workspace in workspace_data or list():
            for doc in workspace.get("docs", {}):
                if doc.get("name") == self.settings.document_name:
                    self.document_id = doc.get("urlId")
                    return

    def list_tables(self):
        return self._client.list_tables(self.document_id)

    def list_cols(self, table_id: str):
        return self._client.list_cols(table_id, doc_id=self.document_id)

    def list_records(self, table_id: str, filter_option: Dict):
        return self._client.list_records(table_id=table_id, filter=filter_option, doc_id=self.document_id)

    def add_table(self, data: Dict):
        return self._client.add_tables(tables=[data], doc_id=self.document_id)

    def add_cols(self, table_id: str, data: List[Dict]):
        return self._client.add_cols(table_id=table_id, cols=data, doc_id=self.document_id)

    def add_record(self, table_id: str, record: Dict):
        return self._client.add_records(table_id=table_id, records=[record], doc_id=self.document_id)
