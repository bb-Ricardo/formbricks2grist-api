import logging

from app.models import InternalWebhookContent
from app.settings import get_settings
from notification.client import MailHandler

logger = logging.getLogger(__name__)


def resolve_template(data: str, record_data: InternalWebhookContent) -> str:

    for item in record_data.data:
        data = data.replace("{{"+item.label+"}}", item.value_as_str())

    return data


def send_email_for_record(record_data: InternalWebhookContent):

    settings = get_settings().mail

    if settings.enabled is False:
        logger.info(f"sending of confirmation mail is disabled (id {record_data.webhook_id})")
        return

    recipient = resolve_template(settings.confirmation_mail_recipient_template, record_data)
    subject = resolve_template(settings.confirmation_mail_subject_template, record_data)
    body = resolve_template(settings.confirmation_mail_content_template, record_data)

    logger.info(f"sending confirmation mail to '{recipient}'")

    MailHandler().send([recipient], subject=subject, body=body)
