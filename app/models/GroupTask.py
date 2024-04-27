from enum import Enum

from sqlalchemy import Column, Integer
from app.models.Task import find_task
from app.database import Base, Session


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
            return {"group_id": self.group_id, "task": find_task(self.task_id)}
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


def find_group_id(task_id):
    session = Session()
    group_task = session.query(GroupTask).filter(GroupTask.task_id == task_id).first()
    if group_task:
        return group_task.group_id
    return None