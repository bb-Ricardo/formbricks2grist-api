from typing import Optional, Annotated, List, Self

from pydantic import BaseModel, Field, SecretStr, BeforeValidator, model_validator

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
    confirmation_mail_recipient_column_name: Optional[str] = Field(
        default=None,
        description="The table column name which contains the recipients eMail address"
    )
    confirmation_mail_subject: Optional[str] = Field(
        default=None,
        description="Subject to use for confirmation mail"
    )
    confirmation_mail_columns: Annotated[List[str] | None, BeforeValidator(string_to_list)] = Field(
        default=[],
        description="Comma separated list of colum to send in confirmation mail",
    )
    confirmation_mail_content: Optional[str] = Field(
        default=None,
        description="Content of confirmation mail"
    )

    @model_validator(mode='after')
    def check_confirmation_mail_settings(self) -> Self:

        if self.enabled is False:
            return self

        for setting in [
            "confirmation_mail_content",
            "confirmation_mail_subject",
            "confirmation_mail_recipient_column_name",
            "confirmation_mail_columns"
        ]:
            if getattr(self, setting) is None or len(getattr(self, setting)) == 0:
                raise ValueError(f'setting "{setting}" must be defined')

        return self

