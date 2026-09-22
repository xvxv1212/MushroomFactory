from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom


class ChatterEnum(str, PyEnum):
    AI = "AI"
    USER = "USER"


class Chatting(SQLModel, table=True):
    __tablename__ = "chatting"

    chat_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    room_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey(
                "chat_room.room_id",
                ondelete="RESTRICT",
                onupdate="RESTRICT",
            ),
            nullable=False,
        )
    )
    chatter: ChatterEnum = Field(
        sa_column=Column(
            Enum(ChatterEnum, name="chatter_enum", native_enum=True),
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    room: "ChatRoom" = Relationship(back_populates="chatting")