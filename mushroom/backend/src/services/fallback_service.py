"""검수된 시나리오 기반의 서버-side fallback 응답.

외부 LLM이 타임아웃/장애여도 학생 학습 흐름을 멈추지 않게 합니다.
점수는 AI 평가가 아니므로 모두 0으로 두고 analysis_available=False를
명시합니다. 사용자 입력 원문은 저장하거나 로그에 남기지 않습니다.
"""


def _axis(stage_data: dict) -> str:
    return str(
        stage_data.get("evaluation_axis")
        or stage_data.get("type")
        or ""
    ).lower()


def build_fallback_result(stage_data: dict) -> dict:
    axis = _axis(stage_data)

    if "risk" in axis:
        npc_response = "다들 괜찮다고 하던데, 그렇게까지 신경 써야 해?"
        feedback = (
            "출처·성분·안전성이 확인되지 않은 점을 먼저 살피는 게 핵심이야. "
            "홍보 문구나 주변 사람의 말만 믿지 말고, 불분명하면 사용하지 않는 선택이 안전해."
        )
    elif "refusal" in axis:
        npc_response = "알겠어. 그래도 한 번만 더 생각해봐."
        feedback = (
            "권유를 받을 때는 ‘나는 안 할래’처럼 짧고 분명하게 말해도 괜찮아. "
            "계속 압박한다면 대화를 끝내거나 그 자리를 벗어나는 것도 좋은 대응이야."
        )
    else:
        npc_response = "굳이 다른 사람에게까지 말할 필요는 없잖아."
        feedback = (
            "혼자 해결하려 하지 말고 보호자·교사·상담기관처럼 믿을 수 있는 어른에게 "
            "상황을 알리는 선택이 중요해. 위험한 접촉은 이어가지 않는 게 좋아."
        )

    return {
        "npc_response": npc_response,
        "feedback": feedback,
        "scores": {
            "risk_awareness": 0,
            "refusal": 0,
            "help_request": 0,
        },
        "fallback_mode": True,
        "analysis_available": False,
    }
