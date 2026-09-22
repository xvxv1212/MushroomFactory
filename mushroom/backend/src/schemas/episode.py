# 에피소드와 Stage JSON을 API 응답으로 검증하는 스키마 모듈입니다.
from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


class DialogueMessage(BaseModel):
    # 장면 안에서 특정 인물이 말한 한 줄의 대사입니다.
    speaker: str

    text: str


class StageResponse(BaseModel):
    # 하나의 Stage에 필요한 장면 정보와 평가 기준입니다.
    stage_id: str

    stage_number: int

    title: str

    type: str

    location: str

    description: str

    messages: list[
        DialogueMessage
    ]

    question: str

    evaluation_axis: str

    evaluation_criteria: list[str]

    next_stage: Optional[str] = None


class EpisodeSummary(BaseModel):
    # 에피소드 목록 화면에 필요한 요약 정보입니다.
    episode_id: str

    title: str

    description: str

    total_stages: int


class EpisodeDetailResponse(BaseModel):
    # 에피소드 전체 정보와 포함된 Stage 목록입니다.
    episode_id: str

    title: str

    description: str

    total_stages: int

    stages: list[
        StageResponse
    ]
