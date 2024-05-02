from sqlalchemy import Column, String, Integer
from sqlalchemy.exc import IntegrityError

from app.core.database import Base, Session
import re


class Email(Base):
    __tablename__ = "emails"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    email = Column("email", String, unique=True)
    verification_token = Column("verification_token", String, unique=True)

    def __init__(self, email, verification_token):
        self.email = email
        self.verification_token = verification_token

    def add(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
            return self.__repr__()
        except IntegrityError:
            session.rollback()
            raise ValueError("The email already in use!")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


def find_user_by_token(token):
    session = Session()
    user = session.query(Email).filter(Email.verification_token == token).first()
    if user:
        return user.email
    return None


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def is_valid_email(email):
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def delete_verification_token(email):
    session = Session()
    session.query(Email).filter(Email.email == email).delete()
    session.commit()
