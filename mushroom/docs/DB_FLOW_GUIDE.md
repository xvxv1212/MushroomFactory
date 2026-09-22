# 마냥이 DB 연동용 실행 흐름 가이드

이 문서는 **웹페이지에서 마냥이를 실제로 실행하면서** 프론트 → FastAPI → AI → 현재 메모리 저장소까지 어떤 값이 이동하는지 DB 담당자가 빠르게 확인하기 위한 문서입니다.

## 1. 로그 보는 위치

### 프론트엔드
브라우저에서 `F12 → Console`을 엽니다.

예시:

```text
[FRONT-FLOW][IN] frontend/src/services/api.ts::createSession
[FRONT-FLOW][HTTP_IN] frontend/src/services/api.ts::apiFetch
[FRONT-FLOW][OUT] frontend/src/services/api.ts::createSession
```

### 백엔드
FastAPI를 실행한 VS Code 터미널을 봅니다.

예시:

```text
[FLOW][IN] backend/src/routes/chat.py::chat | {...}
[FLOW][LLM_RESULT] backend/src/services/ai_service.py::evaluate_response | {...}
[DB-CANDIDATE][SAVE_STAGE_RESULT] backend/src/routes/chat.py::chat | {...}
[FLOW][OUT] backend/src/routes/chat.py::chat | {...}
```

`[DB-CANDIDATE]`가 붙은 로그는 **현재 메모리에만 저장 중이지만 실제 DB 연동 시 INSERT/UPDATE/SELECT 후보가 되는 데이터**입니다.

---

## 2. 전체 실행 흐름

사용자가 `/play/EP01` 같은 학습 화면을 열면 대략 다음 순서로 흐릅니다.

```text
frontend/src/pages/PlayPage.tsx
  restoreOrCreateSession()
        ↓
frontend/src/services/api.ts
  createSession(episodeId)
        ↓ POST /api/sessions
backend/src/routes/sessions.py
  start_session()
        ↓
backend/src/core/scenario_engine.py
  load_episode()
        ↓
backend/src/core/session_store.py
  create_session()
        ↓
프론트에 session_id 반환
```

사용자가 답변을 입력하면:

```text
frontend/src/pages/PlayPage.tsx
  handleAnswer(message)
        ↓
frontend/src/services/api.ts
  sendChat(data)
        ↓ POST /api/chat
backend/src/routes/chat.py
  chat(request)
        ↓
backend/src/core/scenario_engine.py
  get_stage()
        ↓
backend/src/services/ai_service.py
  evaluate_response()
        ↓ OpenAI GPT
backend/src/routes/chat.py
  chat()
        ↓
backend/src/core/session_store.py
  apply_stage_result()
        ↓
프론트에 NPC 답변/피드백/점수/다음 Stage 반환
```

결과 화면으로 들어가면:

```text
frontend/src/pages/ResultPage.tsx
        ↓
frontend/src/services/api.ts
  getSessionResult(sessionId)
        ↓ GET /api/sessions/{session_id}/result
backend/src/routes/sessions.py
  session_result()
        ↓
backend/src/core/session_store.py
  get_result()
```

---

## 3. 파일별 함수 / 입력 / 출력 / DB 관점

| 경로 | 함수 | 주요 입력 | 주요 출력 | DB 담당 관점 |
|---|---|---|---|---|
| `frontend/src/services/api.ts` | `createSession()` | `episodeId` | `session_id`, `episode_id`, `current_stage` | 세션 생성 요청 |
| `backend/src/routes/sessions.py` | `start_session()` | `episode_id` | `session_id`, `current_stage` | 세션 INSERT 후보 |
| `backend/src/core/scenario_engine.py` | `load_episode()` | `episode_id` | episode JSON | 현재 시나리오는 JSON 파일 기반 |
| `frontend/src/services/api.ts` | `sendChat()` | `session_id`, `episode_id`, `stage_id`, `message` | NPC 답변, 피드백, 점수, 다음 stage | 채팅/평가 저장 요청 |
| `backend/src/routes/chat.py` | `chat()` | `ChatRequest` | `ChatResponse` | Stage 완료 시 저장 핵심 지점 |
| `backend/src/services/ai_service.py` | `evaluate_response()` | episode/stage/user message | GPT 평가 결과 | AI 결과 저장 전 단계 |
| `backend/src/core/session_store.py` | `apply_stage_result()` | session/stage/feedback/scores/next_stage | `True/False` | **현재 실제 저장 위치. DB 트랜잭션으로 교체하기 가장 중요** |
| `backend/src/routes/sessions.py` | `session_state()` | `session_id` | 현재 stage, 누적점수, 진행률 | 세션 SELECT 후보 |
| `backend/src/routes/sessions.py` | `session_result()` | `session_id` | 누적점수, stage 결과, 완료 여부 | 최종 결과 SELECT 후보 |
| `backend/src/routes/sessions.py` | `end_session()` | `session_id` | 삭제 성공 메시지 | DELETE 또는 종료 상태 UPDATE 후보 |
| `backend/src/database/connection.py` | `get_session()` | 없음 | SQLModel Session | 기존 관리자 CRUD가 쓰는 실제 PostgreSQL Session |

---

## 4. 현재 DB 담당자가 꼭 알아야 할 구조

### 학생 학습 데이터는 아직 PostgreSQL에 저장되지 않음

현재 학생용 학습 흐름인 `/api/sessions`, `/api/chat`은 `database/connection.py`의 `get_session()`을 사용하지 않습니다.

실제 저장 위치는:

```text
backend/src/core/session_store.py
MemorySessionStore._sessions
```

입니다.

즉 서버가 꺼지면 다음 데이터가 사라집니다.

```text
session_id
현재 stage
완료 stage 목록
stage별 feedback
stage별 scores
누적 scores
완료 여부
fallback 여부
```

### 시나리오도 DB가 아니라 JSON 파일

현재 에피소드/Stage 정보는:

```text
scenario/episodes/episode01.json
scenario/episodes/episode02.json
...
```

을 `scenario_engine.py`에서 읽습니다.

---

## 5. 기존 DB 모델과 현재 학습 데이터의 차이

현재 프로젝트에는 다음 모델이 있습니다.

```text
model/admin.py       -> Admin
model/llm_role.py    -> LlmRole
model/chat_room.py   -> ChatRoom
model/chatting.py    -> Chatting
model/score.py       -> Score
```

그런데 현재 학습 API의 데이터 구조와 바로 1:1로 대응되지는 않습니다.

특히 `Chatting` 모델에는 현재 **사용자/NPC 메시지 본문을 저장할 컬럼이 없습니다.** 현재 정의된 주요 값은 `chat_id`, `room_id`, `chatter`, `created_at`입니다.

또 현재 학습 흐름에는 다음 값이 필요하지만 기존 모델에는 직접 대응되는 컬럼/테이블이 부족합니다.

```text
episode_id
stage_id
feedback
next_stage
is_complete
analysis_available
fallback_mode
```

따라서 DB 담당자가 `MemorySessionStore` 데이터를 바로 기존 테이블에 억지로 넣기보다, **어떤 데이터를 영속 저장할지 먼저 팀 합의 후 스키마를 확장하는 것이 안전합니다.**

---

## 6. 한 번의 답변에서 DB 저장 후보 데이터

`backend/src/routes/chat.py::chat()`에서 아래 로그를 찾으면 됩니다.

```text
[DB-CANDIDATE][SAVE_STAGE_RESULT]
```

구조는 대략 다음과 같습니다.

```json
{
  "session_id": "...",
  "episode_id": "EP01",
  "stage_id": "EP01_STAGE1",
  "user_message": "<hidden len=...>",
  "npc_response": "...",
  "feedback": "...",
  "scores": {
    "risk_awareness": 2,
    "refusal": 0,
    "help_request": 0
  },
  "next_stage": "EP01_STAGE2",
  "analysis_available": true,
  "fallback_mode": false
}
```

이 데이터 묶음이 DB 저장 설계를 논의할 때 가장 보기 좋습니다.

---

## 7. 사용자 원문 로그 설정

기본 설정은 청소년의 자유 입력 문장을 터미널/브라우저 로그에 남기지 않습니다.

백엔드 `.env`:

```env
DB_FLOW_TRACE=1
DB_FLOW_TRACE_INCLUDE_MESSAGE=0
```

프론트 `frontend/.env`:

```env
VITE_FLOW_TRACE=1
VITE_FLOW_TRACE_INCLUDE_MESSAGE=0
```

로컬 테스트 데이터의 원문까지 꼭 확인해야 한다면 `...INCLUDE_MESSAGE=1`로 바꿀 수 있지만, 실제 사용자 환경에서는 `0`을 권장합니다.

---

## 8. 현재 코드에서 발견된 중복 라우트

현재 최신 파일 기준으로:

```text
backend/src/routes/sessions.py
backend/src/routes/episodes.py
```

두 파일이 거의 동일한 `/sessions` API를 가지고 있고, `app.py`에서 둘 다 `/api` prefix로 등록되어 있습니다.

그래서 FastAPI 실행 시 Route Map에 아래처럼 `DUPLICATE`가 표시될 수 있습니다.

```text
[ROUTE] POST /api/sessions -> routes.sessions.start_session
[ROUTE] POST /api/sessions -> routes.episodes.start_session <-- DUPLICATE
```

DB 연동 전에는 `episodes.py`의 역할을 정리하는 것이 좋습니다. 현재 이름은 episodes인데 내용은 session CRUD와 중복되어 있어 담당자에게 혼동을 줄 수 있습니다.
