from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from database import Base, Session
import bcrypt


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
