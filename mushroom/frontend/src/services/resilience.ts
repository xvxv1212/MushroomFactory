import { episode01Stages } from "../data/episode01stages";
import { episode02Stages } from "../data/episode02stages";
import { episode03Stages } from "../data/episode03stages";
import type { GameStage } from "../data/episode01stages";
import type { ChatRequest, ChatResponse, Scores } from "../types/chat";
import type {
  SessionCreateResponse,
  SessionResultResponse,
  SessionStateResponse,
  StageResult,
} from "../types/session";

const STAGES_BY_EPISODE: Record<string, GameStage[]> = {
  EP01: episode01Stages,
  EP02: episode02Stages,
  EP03: episode03Stages,
};

const STORAGE_PREFIX = "manyang_resilient_session_";

export type ResilienceMode = "remote" | "fallback";

interface ResilientSession {
  session_id: string;
  episode_id: string;
  current_stage: string | null;
  completed_stages: string[];
  stage_results: StageResult[];
  scores: Scores;
  is_complete: boolean;
  mode: ResilienceMode;
  analysis_available: boolean;
}

const ZERO_SCORES: Scores = {
  risk_awareness: 0,
  refusal: 0,
  help_request: 0,
};

const INSUFFICIENT_INPUTS = new Set([
  "ㅇ", "ㅇㅇ", "응", "응응", "웅", "어", "네", "넵", "예",
  "ㅇㅋ", "오케이", "ok", "okay", "ㄴ", "ㄴㄴ", "몰라", "모름",
  "글쎄", "그냥", "아무거나", "음", "흠", "ㅋㅋ", "ㅋㅋㅋ",
  "ㅎㅎ", "ㅎㅎㅎ",
]);

function isInsufficientResponse(message: string) {
  const compact = message.trim().toLowerCase().replace(/\s+/g, "");

  if (!compact) return true;
  if (INSUFFICIENT_INPUTS.has(compact)) return true;

  return /^[ㅇㅋㅎㅠㅜㄴ.!?~]+$/.test(compact);
}


const FALLBACK_MEANINGFUL_MARKERS = [
  // 중요: '올바른 답' 목록이 아니라 '행동/판단 의도가 있는 답' 목록입니다.
  // 위험한 선택을 말해도 의미가 분명하면 평가/피드백을 받아야 합니다.

  // 거절 / 회피 / 안전 행동
  "싫", "안 먹", "먹지", "거절", "안 할", "하지 않", "필요 없",
  "그만", "됐어", "괜찮아", "자리", "떠날", "나갈", "피할", "차단",

  // 수락 / 위험한 선택도 의미 있는 대응
  "먹을래", "먹을게", "먹겠다", "먹어볼", "먹어 보", "먹어야",
  "써볼", "사용할", "해볼", "해 볼", "마실래", "마실게",
  "받을래", "받을게", "따라할", "같이 할", "나도 먹", "나만 먹",

  // 위험 인지
  "위험", "수상", "이상", "출처", "정체", "성분", "안전", "모르",
  "확인", "불분명", "의심", "걱정", "약", "알약", "사진", "포장",
  "처방", "약국", "병원", "믿", "문제",

  // 도움 요청
  "선생", "교사", "부모", "보호자", "어른", "상담", "신고", "도움",
  "119", "112", "보건", "알리", "말할", "말하", "연락", "구급", "도와",

  // 판단 / 행동 의사
  "아닌 것", "하지 말", "해야", "하겠", "할래", "할게",
  "생각", "같아", "보여", "왜", "좋아", "싫어",
];

function isFallbackMeaningfulResponse(message: string) {
  if (isInsufficientResponse(message)) return false;

  const text = message.trim().toLowerCase().replace(/\s+/g, " ");
  return FALLBACK_MEANINGFUL_MARKERS.some((marker) => text.includes(marker));
}

function storageKey(sessionId: string) {
  return `${STORAGE_PREFIX}${sessionId}`;
}

function createId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `local-${crypto.randomUUID()}`;
  }

  return `local-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function stagesFor(episodeId: string) {
  return STAGES_BY_EPISODE[episodeId] ?? [];
}

function findStage(episodeId: string, stageId: string) {
  return stagesFor(episodeId).find((stage) => stage.stageid === stageId);
}

function nextStageId(episodeId: string, stageId: string): string | null {
  const stages = stagesFor(episodeId);
  const index = stages.findIndex((stage) => stage.stageid === stageId);

  if (index < 0 || index >= stages.length - 1) {
    return null;
  }

  return stages[index + 1].stageid;
}

function fallbackFeedback(stage: GameStage): string {
  if (stage.scoreType.includes("위험")) {
    return (
      "출처·성분·안전성이 확인되지 않은 점을 먼저 살피는 게 핵심이야. " +
      "홍보 문구나 주변 사람의 말만 믿지 말고, 불분명하면 사용하지 않는 선택이 안전해."
    );
  }

  if (stage.scoreType.includes("거절")) {
    return (
      "권유를 받을 때는 ‘나는 안 할래’처럼 짧고 분명하게 말해도 괜찮아. " +
      "계속 압박한다면 대화를 끝내거나 그 자리를 벗어나는 것도 좋은 대응이야."
    );
  }

  return (
    "혼자 해결하려 하지 말고 보호자·교사·상담기관처럼 믿을 수 있는 어른에게 " +
    "상황을 알리는 선택이 중요해. 위험한 접촉은 이어가지 않는 게 좋아."
  );
}

function fallbackNpcResponse(stage: GameStage): string {
  if (stage.reaction) {
    return stage.reaction;
  }

  if (stage.scoreType.includes("거절")) {
    return "알겠어. 그래도 한 번만 더 생각해봐.";
  }

  if (stage.scoreType.includes("도움")) {
    return "굳이 다른 사람에게까지 말할 필요는 없잖아.";
  }

  return "다들 괜찮다고 하던데, 그렇게까지 신경 써야 해?";
}

function readSession(sessionId: string): ResilientSession | null {
  try {
    const raw = sessionStorage.getItem(storageKey(sessionId));
    return raw ? (JSON.parse(raw) as ResilientSession) : null;
  } catch {
    return null;
  }
}

function writeSession(session: ResilientSession) {
  sessionStorage.setItem(storageKey(session.session_id), JSON.stringify(session));
}

function createSessionRecord(
  episodeId: string,
  sessionId: string,
  mode: ResilienceMode,
  firstStage?: string | null
): ResilientSession {
  const first = firstStage ?? stagesFor(episodeId)[0]?.stageid ?? null;

  return {
    session_id: sessionId,
    episode_id: episodeId,
    current_stage: first,
    completed_stages: [],
    stage_results: [],
    scores: { ...ZERO_SCORES },
    is_complete: false,
    mode,
    analysis_available: mode === "remote",
  };
}

export function mirrorRemoteSession(response: SessionCreateResponse) {
  const existing = readSession(response.session_id);

  const record = existing ??
    createSessionRecord(
      response.episode_id,
      response.session_id,
      "remote",
      response.current_stage
    );

  record.current_stage = response.current_stage;
  record.mode = "remote";
  writeSession(record);
}

export function createFallbackSession(episodeId: string): SessionCreateResponse {
  const stages = stagesFor(episodeId);

  if (stages.length === 0) {
    throw new Error("아직 준비 중인 에피소드입니다.");
  }

  const sessionId = createId();
  const record = createSessionRecord(episodeId, sessionId, "fallback");
  record.analysis_available = false;
  writeSession(record);

  return {
    session_id: sessionId,
    episode_id: episodeId,
    current_stage: record.current_stage as string,
    fallback_mode: true,
    analysis_available: false,
  };
}

export function promoteSessionToFallback(sessionId: string): ResilientSession | null {
  const record = readSession(sessionId);

  if (!record) {
    return null;
  }

  record.mode = "fallback";
  record.analysis_available = false;
  writeSession(record);
  return record;
}

export function getResilienceMode(sessionId: string): ResilienceMode | null {
  return readSession(sessionId)?.mode ?? null;
}

export function isFallbackSession(sessionId: string) {
  return readSession(sessionId)?.mode === "fallback";
}

export function applyRemoteChatResult(
  request: ChatRequest,
  response: ChatResponse
) {
  const record = readSession(request.session_id);

  if (!record) {
    return;
  }

  // 재입력이 필요한 답변은 Stage 완료/점수/진행 상태에 절대 반영하지 않습니다.
  if (response.retry_required) {
    return;
  }

  // 서버가 안전 fallback으로 응답한 경우에도 이후 단계는 로컬 미러를
  // 기준으로 이어갈 수 있도록 degraded 상태를 기억합니다.
  if (response.fallback_mode || response.analysis_available === false) {
    record.mode = "fallback";
    record.analysis_available = false;
  }

  if (!record.completed_stages.includes(request.stage_id)) {
    record.completed_stages.push(request.stage_id);
    record.stage_results.push({
      stage_id: request.stage_id,
      feedback: response.feedback,
      scores: response.scores,
      analysis_available: response.analysis_available !== false,
    });

    record.scores.risk_awareness += response.scores.risk_awareness;
    record.scores.refusal += response.scores.refusal;
    record.scores.help_request += response.scores.help_request;
  }

  record.current_stage = response.next_stage;
  record.is_complete = response.is_episode_complete;
  writeSession(record);
}

export function createFallbackChat(request: ChatRequest): ChatResponse {
  let record = readSession(request.session_id);

  if (!record) {
    record = createSessionRecord(
      request.episode_id,
      request.session_id,
      "fallback",
      request.stage_id
    );
  }

  record.mode = "fallback";
  record.analysis_available = false;

  const stage = findStage(request.episode_id, request.stage_id);

  if (!stage) {
    throw new Error("현재 학습 단계를 찾을 수 없습니다.");
  }

  // Backend가 완전히 내려간 fallback 상황에서도 "ㅇㅇ", "ㅋㅋ" 같은 입력을
  // 정상 답변으로 간주해 다음 단계로 넘기지 않습니다.
  if (!isFallbackMeaningfulResponse(request.message)) {
    writeSession(record);

    return {
      npc_response:
        "응? 어떻게 하겠다는 건지 잘 모르겠어. 조금 더 구체적으로 말해줄래?",
      feedback:
        "현재 상황에서 무엇이 걱정되는지, 무엇을 하지 않을지, " +
        "또는 누구에게 도움을 요청할지 실제로 말하듯 표현해보세요.",
      scores: { ...ZERO_SCORES },
      next_stage: request.stage_id,
      is_episode_complete: false,
      fallback_mode: true,
      analysis_available: false,
      retry_required: true,
    };
  }

  const next = nextStageId(request.episode_id, request.stage_id);
  const feedback = fallbackFeedback(stage);
  const scores = { ...ZERO_SCORES };

  if (!record.completed_stages.includes(request.stage_id)) {
    record.completed_stages.push(request.stage_id);
    record.stage_results.push({
      stage_id: request.stage_id,
      feedback,
      scores,
      analysis_available: false,
    });
  }

  record.current_stage = next;
  record.is_complete = next === null;
  writeSession(record);

  // 사용자 입력 원문은 sessionStorage/localStorage 어느 곳에도 저장하지 않습니다.
  return {
    npc_response: fallbackNpcResponse(stage),
    feedback,
    scores,
    next_stage: next,
    is_episode_complete: next === null,
    fallback_mode: true,
    analysis_available: false,
    retry_required: false,
  };
}

export function getFallbackSessionState(sessionId: string): SessionStateResponse | null {
  const record = readSession(sessionId);

  if (!record) {
    return null;
  }

  const total = stagesFor(record.episode_id).length;
  const progress = total > 0
    ? Math.round((record.completed_stages.length / total) * 100)
    : 0;

  return {
    session_id: record.session_id,
    episode_id: record.episode_id,
    current_stage: record.current_stage,
    completed_stages: [...record.completed_stages],
    scores: { ...record.scores },
    progress,
    is_complete: record.is_complete,
    fallback_mode: record.mode === "fallback",
    analysis_available: record.analysis_available,
  };
}

export function getFallbackSessionResult(sessionId: string): SessionResultResponse | null {
  const record = readSession(sessionId);

  if (!record) {
    return null;
  }

  return {
    episode_id: record.episode_id,
    scores: { ...record.scores },
    stage_results: record.stage_results.map((stage) => ({
      ...stage,
      scores: { ...stage.scores },
    })),
    completed_stages: [...record.completed_stages],
    is_complete: record.is_complete,
    fallback_mode: record.mode === "fallback",
    analysis_available: record.analysis_available,
  };
}

export function deleteFallbackSession(sessionId: string) {
  sessionStorage.removeItem(storageKey(sessionId));
}
