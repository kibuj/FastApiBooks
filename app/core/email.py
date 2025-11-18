from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List

conf = ConnectionConfig(
    MAIL_USERNAME="",
    MAIL_PASSWORD="",
    MAIL_FROM="noreply@bookapi.com",
    MAIL_PORT=1025,
    MAIL_SERVER="localhost",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
    VALIDATE_CERTS=False
)


# app/core/email.py

async def send_notification_email(
        email_to: List[EmailStr],
        subject: str,
        body: str
):

    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    await fm.send_message(message)

