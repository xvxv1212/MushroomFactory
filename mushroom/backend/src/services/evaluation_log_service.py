"""실제 LLM 평가 결과를 DB에 저장하는 서비스.

학생 서비스는 DB 장애와 분리되어야 하므로 저장 실패를 예외로 전파하지 않습니다.
또한 사용자 입력 원문, NPC 대사, 피드백 원문은 저장하지 않고 점수와 식별자만 저장합니다.
"""

import os

from sqlmodel import Session, select

from database.connection import engine_url
from model.ai_evaluation import AiEvaluation


_SCORE_KEYS = (
    "risk_awareness",
    "refusal",
    "help_request",
)


def _normalized_score(scores: dict, key: str) -> int:
    value = int(scores.get(key, 0))
    return max(0, min(3, value))


def persist_ai_evaluation(
    *,
    session_id: str,
    episode_id: str,
    stage_id: str,
    scores: dict,
) -> bool:
    """실제 AI 평가 점수를 session_id + stage_id 기준으로 저장/갱신합니다.

    Returns:
        True: 저장 또는 갱신 성공
        False: DB 오류 등으로 저장하지 못함
    """

    normalized_scores = {
        key: _normalized_score(scores, key)
        for key in _SCORE_KEYS
    }

    try:
        with Session(engine_url) as db_session:
            existing = db_session.exec(
                select(AiEvaluation).where(
                    AiEvaluation.session_id == session_id,
                    AiEvaluation.stage_id == stage_id,
                )
            ).first()

            if existing is None:
                evaluation = AiEvaluation(
                    session_id=session_id,
                    episode_id=episode_id,
                    stage_id=stage_id,
                    risk_awareness=normalized_scores["risk_awareness"],
                    refusal=normalized_scores["refusal"],
                    help_request=normalized_scores["help_request"],
                    llm_provider=os.getenv("LLM_PROVIDER", "openai"),
                    llm_model=os.getenv("LLM_MODEL"),
                )
                db_session.add(evaluation)
                action = "INSERT"
            else:
                existing.episode_id = episode_id
                existing.risk_awareness = normalized_scores["risk_awareness"]
                existing.refusal = normalized_scores["refusal"]
                existing.help_request = normalized_scores["help_request"]
                existing.llm_provider = os.getenv("LLM_PROVIDER", "openai")
                existing.llm_model = os.getenv("LLM_MODEL")
                db_session.add(existing)
                action = "UPDATE"

            db_session.commit()

        print(
            f"[AI EVALUATION DB {action}] "
            f"session_id={session_id}, episode_id={episode_id}, stage_id={stage_id}"
        )
        return True

    except Exception as exc:
        # 사용자 답변 원문은 로그에 남기지 않습니다.
        print(
            "[AI EVALUATION DB WARNING] "
            f"save failed: {type(exc).__name__}: {exc}"
        )
        return False
