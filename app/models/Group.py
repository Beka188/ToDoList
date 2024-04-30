from sqlalchemy import Column, String, Integer
from app.database import Base, Session, engine
from app.models.members import add_member, members
from app.models.GroupTask import delete_group_task

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
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creator_id": self.creator_id,
            "members": all_members(self.id)
        }


def all_groups(user_id):
    session = Session()
    groups = session.query(Group).filter(Group.creator_id == user_id).all()
    return [group.__repr__() for
            group in groups]


def member_of_groups(user_id):
    session = Session()
    groups = session.query(Group).filter(Group.creator_id != user_id).all()
    answer = []
    for group in groups:
        print()
        members_ = all_members(group.id)
        for member_id in members_:
            if member_id == user_id:
                answer.append(group)
    return answer


def create_new_group(creator_id: int, name: str, description: str):
    new_group = Group(creator_id, name, description)
    session = Session()
    existed = session.query(Group).filter(creator_id == Group.creator_id, name == Group.name).first()
    if existed is not None:
        return None
    session.add(new_group)
    session.commit()
    return new_group.__repr__()


def find_group(group_id: int) -> Group:
    session = Session()
    group = session.query(Group).filter(Group.id == group_id).first()
    return group.__repr__()


def add_to_group(group_id: int, member_id: int):
    add_member(group_id, member_id)


def all_members(group_id):
    return members(group_id)


def drop_groups_table():
    Base.metadata.tables['groups'].drop(bind=engine, checkfirst=True)


def delete_group(group_id):
    session = Session()
    session.query(Group).filter(Group.id == group_id).delete()
    delete_group_task(group_id=group_id)
    session.commit()
