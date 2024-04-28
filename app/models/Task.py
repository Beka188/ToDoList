import _json
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, \
    Enum as EnumType
from sqlalchemy.orm import relationship
from enum import Enum
from app.database import Base, Session


class TaskStatus(str, Enum):
    DONE = "done"
    IN_PROGRESS = "in_progress"
    TO_DO = "to_do"
    MISSING = "missing"


class TaskCategory(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    EDUCATION = "education"
    SOCIAL = "social"
    GROUP = "group"
    OTHER = "other"


class Task(Base):
    __tablename__ = "tasks"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    title = Column("title", String)
    description = Column("description", String, default="")
    due_date = Column("due_date", Integer)
    status = Column("status", EnumType(TaskStatus), default=TaskStatus.TO_DO)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column("category", EnumType(TaskCategory), default=TaskCategory.OTHER)

    user = relationship("User", back_populates="tasks")

    def __init__(self, title, description, due_date, status, user_id, category):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.user_id = user_id
        self.category = category

    def __repr__(self):
        pass
        return {"id": self.id, "title": self.title, "description": self.description, "category": self.category,
                "due_date": datetime.fromtimestamp(self.due_date), "status": self.status, "user_id": self.user_id}

    def add(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
            return self.__repr__()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


def find_task(task_id: int):
    session = Session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        return task.__repr__()
    return None


def update(task_id, data: _json):
    session = Session()
    task = session.query(Task).filter(Task.id == task_id).first()
    try:
        print("Dannye: ")
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_user_task(task_id):
    session = Session()
    session.query(Task).filter(Task.id == task_id).delete()
    session.commit()
