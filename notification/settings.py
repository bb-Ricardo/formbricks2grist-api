from typing import Optional, Annotated, List

from pydantic import BaseModel, Field, SecretStr, BeforeValidator

from grist.settings import string_to_list


class MailConfig(BaseModel):

    hostname: Optional[str] = Field(
        default=None,
        description="SMTP Server"
    )
    port: Optional[int] = Field(
        default=587,
        description="SMTP Port"
    )
    username: Optional[str] = Field(
        default=None,
        description="SMTP Username"
    )
    password: Optional[SecretStr] = Field(
        default=None,
        description="SMTP Passwort"
    )
    enabled: Optional[bool] = Field(
        default=False,
        description="defines if eMails will be sent"
    )
    sender_name: Optional[str] = Field(
        default=None,
        description="Mail from Name"
    )
    sender_address: Optional[str] = Field(
        default=None,
        description="Mail from email address"
    )
    confirmation_mail_columns: Annotated[List[str] | None, BeforeValidator(string_to_list)] = Field(
        default=[],
        description="comma separated list of colum to send in confirmation mail",
    )
