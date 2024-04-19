from fastapi import requests
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func, desc, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database import Base, Session


class Task(Base):
    __tablename__ = "tasks"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    title = Column("title", String)
    description = Column("description", String)
    due_date = Column("due_date", DateTime)
    status = Column("status", Boolean)
    user_id = Column("user_id", Integer)
    category_id = Column("category_id", Integer)

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
