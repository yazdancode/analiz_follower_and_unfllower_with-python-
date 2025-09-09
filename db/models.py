from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


def now_iso():
    return datetime.utcnow()


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: Optional[int] = Field(default=None, unique=True, index=True)
    username: Optional[str] = None
    created_at: datetime = Field(default_factory=now_iso)
    updated_at: datetime = Field(default_factory=now_iso)

    def update_timestamp(self):
        self.updated_at = now_iso()


class User(BaseModel, table=True):
    username_instagram: str | None = Field(default_factory=lambda: "temp_user")
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = True
    stage: str = "start"


class Follower(BaseModel, table=True):
    pk: Optional[int] = None
    full_name: Optional[str] = None
    is_private: Optional[bool] = False
    profile_pic_url: Optional[str] = None


class FollowingUser(BaseModel, table=True):
    pk: Optional[int] = None
    full_name: Optional[str] = None
    is_private: Optional[bool] = False
    profile_pic_url: Optional[str] = None
