from pydantic import BaseModel, Field, SecretStr, BeforeValidator
from typing import Optional, List, Annotated


def string_to_list(value: str) -> List[str]:
    if not isinstance(value, str):
        return []

    return [item.strip() for item in value.split(",") if len(item) > 0]


class GristConfig(BaseModel):

    host_name: str = Field(
        default="",
        description="Grist host name"
    )
    api_key: SecretStr = Field(
        default="",
        description="Grist API Key"
    )
    team_name: str = Field(
        default="",
        description="Grist team name"
    )
    document_name: str = Field(
        default="",
        description="Grist document to add registrations"
    )
    table_name: str = Field(
        default="",
        description="Grist document table name to use"
    )
    mail_recipient_column_name: Optional[str] = Field(
        default=None,
        description="The Table column name which contains the recipients eMail address"
    )
    public_list_columns: Annotated[List[str] | None, BeforeValidator(string_to_list)] = Field(
        default=[],
        description="comma separated list of colum to list public",
    )
