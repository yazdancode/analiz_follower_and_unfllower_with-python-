from sqlmodel import SQLModel, create_engine, Session
from .models import User

engine = create_engine("sqlite:///users.db")


def init_db():
    SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    return Session(engine)
