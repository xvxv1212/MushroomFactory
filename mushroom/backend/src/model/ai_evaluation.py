from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlmodel import Field, SQLModel


class AiEvaluation(SQLModel, table=True):
    """학생의 Stage 응답에 대해 실제 LLM이 산출한 평가 점수 저장용 테이블.

    기존 chat_room/chatting/score 구조는 정적 시나리오 기반 학생 Session과 직접
    연결되어 있지 않으므로, 기존 테이블을 변경하지 않고 평가 결과만 최소 단위로
    영속화합니다. 사용자 입력 원문과 AI 대사는 저장하지 않습니다.
    """

    __tablename__ = "ai_evaluation"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "stage_id",
            name="UK_AI_EVALUATION_SESSION_STAGE",
        ),
        CheckConstraint(
            "risk_awareness >= 0 AND risk_awareness <= 3",
            name="CHK_AI_EVALUATION_RISK_RANGE",
        ),
        CheckConstraint(
            "refusal >= 0 AND refusal <= 3",
            name="CHK_AI_EVALUATION_REFUSAL_RANGE",
        ),
        CheckConstraint(
            "help_request >= 0 AND help_request <= 3",
            name="CHK_AI_EVALUATION_HELP_RANGE",
        ),
    )

    evaluation_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            primary_key=True,
            autoincrement=True,
        ),
    )

    session_id: str = Field(max_length=36, index=True)
    episode_id: str = Field(max_length=20, index=True)
    stage_id: str = Field(max_length=50, index=True)

    risk_awareness: int = Field(default=0)
    refusal: int = Field(default=0)
    help_request: int = Field(default=0)

    llm_provider: str | None = Field(default=None, max_length=50)
    llm_model: str | None = Field(default=None, max_length=100)

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )
