# Scenario API Contract

## 1. 기본 규칙

Scenario API는 EP01, EP02 및 이후 추가되는 Episode에서
동일한 API 구조를 사용한다.

Episode ID:

- EP01
- EP02

Stage ID:

- EP01_STAGE01 ~ EP01_STAGE05
- EP02_STAGE01 ~ EP02_STAGE05

평가 축:

- risk_awareness
- refusal
- help_request

각 Stage의 점수는 0~3점이다.

---

## 2. Episode 목록

GET /api/episodes

Response

[
  {
    "episode_id": "EP01",
    "title": "시험기간 스터디 그룹",
    "description": "시험기간 스터디 그룹에서 발생하는 위험 상황에 대응해봅니다.",
    "total_stages": 5
  },
  {
    "episode_id": "EP02",
    "title": "SNS에서 시작된 유혹",
    "description": "SNS에서 출처 불명의 약물 권유를 받는 상황에 대응해봅니다.",
    "total_stages": 5
  }
]

---

## 3. Episode 상세

GET /api/episodes/{episode_id}

예:

GET /api/episodes/EP02

Response

{
  "episode_id": "EP02",
  "title": "SNS에서 시작된 유혹",
  "background": {
    "character": "중학교 1학년 학생",
    "situation": "SNS를 이용하던 중 다이어트와 기분 전환에 도움이 된다는 출처 불명의 약물 게시물을 접하고, 이후 모르는 계정으로부터 약물을 권유받는 상황을 경험한다."
  },
  "total_stages": 5
}

---

## 4. Stage 조회

GET /api/episodes/{episode_id}/stages/{stage_id}

예:

GET /api/episodes/EP02/stages/EP02_STAGE01

Response

{
  "episode_id": "EP02",
  "stage_id": "EP02_STAGE01",
  "stage_number": 1,
  "total_stages": 5,
  "title": "SNS 속 유혹 인지",
  "location": "SNS 피드",
  "description": "SNS를 보던 중 먹으면 살이 빠지고 기분이 좋아진다는 출처 불명의 약물을 소개하는 게시물을 발견한다.",
  "messages": [
    {
      "speaker": "SNS 게시물",
      "text": "요즘 이거 먹고 살 빠졌다는 사람 많음."
    },
    {
      "speaker": "SNS 게시물",
      "text": "식단이나 운동 힘들면 이걸로 관리해봐."
    },
    {
      "speaker": "SNS 게시물",
      "text": "기분도 한결 편해지고 스트레스도 덜함."
    }
  ],
  "question": "이 게시물에서 어떤 점이 가장 신경 쓰이나요?",
  "evaluation_axis": "risk_awareness"
}

---

## 5. 사용자 답변

POST /api/chat

Request

{
  "session_id": "temporary-session-id",
  "episode_id": "EP02",
  "stage_id": "EP02_STAGE01",
  "message": "무슨 약인지 모르고 출처도 불분명해서 위험한 것 같아."
}

---

## 6. Chat Response

Response

{
  "episode_id": "EP02",
  "stage_id": "EP02_STAGE01",
  "npc_response": "그렇게까지 걱정할 필요 있어? 다들 괜찮다는데.",
  "feedback": "약물의 출처와 안전성을 의심한 점이 좋아요.",
  "axis": "risk_awareness",
  "score": 3,
  "next_stage": "EP02_STAGE02",
  "episode_completed": false
}

---

## 7. 마지막 Stage

EP02_STAGE05 완료 시:

{
  "episode_id": "EP02",
  "stage_id": "EP02_STAGE05",
  "npc_response": "알겠어... 하지만 다른 사람에게는 말하지 않았으면 좋겠어.",
  "feedback": "비밀 유지 요구를 따르지 않고 도움을 요청하려 한 점이 좋아요.",
  "axis": "help_request",
  "score": 3,
  "next_stage": null,
  "episode_completed": true
}

---

## 8. Result

GET /api/sessions/{session_id}/episodes/EP02/result

Response

{
  "episode_id": "EP02",
  "title": "SNS에서 시작된 유혹",
  "scores": {
    "risk_awareness": 67,
    "refusal": 83,
    "help_request": 83
  },
  "stage_scores": {
    "EP02_STAGE01": 2,
    "EP02_STAGE02": 3,
    "EP02_STAGE03": 2,
    "EP02_STAGE04": 3,
    "EP02_STAGE05": 2
  },
  "completed": true
}

---

## 9. Scenario 진행 규칙

다음 Stage는 AI가 결정하지 않는다.

각 Episode JSON의 `next_stage` 값을 Backend가 사용한다.

예:

EP02_STAGE01
→ EP02_STAGE02
→ EP02_STAGE03
→ EP02_STAGE04
→ EP02_STAGE05
→ null

사용자의 답변 내용과 관계없이
Episode의 Stage 순서는 변경되지 않는다.

AI는 다음 항목만 생성한다.

- npc_response
- feedback
- score

`next_stage`와 `episode_completed`는
Backend/Scenario 규칙에 따라 결정한다.

---

## 10. 평가 기준 보안

`evaluation_criteria`와 Rubric은
Frontend 응답에 포함하지 않는다.

평가 기준은 Backend/AI 내부에서 사용한다.

Frontend에는 다음 정보만 전달한다.

- question
- messages
- npc_response
- feedback
- axis
- score
- next_stage
- episode_completed

---

## 11. 평가 축

risk_awareness
refusal
help_request

평가 축 이름은 모든 Episode에서 동일하게 사용한다.