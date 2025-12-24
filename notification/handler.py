import datetime
import logging

from app.models import InternalWebhookContent
from app.settings import get_settings
from notification.client import MailHandler

logger = logging.getLogger(__name__)


def send_email_for_record(record_data: InternalWebhookContent):

    settings = get_settings().mail

    if settings.enabled is False:
        logger.info(f"sending of confirmation mail is disabled (id {record_data.webhook_id})")
        return

    email_column_name = settings.confirmation_mail_recipient_column_name

    mail_recipient = record_data.get_item_by_label(email_column_name)
    if mail_recipient is None:
        logger.warning(f"unable to find mail address in column '{email_column_name}'")
        return

    registration_details = list()
    for item in record_data.data:
        if item.label in settings.confirmation_mail_columns:
            if item.type == "Date":
                value = datetime.datetime.fromtimestamp(item.value).strftime("%d/%m/%Y")
            else:
                value = item.value

            registration_details.append(f"   {item.label}: {value}")

    body = settings.confirmation_mail_content.format(registration_details='\n'.join(registration_details))

    MailHandler().send([mail_recipient.value], subject=settings.confirmation_mail_subject, body=body)
