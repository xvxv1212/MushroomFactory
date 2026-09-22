export interface ChatRequest {
  session_id: string;
  episode_id: string;
  stage_id: string;
  message: string;
}

export interface Scores {
  risk_awareness: number;
  refusal: number;
  help_request: number;
}

export interface ChatResponse {
  npc_response: string;
  feedback: string;

  scores: Scores;

  next_stage: string | null;

  is_episode_complete: boolean;

  // true면 FastAPI/AI 장애로 검수된 로컬/서버 fallback 응답을 사용 중입니다.
  fallback_mode?: boolean;

  // false면 숫자 점수는 신뢰 가능한 AI 평가 결과가 아니므로 결과 화면에서 숨깁니다.
  analysis_available?: boolean;

  // true면 현재 입력은 평가 가능한 답변이 아니므로 같은 Stage에서 다시 입력합니다.
  retry_required?: boolean;
}
