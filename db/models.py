from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


def now_iso():
    return datetime.utcnow()


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=now_iso)
    updated_at: datetime = Field(default_factory=now_iso)

    def update_timestamp(self):
        self.updated_at = now_iso()


class User(BaseModel, table=True):
    chat_id: Optional[int] = Field(default=None, unique=True, index=True)
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    stage: str = "start"
