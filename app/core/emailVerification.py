import os

from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME=str(os.getenv("MAIL_USERNAME")),
    MAIL_PASSWORD=str(os.getenv("MAIL_PASSWORD")),
    MAIL_FROM=str(os.getenv("MAIL_FROM")),
    MAIL_PORT=(os.getenv("MAIL_PORT")),
    MAIL_SERVER=str(os.getenv("MAIL_SERVER")),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=bool(os.getenv("MAIL_STARTTLS")),
    MAIL_SSL_TLS=bool(os.getenv("MAIL_SSL_TLS")),
    USE_CREDENTIALS=bool(os.getenv("USE_CREDENTIALS")),
    VALIDATE_CERTS=bool(os.getenv("VALIDATE_CERTS"))
)
