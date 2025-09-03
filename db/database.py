import os

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
engine = create_engine(DATABASE_URL, echo=True)


# ساخت جدول‌ها خودکار هنگام اجرا - بعد از import مدل‌ها
def create_db_and_tables():
    """ایجاد تمام جداول دیتابیس"""
    SQLModel.metadata.create_all(engine)


# فراخوانی برای ایجاد جداول هنگام import
create_db_and_tables()


def get_session():
    """یک session جدید برای دیتابیس برمی‌گرداند"""
    return Session(engine)
