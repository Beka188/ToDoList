from sqlalchemy import Column, String, Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from app.database import Base, Session
import bcrypt

from app.models.Task import Task
from app.models.Group import member_of_groups, all_groups


class User(Base):
    __tablename__ = "users"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String)
    email = Column("email", String, unique=True)
    password = Column("password", String)
    tasks = relationship("Task", back_populates="user")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def __repr__(self):
        return {"username": self.username,
                "email": self.email,
                "id": self.id
                }

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

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode('utf-8'))

    def all_tasks(self):
        session = Session()
        tasks = session.query(Task).filter(Task.user_id == self.id).all()
        return [task.__repr__() for
                task in tasks]

    def user_own_groups(self):
        return all_groups(self.id)

    def user_member_groups(self):
        return member_of_groups(self.id)


def login(email, password):
    user = find_user(email)
    if user is not None:
        if user.verify_password(password):
            return user
    return None


def find_user(email):
    session = Session()
    user = session.query(User).filter(User.email == email).first()
    return user