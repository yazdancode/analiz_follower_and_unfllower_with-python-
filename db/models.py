from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from utils.datetime_utils import now_iso

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=now_iso)
    updated_at: datetime = Field(default_factory=now_iso)

    def update_timestamp(self):
        self.updated_at = now_iso()

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: Optional[int] = Field(default=None, unique=True)
    username: Optional[str] = None
    created_at: datetime = Field(default_factory=now_iso)
    updated_at: datetime = Field(default_factory=now_iso)

    def __str__(self):
        return str(self.username)
