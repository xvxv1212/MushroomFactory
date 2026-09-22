from sqlalchemy import BigInteger, CheckConstraint, UniqueConstraint
from sqlmodel import Column, Field, SQLModel


class Score(SQLModel, table=True):
    __tablename__ = "score"
    __table_args__ = (
        CheckConstraint(
            "category IN ('risk_awareness', 'refusal', 'help_request')",
            name="CHK_SCORE_CATEGORY",
        ),
        CheckConstraint(
            "score >= 0 AND score <= 3",
            name="CHK_SCORE_RANGE",
        ),
        UniqueConstraint("chat_id", "category", name="UK_SCORE_CHAT_CATEGORY"),
    )

    score_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    chat_id: int = Field(foreign_key="chatting.chat_id", nullable=False)
    category: str = Field(max_length=50, nullable=False)
    score: int = Field(nullable=False)