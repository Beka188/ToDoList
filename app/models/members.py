from sqlalchemy import Column, Integer
from app.core.database import Base, Session, engine


class Member(Base):
    __tablename__ = "members"
    id = Column("id", Integer, primary_key=True)
    group_id = Column("group_id", Integer)
    member_id = Column("member_id", Integer)

    def __init__(self, group_id, member_id):
        self.group_id = group_id
        self.member_id = member_id


def add_member(group_id: int, member_id: int):
    new_member = Member(group_id, member_id)
    session = Session()
    session.add(new_member)
    session.commit()


def delete_member(group_id: int, member_id: int):
    session = Session()
    session.query(Member).filter(group_id == Member.group_id, member_id == Member.member_id).delete()
    session.commit()


def members(group_id: int):
    session = Session()
    all_members = session.query(Member).filter(Member.group_id == group_id).all()
    session.commit()
    return [member.member_id for member in all_members]


def drop_members_table():
    Base.metadata.tables['members'].drop(bind=engine, checkfirst=True)


def delete_members(member_id: int = None, group_id: int = None):
    session = Session()
    if member_id:
        session.query(Member).filter(Member.member_id == member_id).delete()
    elif group_id:
        session.query(Member).filter(Member.group_id == group_id).delete()
    session.commit()
