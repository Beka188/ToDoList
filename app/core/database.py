from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "../../to_do_list.db")

engine = create_engine(f"sqlite:///{db_path}", echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)

