
import datetime
import logging

from app.models import InternalWebhookContent
from app.settings import get_settings
from notification.client import MailHandler

logger = logging.getLogger(__name__)

regIDColumnName = "Registration ID"


def send_email_for_record(record_data: InternalWebhookContent):

    settings = get_settings()

    email_column_name = settings.grist.mail_recipient_column_name

    if email_column_name is None:
        logger.warning("Grist MAIL_RECIPIENT_COLUMN_NAME is undefined")
        return

    mail_recipient = record_data.get_item_by_label(email_column_name)
    if mail_recipient is None:
        logger.warning(f"unable to find mail address in column '{email_column_name}'")
        return

    registration_id = record_data.get_item_by_label(regIDColumnName)

    subject = f"Eurohash 2027 Registration ID - {registration_id.value}"

    body = list()
    body.append("Welcome to Eurohash 2027")
    body.append("")
    body.append("here are your registration details")
    for item in record_data.data:

        if item.label not in settings.mail.confirmation_mail_columns:
            continue

        if item.type == "Date":
            value = datetime.datetime.fromtimestamp(item.value).strftime("%d/%m/%Y")
        else:
            value = item.value
        body.append(f"   {item.label}: {value}")
    body.append("")
    body.append("Thank you for joining Eurohash 2027")
    body.append("")
    body.append("OnOn")
    body.append("Mismanagement")

    mail = MailHandler()

    mail.send([mail_recipient.value], subject=subject, body='\n'.join(body))
