"""개발/DB 연동 확인용 실행 흐름 추적 유틸리티.

목적
- 웹에서 마냥이를 실행했을 때 어떤 파일/함수가 호출되는지 확인
- 함수에 들어오는 값(IN), 반환하는 값(OUT), DB에 저장 후보가 되는 값(DB-CANDIDATE)을 확인
- 비밀번호/API 키/토큰/사용자 원문 메시지는 기본적으로 노출하지 않음

환경변수
- DB_FLOW_TRACE=1                : 추적 로그 출력 (기본 1)
- DB_FLOW_TRACE_INCLUDE_MESSAGE=1: 사용자 message 원문까지 출력 (기본 0, 로컬 테스트에서만 권장)
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from typing import Any


TRACE_ENABLED = os.getenv("DB_FLOW_TRACE", "1").lower() not in {
    "0",
    "false",
    "off",
    "no",
}

TRACE_INCLUDE_MESSAGE = os.getenv(
    "DB_FLOW_TRACE_INCLUDE_MESSAGE",
    "0",
).lower() in {
    "1",
    "true",
    "on",
    "yes",
}

_SECRET_KEYS = {
    "password",
    "passwd",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "authorization",
    "secret",
    "secret_key",
}

_MESSAGE_KEYS = {
    "message",
    "user_message",
}


def _safe_value(key: str | None, value: Any) -> Any:
    """로그에 출력해도 안전한 값으로 변환합니다."""
    normalized_key = (key or "").lower()

    if normalized_key in _SECRET_KEYS:
        return "<redacted>"

    if normalized_key in _MESSAGE_KEYS and isinstance(value, str):
        if TRACE_INCLUDE_MESSAGE:
            return value
        return f"<hidden len={len(value)}>"

    if isinstance(value, Mapping):
        return {
            str(child_key): _safe_value(str(child_key), child_value)
            for child_key, child_value in value.items()
        }

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_safe_value(None, item) for item in value]

    # Path, UUID, Pydantic 객체 등 JSON 직렬화가 어려운 값은 문자열 처리
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def trace_flow(
    file_path: str,
    function_name: str,
    event: str,
    data: Any = None,
) -> None:
    """일반 실행 흐름 로그를 한 줄로 출력합니다."""
    if not TRACE_ENABLED:
        return

    safe_data = _safe_value(None, data)
    encoded = json.dumps(
        safe_data,
        ensure_ascii=False,
        default=str,
    )

    print(
        f"[FLOW][{event}] "
        f"{file_path}::{function_name} | {encoded}"
    )


def trace_db_candidate(
    file_path: str,
    function_name: str,
    action: str,
    data: Any = None,
) -> None:
    """DB 담당자가 저장/조회 후보를 바로 찾도록 별도 태그를 붙입니다."""
    if not TRACE_ENABLED:
        return

    safe_data = _safe_value(None, data)
    encoded = json.dumps(
        safe_data,
        ensure_ascii=False,
        default=str,
    )

    print(
        f"[DB-CANDIDATE][{action}] "
        f"{file_path}::{function_name} | {encoded}"
    )


def print_route_map(app: Any) -> None:
    """FastAPI에 실제 등록된 API 경로와 endpoint 함수명을 출력합니다.

    같은 METHOD + PATH가 두 번 등록되면 DUPLICATE 표시를 남깁니다.
    현재 프로젝트의 routes/episodes.py와 routes/sessions.py처럼 중복 라우트가
    존재하는지 DB/백엔드 담당자가 실행 즉시 파악할 수 있습니다.
    """
    if not TRACE_ENABLED:
        return

    seen: set[tuple[str, str]] = set()

    print("\n========== MANYANG API ROUTE MAP ==========")

    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])
        endpoint = getattr(route, "endpoint", None)
        endpoint_name = getattr(endpoint, "__name__", "<unknown>")
        module_name = getattr(endpoint, "__module__", "<unknown>")

        if not (
            path.startswith("/api")
            or path.startswith("/admins")
        ):
            continue

        if not methods:
            methods = ["-"]

        for method in methods:
            key = (method, path)
            duplicate = "  <-- DUPLICATE" if key in seen else ""
            seen.add(key)

            print(
                f"[ROUTE] {method:7} {path:35} "
                f"-> {module_name}.{endpoint_name}{duplicate}"
            )

    print("===========================================\n")
