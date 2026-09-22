# 사용자 답변을 평가하고 다음 Stage로 진행시키는 API 모듈입니다.
import asyncio
import logging

from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from schemas.chat import (
    ChatRequest,
    ChatResponse
)

from core.scenario_engine import (
    get_stage
)

from core.session_store import (
    session_store
)

from services.fallback_service import (
    build_fallback_result
)


router = APIRouter(
    tags=["Chat"]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
    logger.addHandler(console_handler)
logger.propagate = False

@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):
    # 1. Session 존재 확인
    session = session_store.get_session(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # 2. Session의 Episode와 요청 Episode 일치 확인
    if session["episode_id"] != request.episode_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Episode does not match session"
        )

    # 3. 이미 Episode가 완료됐는지 확인
    if session["is_complete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Episode already completed"
        )

    # 4. 이미 완료한 Stage인지 확인
    if request.stage_id in session["completed_stages"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage already completed"
        )

    expected_prefix = f"{request.episode_id}_STAGE"

    if not request.stage_id.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage does not belong to episode"
        )

    # 5. 현재 진행해야 할 Stage인지 확인
    if session["current_stage"] != request.stage_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid stage"
        )

    # 6. Scenario에서 현재 Stage 조회
    stage = get_stage(
        request.episode_id,
        request.stage_id
    )

    if stage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )

    # 7. AI 평가
    # LLM 장애/타임아웃이 학생 학습 중단으로 이어지지 않도록
    # 검수된 시나리오 기반 fallback 응답으로 자동 전환합니다.
    fallback_mode = False
    analysis_available = True

    try:
        from services.ai_service import evaluate_response

        ai_result = await asyncio.wait_for(
            evaluate_response(
                episode_id=request.episode_id,
                stage_id=request.stage_id,
                user_message=request.message,
                stage_data=stage
            ),
            timeout=20
        )

    except (asyncio.TimeoutError, Exception) as exc:
        # 사용자 message 원문은 로그에 남기지 않음
        print(
            "AI evaluation unavailable - fallback enabled:",
            type(exc).__name__
        )

        ai_result = build_fallback_result(stage)
        fallback_mode = True
        analysis_available = False

    required_ai_fields = {
        "npc_response",
        "feedback",
        "scores"
    }

    if not required_ai_fields.issubset(ai_result.keys()):
        ai_result = build_fallback_result(stage)
        fallback_mode = True
        analysis_available = False

    required_score_fields = {
        "risk_awareness",
        "refusal",
        "help_request"
    }

    scores = ai_result.get("scores", {})

    if not required_score_fields.issubset(scores.keys()):
        ai_result = build_fallback_result(stage)
        scores = ai_result["scores"]
        fallback_mode = True
        analysis_available = False

    # 서비스 레이어가 직접 fallback 표시를 내려주는 경우도 반영
    if ai_result.get("fallback_mode") is True:
        fallback_mode = True

    if ai_result.get("analysis_available") is False:
        analysis_available = False

    # 8. 다음 Stage는 AI가 아닌 검수된 Scenario가 결정
    next_stage = stage.get("next_stage")

    # 9. 점수 + Stage 결과 + 진행상태 저장
    saved = session_store.apply_stage_result(
        session_id=request.session_id,
        stage_id=request.stage_id,
        feedback=ai_result["feedback"],
        scores=scores,
        next_stage=next_stage,
        analysis_available=analysis_available
    )

    if not saved:
        raise HTTPException(
            status_code=409,
            detail="Failed to save stage result"
        )

    # 10. Episode 종료 여부
    is_episode_complete = next_stage is None

    # 11. Frontend 반환
    return ChatResponse(
        npc_response=ai_result["npc_response"],
        feedback=ai_result["feedback"],
        scores=scores,
        next_stage=next_stage,
        is_episode_complete=is_episode_complete,
        fallback_mode=fallback_mode,
        analysis_available=analysis_available
    )
