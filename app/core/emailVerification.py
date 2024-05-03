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
    MAIL_FROM="bekarys.shaimardan@nu.edu.kz",
    MAIL_PORT=587,
    MAIL_SERVER=str(os.getenv("MAIL_SERVER")),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == 'True',
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == 'True',
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS") == 'True',
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS") == 'True'
)

