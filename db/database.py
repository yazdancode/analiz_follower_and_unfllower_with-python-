from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./database.db"  # مسیر دیتابیس شما
engine = create_engine(DATABASE_URL, echo=True)

# ساخت جدول‌ها خودکار هنگام اجرا
from db.models import User  # اطمینان از اینکه مدل‌ها لود شوند

SQLModel.metadata.create_all(engine)


def get_session():
    # بدون yield، چون می‌خوایم با 'with' استفاده کنیم
    return Session(engine)
