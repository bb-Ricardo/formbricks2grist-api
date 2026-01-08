from typing import Optional, Self

from pydantic import BaseModel, Field, SecretStr, model_validator


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
    confirmation_mail_recipient_template: Optional[str] = Field(
        default=None,
        description="The mail TO filed, supports column name substitution"
    )
    confirmation_mail_subject_template: Optional[str] = Field(
        default=None,
        description="Subject to use for confirmation mail, supports column name substitution"
    )
    confirmation_mail_content_template: Optional[str] = Field(
        default=None,
        description="Content of confirmation mail, supports column name substitution"
    )

    @model_validator(mode='after')
    def check_confirmation_mail_settings(self) -> Self:

        if self.enabled is False:
            return self

        for setting in [
            "sender_name",
            "sender_address",
            "confirmation_mail_recipient_template",
            "confirmation_mail_subject_template",
            "confirmation_mail_content_template"
        ]:
            if getattr(self, setting) is None or len(getattr(self, setting)) == 0:
                raise ValueError(f'setting "{setting}" must be defined')

        return self
