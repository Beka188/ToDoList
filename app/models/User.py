import _json

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from app.core.database import Base, Session, engine
import bcrypt

from app.models.Task import Task
from app.models.Group import member_of_groups, all_groups


class User(Base):
    __tablename__ = "users"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String)
    email = Column("email", String, unique=True)
    is_email_verified = Column("is_email_verified", Boolean, default=False)
    password = Column("password", String)
    tasks = relationship("Task", back_populates="user")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def __repr__(self):
        return {"username": self.username,
                "email": self.email,
                "id": self.id,
                "is_email_verified": self.is_email_verified
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


def all_users():
    session = Session()
    users = session.query(User).all()
    return [user.__repr__() for user in users]


def find_user(email):
    session = Session()
    user = session.query(User).filter(User.email == email).first()
    return user


def find_user_id(user_id: int):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        return user.__repr__()
    return None


def update_user(email, data: _json):
    session = Session()
    task = session.query(User).filter(User.email == email).first()
    try:
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_user(email):
    session = Session()
    session.query(User).filter(User.email == email).delete()
    session.commit()


def drop_users_table():
    Base.metadata.tables['users'].drop(bind=engine, checkfirst=True)
