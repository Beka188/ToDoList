from fastapi import requests
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func, desc, Boolean, ForeignKey, \
    Enum as EnumType
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from database import Base, Session


class TaskStatus(str, Enum):
    DONE = "done"
    IN_PROGRESS = "in_progress"
    TO_DO = "to_do"
    MISSING = "missing"


class Task(Base):
    __tablename__ = "tasks"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    title = Column("title", String)
    description = Column("description", String)
    due_date = Column("due_date", DateTime)
    status = Column("status", EnumType(TaskStatus), default=TaskStatus.TO_DO)
    user_id = Column(Integer, ForeignKey("users_id"))
    user = relationship("users", back_populates="tasks")
    category_id = Column(Integer, ForeignKey("category_id"))
    category = relationship("categories", back_populates="tasks")

    def __init__(self, title, description, due_date, status, user_id, category_id):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.user_id = user_id
        self.category_id = category_id

    def __repr__(self):
        return f'title: {self.title}\nDescription: {self.description}\nCompleted: {self.status}\n{self.due_date}\nuser_id: {self.user_id},  category_id: {self.category_id}'

    def add(self):
        session = Session()
        session.add(self)
        session.commit()
