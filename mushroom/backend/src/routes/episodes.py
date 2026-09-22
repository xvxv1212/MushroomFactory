from uuid import uuid4

import logging
from fastapi import (
    APIRouter,
    HTTPException
)

from schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionResultResponse,
    SessionStateResponse
)

from core.session_store import (
    session_store
)

from core.scenario_engine import (
    load_episode,
    get_total_stages
)


router = APIRouter(
    tags=["Sessions"]
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

# =========================
# Session 생성
# =========================

@router.post(
    "/sessions",
    response_model=SessionCreateResponse
)
def start_session(
    request: SessionCreateRequest
):
    logger.debug("episode.py start_session() 실행")
    # 1. Episode 조회
    episode = load_episode(
        request.episode_id
    )

    logger.debug(f"episode : {episode}")

    if episode is None:
        raise HTTPException(
            status_code=404,
            detail="Episode not found"
        )

    # 2. Episode Stage 확인
    stages = episode.get(
        "stages",
        []
    )
    logger.debug(f"stages : {stages}")
    if not stages:
        raise HTTPException(
            status_code=500,
            detail="Episode has no stages"
        )

    # 3. 첫 Stage 결정
    first_stage = stages[0][
        "stage_id"
    ]
    logger.debug(f"first_stage : {first_stage}")
    # 4. Session ID 생성
    session_id = str(
        uuid4()
    )

    # 5. Session 생성
    session = (
        session_store.create_session(
            session_id=session_id,
            episode_id=request.episode_id,
            first_stage=first_stage
        )
    )
    logger.debug(f"session : {session}")

    return {
        "session_id":
            session_id,

        "episode_id":
            request.episode_id,

        "current_stage":
            session["current_stage"]
    }


# =========================
# Session 결과 조회
# =========================

@router.get(
    "/sessions/{session_id}/result",
    response_model=SessionResultResponse
)
def session_result(
    session_id: str
):

    result = (
        session_store.get_result(
            session_id
        )
    )
    logger.debug(f"result : {result}")

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return result


# =========================
# Session 현재 상태 조회
# =========================

@router.get(
    "/sessions/{session_id}",
    response_model=SessionStateResponse
)
@router.get(
    "/sessions/{session_id}",
    response_model=SessionStateResponse
)
def session_state(
    session_id: str
):

    session = (
        session_store.get_session(
            session_id
        )
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    total_stages = (
        get_total_stages(
            session["episode_id"]
        )
    )

    if total_stages <= 0:
        raise HTTPException(
            status_code=500,
            detail="Episode has no stages"
        )

    state = (
        session_store.get_session_state(
            session_id,
            total_stages
        )
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return state


# =========================
# Session 종료
# =========================

@router.delete(
    "/sessions/{session_id}"
)
def end_session(
    session_id: str
):

    deleted = (
        session_store.delete_session(
            session_id
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {
        "message":
            "Session deleted"
    }

