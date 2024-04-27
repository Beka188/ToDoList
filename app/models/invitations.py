from sqlalchemy import Column, Integer, String
from app.database import Base, Session
import uuid


class Invitation(Base):
    __tablename__ = "invitations"
    id = Column("id", Integer, primary_key=True)
    sender_id = Column("sender_id", Integer)
    group_id = Column("group_id", Integer)
    token = Column("token", String)
    status = Column("status", String)

    def __init__(self, sender_id, group_id, token, status: str = "pending"):
        self.sender_id = sender_id
        self.group_id = group_id
        self.token = token
        self.status = status

    def add(self):
        session = Session()
        session.add(self)
        session.commit()


def generate_unique_token():
    return str(uuid.uuid4())


def is_invitation(token: str):
    session = Session()
    return session.query(Invitation).filter(Invitation.token == token).first()
