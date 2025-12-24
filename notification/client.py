import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.settings import get_settings
import logging
from typing import List

logger = logging.getLogger(__name__)


class MailHandler:

    def __init__(self):

        self.settings = get_settings().mail

        self.smtp_server = self.settings.hostname
        self.smtp_port = self.settings.port
        self.smtp_username = self.settings.username
        self.smtp_password = None
        if self.settings.password is not None:
            self.smtp_password = self.settings.password.get_secret_value()
        self.sender_mail = f"{self.settings.sender_name} <{self.settings.sender_address}>"
        self.default_subject = f"Eurohash registration"
        self.recipient_email = ""

    def send(self, recipients: List, subject=None, body: str = None) -> bool:

        if len(recipients) == 0:
            return False

        if subject is None:
            subject = self.default_subject

        if body is None:
            return False

        message = MIMEMultipart()
        message['From'] = self.sender_mail
        message['To'] = ", ".join(recipients)
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        try:
            logger.info("sending email")
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtp.starttls()  # Use for TLS encryption
            # smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)  # Use for SSL encryption
            if self.smtp_username is not None and self.smtp_password is not None:
                smtp.login(self.smtp_username, self.smtp_password)
            smtp.sendmail(self.sender_mail, recipients, message.as_string())
            smtp.quit()
            logger.info('email sent successfully')
            return True

        except Exception as e:
            logger.error(f'email sending failed: {str(e)}')
            return False
