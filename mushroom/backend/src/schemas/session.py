# 학습 Session 생성·상태·결과 API에서 사용하는 스키마 모듈입니다.
from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


# =========================
# 점수 Schema
# =========================

class StageScores(BaseModel):
    risk_awareness: int = Field(ge=0, le=3)
    refusal: int = Field(ge=0, le=3)
    help_request: int = Field(ge=0, le=3)


class TotalScores(BaseModel):
    risk_awareness: int = Field(ge=0)
    refusal: int = Field(ge=0)
    help_request: int = Field(ge=0)


# =========================
# Stage 결과
# =========================

class StageResultResponse(BaseModel):
    stage_id: str
    feedback: str
    scores: StageScores
    analysis_available: bool = True


# =========================
# Session 생성
# =========================

class SessionCreateRequest(BaseModel):
    episode_id: str


class SessionCreateResponse(BaseModel):
    session_id: str
    episode_id: str
    current_stage: str
    fallback_mode: bool = False
    analysis_available: bool = True


# =========================
# Session 현재 상태
# =========================

class SessionStateResponse(BaseModel):
    session_id: str
    episode_id: str
    current_stage: Optional[str]
    completed_stages: list[str]
    scores: TotalScores
    progress: int = Field(ge=0, le=100)
    is_complete: bool
    fallback_mode: bool = False
    analysis_available: bool = True


# =========================
# Session 최종 결과
# =========================

class SessionResultResponse(BaseModel):
    episode_id: str
    scores: TotalScores
    stage_results: list[StageResultResponse]
    completed_stages: list[str]
    is_complete: bool
    fallback_mode: bool = False
    analysis_available: bool = True
