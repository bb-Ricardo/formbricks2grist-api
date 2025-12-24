from pydantic import BaseModel, Field, SecretStr


class FormbricksConfig(BaseModel):

    host_name: str = Field(
        default="",
        description="Formbricks host name"
    )
    api_key: SecretStr = Field(
        default="",
        description="Formbricks API Key"
    )
    webhook_api_token: SecretStr = Field(
        default="",
        description="defines a key which needs to passed as 'api_token' "
                    "url param in order to accept the webhook content"
    )
    timeout_seconds: int = Field(
        default=2,
        description="time out for formbricks requests",
        ge=1,
        le=300
    )
