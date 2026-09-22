# Scenario 데이터 규칙

## Episode

Scenario는 여러 개의 Episode로 구성한다.

각 Episode는 독립적인 Scenario 데이터 파일로 관리한다.

예시:

- EP01
- EP02
- EP03
- EP04
- EP05

Episode별 실제 Scenario 내용은 각 Episode JSON 파일에서 관리한다.

예시:

```text
scenario/
├── episodes/
│   ├── episode01.json
│   ├── episode02.json
│   ├── episode03.json
│   ├── episode04.json
│   └── episode05.json
├── rubrics/
│   ├── episode01-rubric.json
│   ├── episode02-rubric.json
│   ├── episode03-rubric.json
│   ├── episode04-rubric.json
│   └── episode05-rubric.json
└── branches/
    ├── episode01-branches.json
    ├── episode02-branches.json
    ├── episode03-branches.json
    ├── episode04-branches.json
    └── episode05-branches.json
```

Episode의 제목, Stage 구성, 대화 내용 등의 상세 정보는 해당 Episode JSON에서 정의한다.

---

## Stage 구조

각 Episode는 여러 개의 Stage로 구성한다.

기본적인 구조는 다음과 같다.

```text
{EPISODE_ID}_STAGE01
        ↓
{EPISODE_ID}_STAGE02
        ↓
{EPISODE_ID}_STAGE03
        ↓
...
{EPISODE_ID}_STAGE{N}
        ↓
RESULT
```

예를 들어 Episode가 `EP01`이라면:

```text
EP01_STAGE01
→ EP01_STAGE02
→ EP01_STAGE03
→ EP01_STAGE04
→ EP01_STAGE05
→ RESULT
```

Episode가 `EP02`라면:

```text
EP02_STAGE01
→ EP02_STAGE02
→ EP02_STAGE03
→ EP02_STAGE04
→ EP02_STAGE05
→ RESULT
```

각 Stage의 실제 제목과 내용은 Episode JSON에서 정의한다.

---

## Stage ID 규칙

Stage ID는 다음 형식을 사용한다.

```text
{EPISODE_ID}_STAGE{번호}
```

예시:

```text
EP01_STAGE01
EP01_STAGE02
EP02_STAGE01
EP02_STAGE02
```

Episode ID와 Stage ID는 반드시 일치해야 한다.

예를 들어 `EP02` Episode의 Stage라면:

```text
EP02_STAGE01
```

이어야 하며, 다른 Episode의 Stage ID를 사용하지 않는다.

---

## Stage 필수 데이터

각 Stage는 다음 데이터를 기본적으로 포함한다.

```text
stage_id
stage_number
title
messages
question
evaluation_axis
evaluation_criteria
next_stage
```

`next_stage`는 다음 Stage의 ID를 저장한다.

마지막 Stage의 `next_stage`는 `null`로 설정한다.

예시:

```json
{
  "stage_id": "EP01_STAGE01",
  "stage_number": 1,
  "title": "위험 인지",
  "next_stage": "EP01_STAGE02"
}
```

마지막 Stage:

```json
{
  "stage_id": "EP01_STAGE05",
  "stage_number": 5,
  "title": "최종 판단",
  "next_stage": null
}
```

---

## Stage 흐름 규칙

Episode의 핵심 Scenario 흐름은 반드시 Scenario 데이터에서 관리한다.

예시:

```text
STAGE01
→ STAGE02
→ STAGE03
→ STAGE04
→ STAGE05
→ RESULT
```

AI가 Scenario의 Stage 순서를 변경하거나 새로운 Stage를 생성하지 않는다.

`next_stage`는 Episode JSON에 정의된 값을 사용한다.

---

# 평가 점수

각 Stage의 사용자 응답은 `0~3점`으로 평가한다.

| 점수 | 의미 |
|---|---|
| 0 | 적절한 대응 없음 |
| 1 | 대응이 매우 약함 |
| 2 | 적절하지만 보완 필요 |
| 3 | 명확하고 적절한 대응 |

각 Stage의 평가 기준은 해당 Episode의 Rubric 파일에서 정의한다.

예시:

```text
rubrics/episode01-rubric.json
rubrics/episode02-rubric.json
...
```

---

# 결과 계산

각 Episode의 결과 점수는 해당 Episode에서 정의된 Stage 점수를 기반으로 계산한다.

현재 사용하는 평가 축은 다음과 같다.

### risk_awareness

위험 인지 관련 Stage의 점수를 기반으로 계산한다.

```text
Stage 점수 / 해당 Stage의 최대 점수 × 100
```

### refusal

거절 및 또래 압박 대응 관련 Stage의 점수를 기반으로 계산한다.

```text
관련 Stage 점수 합계 / 관련 Stage의 최대 점수 합계 × 100
```

### help_request

도움 요청 및 최종 판단 관련 Stage의 점수를 기반으로 계산한다.

```text
관련 Stage 점수 합계 / 관련 Stage의 최대 점수 합계 × 100
```

각 Episode에서 어떤 Stage가 어떤 평가 축에 해당하는지는 해당 Episode의 Rubric에서 정의한다.

따라서 Episode가 추가되거나 Stage 구성이 변경되어도 README의 계산식을 수정하지 않는다.

---

# AI 역할

AI는 다음 역할만 담당한다.

- 사용자 자유문장 평가
- NPC 후속 반응 생성
- 마냥이 피드백 생성
- Stage 점수 생성

AI는 Scenario의 핵심 흐름을 결정하지 않는다.

특히 AI가 다음 Stage를 직접 결정해서는 안 된다.

```text
AI → next_stage 결정 ❌
```

올바른 구조:

```text
Episode JSON
    ↓
next_stage 결정
    ↓
AI
    ↓
사용자 응답 평가 / NPC 반응 / 마냥이 피드백
```

`next_stage`는 항상 Scenario 데이터에 정의된 값을 사용한다.

---

# 개인정보

사용자의 자유문장 원문은 분석 DB에 영구 저장하지 않는다.

## 저장 가능

다음과 같은 최소한의 결과 데이터만 저장할 수 있다.

```text
session_id
episode_id
stage_id
score
axis
completed
```

## 영구 저장하지 않음

```text
사용자 자유문장 원문
```

사용자 응답의 원문은 Scenario 평가 및 AI 응답 생성에 사용할 수 있지만, 분석 DB에 영구 저장하지 않는다.

---

# Branch 규칙

각 Stage의 사용자 응답은 `0~3점`으로 평가한다.

| 점수 | Branch |
|---|---|
| 3 | high |
| 2 | medium |
| 0~1 | low |

Branch는 사용자 응답의 점수에 따라 **NPC 반응 및 마냥이 코칭을 선택하기 위한 용도**로 사용한다.

예시:

```text
사용자 응답
    ↓
AI 평가
    ↓
Score
    ↓
Branch 선택
    ├── high
    ├── medium
    └── low
    ↓
NPC 반응 / 마냥이 코칭
```

---

# Branch의 역할 제한

Branch는 NPC 반응과 마냥이 코칭을 선택하는 데만 사용한다.

Branch가 Episode의 핵심 Scenario 흐름을 변경해서는 안 된다.

잘못된 구조:

```text
사용자 응답
    ↓
AI 평가
    ↓
low
    ↓
다른 Stage로 이동 ❌
```

올바른 구조:

```text
사용자 응답
    ↓
AI 평가
    ↓
high / medium / low
    ↓
NPC 반응 및 마냥이 코칭 선택
    ↓
Episode JSON의 next_stage 사용
```

즉,

```text
Branch = 반응 선택
next_stage = Scenario 흐름 결정
```

으로 역할을 분리한다.

---

# Episode 확장 규칙

새로운 Episode를 추가할 때 기존 Scenario 규칙을 변경하지 않는다.

예를 들어 `EP06`을 추가한다면:

```text
episodes/episode06.json
rubrics/episode06-rubric.json
branches/episode06-branches.json
```

을 추가하고 다음과 같은 구조를 사용한다.

```text
EP06_STAGE01
→ EP06_STAGE02
→ ...
→ EP06_STAGE{N}
→ RESULT
```

Episode마다 Stage 수나 제목, 평가 축, Branch 내용은 달라질 수 있다.

단, 다음 원칙은 모든 Episode에 공통으로 적용한다.

1. Stage ID는 해당 Episode ID를 사용한다.
2. Stage 순서는 `next_stage`로 Scenario 데이터에서 관리한다.
3. AI가 `next_stage`를 결정하지 않는다.
4. Branch는 NPC 반응과 마냥이 코칭 선택에만 사용한다.
5. Stage 점수는 0~3점으로 평가한다.
6. 사용자 자유문장 원문은 분석 DB에 영구 저장하지 않는다.
7. Episode별 평가 기준은 해당 Episode의 Rubric에서 관리한다.

---

# 데이터 검증

각 Episode JSON과 Rubric은 검증 스크립트를 통해 구조를 확인한다.

검증 대상:

- Episode 기본 정보
- Stage 수
- Stage 필수 필드
- Stage ID 중복
- Stage 번호
- `next_stage` 연결
- 마지막 Stage의 `next_stage`
- Episode와 Rubric의 Stage 일치 여부

검증 스크립트는 특정 Episode에 고정하지 않고 실행 시 Episode ID를 전달할 수 있도록 구성한다.

예시:

```bash
python validate_episode.py
```

기본적으로 `EP01`을 검사한다.

특정 Episode 검사:

```bash
python validate_episode.py EP02
```

```bash
python validate_episode.py EP03
```

```bash
python validate_episode.py EP04
```

```bash
python validate_episode.py EP05
```

새로운 Episode가 추가되면 동일한 방식으로 검사할 수 있다.

---

# 핵심 원칙

Scenario 시스템의 역할을 다음과 같이 분리한다.

```text
┌─────────────────────────────┐
│       Scenario JSON         │
│                             │
│ Stage 순서                  │
│ next_stage                  │
│ 핵심 Scenario 흐름          │
└──────────────┬──────────────┘
               │
               ↓
┌─────────────────────────────┐
│             AI              │
│                             │
│ 사용자 응답 평가             │
│ 점수 생성                   │
│ NPC 반응                    │
│ 마냥이 피드백               │
└──────────────┬──────────────┘
               │
               ↓
┌─────────────────────────────┐
│           Branch            │
│                             │
│ high / medium / low         │
│ NPC 반응 선택               │
│ 마냥이 코칭 선택             │
└─────────────────────────────┘
```

핵심적으로 **Scenario의 흐름은 데이터가 결정하고, AI는 사용자 응답에 대한 평가와 반응을 담당한다.**

```text
Scenario 데이터
= 흐름 결정

AI
= 평가 및 반응

Branch
= 반응 선택
```