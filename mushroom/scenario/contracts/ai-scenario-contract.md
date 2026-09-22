# AI - Scenario Contract

## 1. 목적

Scenario는 에피소드의 사건, Stage 순서, 평가축, 평가기준을 정의한다.

AI는 Scenario의 내용을 변경하지 않으며,
현재 Stage 안에서 다음 역할만 수행한다.

- NPC 후속 반응 생성
- 사용자 답변 평가
- 교육 피드백 생성

다음 Stage 및 엔딩은 AI가 결정하지 않는다.

---

## 2. Scenario → AI 입력

Backend는 현재 Stage 데이터를 AI에 전달한다.

필수 Stage 필드:

- stage_id
- stage_number
- title
- type
- location
- description
- messages
- question
- evaluation_axis
- evaluation_criteria
- next_stage

messages 구조:

```json
[
  {
    "speaker": "학생1",
    "text": "나 요즘 이거 먹고 공부하는데 잠이 하나도 안 온다."
  }
]
## 3. AI 출력
{
  "npc_response": "다들 먹었다는데 그렇게 위험할까?",
  "feedback": "알약의 출처와 안전성을 의심한 점이 좋아요.",
  "scores": {
    "risk_awareness": 3,
    "refusal": 0,
    "help_request": 0
  }
}
## 4. 금지사항

AI 출력에 다음 필드를 포함하지 않는다.

- next_stage
- ending
- branch
- new_stage

Stage 이동과 엔딩 결정은 Scenario와 Backend가 담당한다.
## 5. Stage 이동

Stage의 `next_stage` 값은 Scenario에서 정의한다.

예:

```json
{
  "next_stage": "EP01_STAGE02"
}