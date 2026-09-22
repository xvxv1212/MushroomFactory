# 채팅 요청과 AI 평가 응답의 데이터 형식을 정의합니다.
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    # 현재 Session과 Stage를 식별하고 사용자의 답변을 전달합니다.
    session_id: str = Field(
        min_length=1
    )

    episode_id: str = Field(
        min_length=1
    )

    stage_id: str = Field(
        min_length=1
    )

    message: str = Field(
        min_length=1,
        max_length=500
    )

    @field_validator("message")
    @classmethod
    def validate_message(
        cls,
        value: str
    ) -> str:
        # 공백만 입력된 답변을 거부하고 실제 텍스트만 반환합니다.
        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be empty"
            )

        return value


class Scores(BaseModel):
    # 한 번의 답변에 대한 세 가지 행동 평가 점수입니다.
    risk_awareness: int = Field(default=0, ge=0, le=3)
    refusal: int = Field(default=0, ge=0, le=3)
    help_request: int = Field(default=0, ge=0, le=3)


class ChatResponse(BaseModel):
    # 채팅 API가 프론트엔드에 반환하는 최종 응답입니다.
    npc_response: str
    feedback: str
    scores: Scores

    next_stage: Optional[str] = None

    is_episode_complete: bool = False

    # 외부 AI/서버 일부 장애로 검수된 fallback 응답을 사용했는지 표시
    fallback_mode: bool = False

    # False이면 숫자 점수는 AI 기반 분석 결과가 아니므로 UI에서 숨김
    analysis_available: bool = True

    # True이면 현재 답변은 평가 가능한 대응으로 보지 않고 같은 Stage에서
    # 다시 입력받습니다. (예: "ㅇㅇ", "ㅋㅋ", 욕설/위험정보 요청 등)
    retry_required: bool = False
