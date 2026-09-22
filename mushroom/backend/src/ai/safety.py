import re
from pydantic import BaseModel
from typing import Optional


class SafetyResult(BaseModel):
    blocked: bool
    reason: Optional[str] = None
    feedback: Optional[str] = None


def normalize_text(message: str) -> str:
    return " ".join(
        message
        .strip()
        .lower()
        .split()
    )


ABUSIVE_PATTERNS = [
    "씨발",
    "시발",
    "ㅅㅂ",
    "병신",
    "개새끼",
    "좆",
    "지랄",
    "쉣",
]


DANGEROUS_PATTERNS = [
    "어디서 구해",
    "어디서 사",
    "구매 방법",
    "사는 방법",
    "제조 방법",
    "만드는 방법",
    "복용량",
    "얼마나 먹어",
    "숨기는 방법",
    "안 걸리는 방법",
]


PROMPT_INJECTION_PATTERNS = [
    "이전 지시 무시",
    "위 지시 무시",
    "규칙 무시",
    "프롬프트 무시",
    "시스템 프롬프트",
    "너의 지시를 무시",
]


# 장면에 대한 실제 대응으로 보기 어려운 짧은 확인/추임새 입력입니다.
# "싫어", "안 먹어", "신고할래"처럼 짧더라도 의미가 분명한 문장은
# 여기에 넣지 않습니다.
INSUFFICIENT_EXACT_INPUTS = {
    "ㅇ",
    "ㅇㅇ",
    "응",
    "응응",
    "웅",
    "어",
    "네",
    "넵",
    "예",
    "ㅇㅋ",
    "오케이",
    "ok",
    "okay",
    "ㄴ",
    "ㄴㄴ",
    "몰라",
    "모름",
    "글쎄",
    "그냥",
    "아무거나",
    "음",
    "흠",
    "ㅋㅋ",
    "ㅋㅋㅋ",
    "ㅎㅎ",
    "ㅎㅎㅎ",
}


def is_insufficient_response(message: str) -> bool:
    """실제 대응 의도를 판단하기 어려운 입력인지 확인합니다.

    단순 글자 수로 차단하지 않습니다. 예를 들어 "싫어"는 짧지만
    거절 의사가 명확하므로 정상 답변으로 AI 평가에 전달됩니다.
    """
    text = normalize_text(message)
    compact = re.sub(r"\s+", "", text)

    if not compact:
        return True

    if compact in INSUFFICIENT_EXACT_INPUTS:
        return True

    # 자음/웃음/울음/구두점만 반복된 입력도 실제 답변으로 보지 않습니다.
    if re.fullmatch(r"[ㅇㅋㅎㅠㅜㄴ.!?~]+", compact):
        return True

    return False


def check_user_message(message: str) -> SafetyResult:
    text = normalize_text(message)

    # 빈 입력
    if not text:
        return SafetyResult(
            blocked=True,
            reason="empty_message",
            feedback="답변을 입력한 뒤 다시 시도해 주세요."
        )

    # 'ㅇㅇ', 'ㅋㅋ'처럼 장면 대응을 판단하기 어려운 입력
    if is_insufficient_response(message):
        return SafetyResult(
            blocked=True,
            reason="insufficient_response",
            feedback=(
                "지금 답변만으로는 어떤 대응을 하려는지 알기 어려워요. "
                "왜 그렇게 생각했는지 또는 무엇을 하겠는지 "
                "실제로 말하듯 한 문장으로 표현해보세요."
            )
        )

    # 욕설
    for pattern in ABUSIVE_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="abusive_language",
                feedback=(
                    "공격적인 표현 대신 "
                    "현재 상황에서 자신의 생각이나 "
                    "행동을 문장으로 표현해 주세요."
                )
            )

    # 위험정보 요청
    for pattern in DANGEROUS_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="dangerous_information",
                feedback=(
                    "위험한 약물의 구매·제조·복용·은폐 방법은 "
                    "안내할 수 없어요. 현재 상황에서 자신을 안전하게 "
                    "지키는 방법을 생각해보세요."
                )
            )

    # Prompt Injection
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="prompt_injection",
                feedback=(
                    "현재 에피소드의 안전한 대응 연습 범위 안에서 "
                    "답변해 주세요."
                )
            )

    return SafetyResult(blocked=False)


# AI를 사용할 수 없는 경우에는 의미 없는 입력을 다음 Stage로 넘기지 않기 위해
# 보수적인 키워드 기반 검사를 추가로 사용합니다.
# 온라인 AI 평가에서는 이 함수만으로 의미를 판단하지 않고 LLM의 의미 판정을 함께 사용합니다.
FALLBACK_MEANINGFUL_MARKERS = (
    # -----------------------------------------------------------------
    # 중요: 이 목록은 "좋은 답" 목록이 아니라 "의도가 있는 답" 목록입니다.
    # 안전하지 않은 선택도 실제 대응 의사가 분명하면 Stage 평가 대상으로
    # 보내야 합니다. 예: "나도 먹을래", "그냥 한번 먹어볼래".
    # 이런 답변을 재입력으로 막아버리면 사용자는 잘못된 선택을 해보고
    # 교육 피드백을 받을 수 없게 됩니다.
    # -----------------------------------------------------------------

    # 거절 / 회피 / 안전 행동
    "싫", "안 먹", "먹지", "거절", "안 할", "하지 않", "필요 없",
    "그만", "됐어", "괜찮아", "자리", "떠날", "나갈", "피할", "차단",

    # 수락 / 위험한 선택도 '의미 있는 대응'이므로 평가 가능
    "먹을래", "먹을게", "먹겠다", "먹어볼", "먹어 보", "먹어야",
    "써볼", "사용할", "해볼", "해 볼", "마실래", "마실게",
    "받을래", "받을게", "따라할", "같이 할", "나도 먹", "나만 먹",

    # 위험 인지
    "위험", "수상", "이상", "출처", "정체", "성분", "안전", "모르",
    "확인", "불분명", "의심", "걱정", "약", "알약", "사진", "포장",
    "처방", "약국", "병원", "믿", "문제",

    # 도움 요청 / 신고
    "선생", "교사", "부모", "보호자", "어른", "상담", "신고", "도움",
    "119", "112", "보건", "알리", "말할", "말하", "연락", "구급", "도와",

    # 판단 / 행동 의사 표현
    "아닌 것", "하지 말", "해야", "하겠", "할래", "할게",
    "생각", "같아", "보여", "왜", "좋아", "싫어"
)


def is_fallback_response_meaningful(message: str, stage_data: dict | None = None) -> bool:
    """AI 장애 시 다음 Stage 진행 여부를 보수적으로 판단합니다.

    명확한 안전 대응 표현이 확인되지 않으면 같은 Stage에서 다시 입력받습니다.
    오탐보다 무의미한 입력으로 학습이 넘어가는 것을 막는 쪽을 우선합니다.
    """
    if is_insufficient_response(message):
        return False

    text = normalize_text(message)

    if any(marker in text for marker in FALLBACK_MEANINGFUL_MARKERS):
        return True

    # 숫자/기호/랜덤 토큰만 섞인 짧은 입력은 거절합니다.
    compact = re.sub(r"[^0-9a-z가-힣]", "", text)
    if len(compact) < 4:
        return False

    # fallback에서는 장면과의 관련성을 확인할 AI가 없으므로,
    # 위 의미 표지가 없는 문장은 사용자에게 한 번 더 구체화를 요청합니다.
    return False
