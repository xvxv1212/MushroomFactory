from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import BigInteger, CheckConstraint, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chat_room import ChatRoom


class LlmRole(SQLModel, table=True):
    __tablename__ = "llm_role"
    __table_args__ = (
        CheckConstraint(
            "category IN ('user_defined', 'school', 'trip', 'club')",
            name="CHK_LLM_ROLE_CATEGORY",
        ),
    )

    lr_num: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            primary_key=True,
            autoincrement=True,
        ),
    )
    title: str | None = Field(default=None, max_length=30)
    admin_id: str | None = Field(
        default=None, foreign_key="admin_table.admin_id", max_length=20
    )
    category: str | None = Field(default=None, max_length=50)
    content: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    admin: Optional["Admin"] = Relationship(
        back_populates="llm_roles"
    )
    chat_rooms: list["ChatRoom"] = Relationship(
        back_populates="llm_role"
    )

class WriteLlmRole(SQLModel):
    category: Literal["user_defined", "school", "trip", "club"] | None = Field(
        default=None, max_length=50
    )
    content: str | None = Field(default=None)