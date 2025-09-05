from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


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
    username_instagram: str | None = Field(default_factory=lambda: "temp_user")
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    stage: str = "start"
