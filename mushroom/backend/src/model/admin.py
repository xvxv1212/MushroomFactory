from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom
    from model.llm_role import LlmRole


class Admin(SQLModel, table=True):
    __tablename__ = "admin_table"

    admin_id: str = Field(primary_key=True, max_length=20)
    admin_pw: str = Field(max_length=255)
    teacher_num: int
    enabled: bool = Field(default=True)
    admin_name: str = Field(max_length=100)
    contact: str = Field(max_length=14)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    llm_roles: list["LlmRole"] = Relationship(back_populates="admin")
    chat_rooms: list["ChatRoom"] = Relationship(
        back_populates="admin"
    )


class AdminSignIn(SQLModel):
    admin_id: str
    admin_pw: str


class AdminSignUp(SQLModel):
    admin_id: str = Field(max_length=20)
    admin_pw: str = Field(max_length=255)
    teacher_num: int
    admin_name: str = Field(max_length=100)
    contact: str = Field(max_length=14)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str