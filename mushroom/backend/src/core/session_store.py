"""학습 Session 상태 저장소.

[DB 담당 핵심]
현재 이 파일이 사실상 "임시 DB" 역할을 합니다.
모든 학습 진행 상태는 ``self._sessions`` 메모리 딕셔너리에만 저장되며
서버가 재시작되면 사라집니다.

실제 DB 연동 시 우선적으로 교체/연결할 함수
1. create_session()      : 새 학습 세션 INSERT
2. get_session()         : 진행 중 세션 SELECT
3. get_session_state()   : 현재 진행상태/누적점수 SELECT
4. apply_stage_result()  : Stage 결과 + 점수 + 다음 Stage UPDATE/INSERT
5. get_result()          : 최종 결과 SELECT
6. delete_session()      : 삭제 또는 상태 종료 UPDATE

실행 시 [DB-CANDIDATE] 로그를 보면 각 함수에 어떤 데이터가 들어오고
어떤 데이터가 나가는지 확인할 수 있습니다.
"""

from copy import deepcopy
from typing import Dict, Optional

from core.flow_trace import (
    trace_flow,
    trace_db_candidate,
)


FILE = "backend/src/core/session_store.py"


class MemorySessionStore:
    # 서버 프로세스가 실행되는 동안만 유지되는 Session 저장소입니다.

    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    def create_session(
        self,
        session_id: str,
        episode_id: str,
        first_stage: str
    ) -> dict:
        trace_flow(
            FILE,
            "MemorySessionStore.create_session",
            "IN",
            {
                "session_id": session_id,
                "episode_id": episode_id,
                "first_stage": first_stage,
            },
        )

        session = {
            "episode_id": episode_id,
            "current_stage": first_stage,
            "completed_stages": [],
            "stage_results": [],
            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            },
            "is_complete": False,
            "analysis_available": True,
            "fallback_mode": False
        }

        self._sessions[session_id] = session

        trace_db_candidate(
            FILE,
            "MemorySessionStore.create_session",
            "MEMORY_WRITE -> DB_INSERT_CANDIDATE",
            {
                "session_id": session_id,
                **session,
            },
        )

        result = deepcopy(session)
        trace_flow(
            FILE,
            "MemorySessionStore.create_session",
            "OUT",
            result,
        )
        return result

    def get_session(
        self,
        session_id: str
    ) -> Optional[dict]:
        trace_flow(
            FILE,
            "MemorySessionStore.get_session",
            "IN",
            {"session_id": session_id},
        )

        session = self._sessions.get(session_id)

        if session is None:
            trace_flow(
                FILE,
                "MemorySessionStore.get_session",
                "OUT",
                None,
            )
            return None

        result = deepcopy(session)

        trace_db_candidate(
            FILE,
            "MemorySessionStore.get_session",
            "MEMORY_READ -> DB_SELECT_CANDIDATE",
            {
                "session_id": session_id,
                "episode_id": result.get("episode_id"),
                "current_stage": result.get("current_stage"),
                "is_complete": result.get("is_complete"),
            },
        )

        trace_flow(
            FILE,
            "MemorySessionStore.get_session",
            "OUT",
            result,
        )
        return result

    def get_session_state(
        self,
        session_id: str,
        total_stages: int
    ) -> Optional[dict]:
        trace_flow(
            FILE,
            "MemorySessionStore.get_session_state",
            "IN",
            {
                "session_id": session_id,
                "total_stages": total_stages,
            },
        )

        session = self._sessions.get(session_id)

        if session is None:
            return None

        completed_count = len(session["completed_stages"])
        progress = 0 if total_stages <= 0 else int(
            completed_count / total_stages * 100
        )

        result = {
            "session_id": session_id,
            "episode_id": session["episode_id"],
            "current_stage": session["current_stage"],
            "completed_stages": list(session["completed_stages"]),
            "scores": deepcopy(session["scores"]),
            "progress": progress,
            "is_complete": session["is_complete"],
            "fallback_mode": session.get("fallback_mode", False),
            "analysis_available": session.get("analysis_available", True)
        }

        trace_db_candidate(
            FILE,
            "MemorySessionStore.get_session_state",
            "SESSION_STATE_SELECT_CANDIDATE",
            result,
        )

        trace_flow(
            FILE,
            "MemorySessionStore.get_session_state",
            "OUT",
            result,
        )
        return result

    def apply_stage_result(
        self,
        session_id: str,
        stage_id: str,
        feedback: str,
        scores: dict,
        next_stage: Optional[str],
        analysis_available: bool = True
    ) -> bool:
        trace_flow(
            FILE,
            "MemorySessionStore.apply_stage_result",
            "IN",
            {
                "session_id": session_id,
                "stage_id": stage_id,
                "feedback": feedback,
                "scores": scores,
                "next_stage": next_stage,
                "analysis_available": analysis_available,
            },
        )

        session = self._sessions.get(session_id)

        if session is None:
            return False

        if stage_id in session["completed_stages"]:
            return False

        # 1) 누적 점수 갱신
        current_scores = session["scores"]
        current_scores["risk_awareness"] += scores.get("risk_awareness", 0)
        current_scores["refusal"] += scores.get("refusal", 0)
        current_scores["help_request"] += scores.get("help_request", 0)

        # 2) Stage 단위 결과 저장
        stage_result = {
            "stage_id": stage_id,
            "feedback": feedback,
            "scores": {
                "risk_awareness": scores.get("risk_awareness", 0),
                "refusal": scores.get("refusal", 0),
                "help_request": scores.get("help_request", 0)
            },
            "analysis_available": analysis_available
        }
        session["stage_results"].append(stage_result)

        # 3) 진행 상태 갱신
        session["completed_stages"].append(stage_id)
        session["current_stage"] = next_stage
        session["is_complete"] = next_stage is None

        if not analysis_available:
            session["analysis_available"] = False
            session["fallback_mode"] = True

        # DB 연동 시 한 Stage 완료 트랜잭션으로 묶기 좋은 데이터입니다.
        trace_db_candidate(
            FILE,
            "MemorySessionStore.apply_stage_result",
            "STAGE_RESULT_WRITE -> DB_TRANSACTION_CANDIDATE",
            {
                "session_id": session_id,
                "stage_result": stage_result,
                "total_scores": session["scores"],
                "completed_stages": session["completed_stages"],
                "current_stage": session["current_stage"],
                "is_complete": session["is_complete"],
                "fallback_mode": session.get("fallback_mode", False),
                "analysis_available": session.get("analysis_available", True),
            },
        )

        trace_flow(
            FILE,
            "MemorySessionStore.apply_stage_result",
            "OUT",
            True,
        )
        return True

    def get_result(
        self,
        session_id: str
    ) -> Optional[dict]:
        trace_flow(
            FILE,
            "MemorySessionStore.get_result",
            "IN",
            {"session_id": session_id},
        )

        session = self._sessions.get(session_id)

        if session is None:
            return None

        result = {
            "episode_id": session["episode_id"],
            "scores": deepcopy(session["scores"]),
            "stage_results": deepcopy(session["stage_results"]),
            "completed_stages": list(session["completed_stages"]),
            "is_complete": session["is_complete"],
            "fallback_mode": session.get("fallback_mode", False),
            "analysis_available": session.get("analysis_available", True)
        }

        trace_db_candidate(
            FILE,
            "MemorySessionStore.get_result",
            "FINAL_RESULT_SELECT_CANDIDATE",
            {
                "session_id": session_id,
                **result,
            },
        )

        trace_flow(
            FILE,
            "MemorySessionStore.get_result",
            "OUT",
            result,
        )
        return result

    def delete_session(
        self,
        session_id: str
    ) -> bool:
        trace_flow(
            FILE,
            "MemorySessionStore.delete_session",
            "IN",
            {"session_id": session_id},
        )

        if session_id not in self._sessions:
            return False

        del self._sessions[session_id]

        trace_db_candidate(
            FILE,
            "MemorySessionStore.delete_session",
            "MEMORY_DELETE -> DB_DELETE_OR_CLOSE_CANDIDATE",
            {"session_id": session_id},
        )

        trace_flow(
            FILE,
            "MemorySessionStore.delete_session",
            "OUT",
            True,
        )
        return True

    def clear(self):
        self._sessions.clear()
        trace_flow(
            FILE,
            "MemorySessionStore.clear",
            "OUT",
            {"cleared": True},
        )


session_store = MemorySessionStore()
