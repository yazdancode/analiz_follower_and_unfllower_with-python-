from typing import Optional

from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    __tablename__ = "base"
    id: Optional[int] = Field(default=None, primary_key=True)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class User(BaseModel, table=True):
    __tablename__ = "users"
    username: str = Field(max_length=50)
    password: str = Field(max_length=50)
    email: str = Field(max_length=50)
    phone: str = Field(max_length=50)
    chat_id: int = Field(default=None, primary_key=True)

    def __str__(self):
        return str(self.username)

    def __repr__(self):
        return f"<{self.__class__.__name__}(username={self.username})>"
