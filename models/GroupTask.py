import _json
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Column, String, Integer, ForeignKey, \
    Enum as EnumType
from sqlalchemy.orm import relationship
from database import Base, Session


class TaskStatus(str, Enum):
    DONE = "done"
    IN_PROGRESS = "in_progress"
    TO_DO = "to_do"
    MISSING = "missing"


class GroupTask(Base):
    __tablename__ = "groupTasks"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    group_id = Column("group_id", Integer)
    task_id = Column("task_id", Integer)

    def __init__(self, group_id, task_id):
        self.group_id = group_id
        self.task_id = task_id

    def __repr__(self):
        return {"group_id": self.group_id, "task_id": self.task_id}

    def add(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
