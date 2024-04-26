from sqlalchemy import Column, String, Integer, DateTime, Boolean, ARRAY, Table, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from database import Base, Session
from models.members import add_member
import bcrypt



class Group(Base):
    __tablename__ = "groups"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    description = Column("description", String, default="")
    creator_id = Column("creator_id", Integer)

    def __init__(self, creator_id, name, description: str = ""):
        self.creator_id = creator_id
        self.name = name
        self.description = description

    def __repr__(self):
        return {"name": self.name,
                "description": self.description,
                "creator_id": self.creator_id
                }


def create_new_group(creator_id: int, name: str, description: str = ""):
    try:
        new_group = Group(creator_id, name, description)
    except ValueError:
        return -1  # incorrect format
    session = Session()
    existed = session.query(Group).filter(creator_id == Group.creator_id, name == Group.name).first()
    if existed is not None:
        return 0  # group already exists
    session.add(new_group)
    session.commit()
    add_to_group(new_group.id, creator_id)
    return 1  # successful operation


def add_to_group(group_id: int, member_id: int):
    add_member(group_id, member_id)
