import type { Scores } from "./chat";


export interface SessionCreateRequest {
  episode_id: string;
}


export interface SessionCreateResponse {
  session_id: string;
  episode_id: string;
  current_stage: string;
  fallback_mode?: boolean;
  analysis_available?: boolean;
}


export interface SessionStateResponse {
  session_id: string;
  episode_id: string;

  current_stage: string | null;

  completed_stages: string[];

  scores: Scores;

  progress: number;

  is_complete: boolean;

  fallback_mode?: boolean;
  analysis_available?: boolean;
}


export interface StageResult {
  stage_id: string;
  feedback: string;
  scores: Scores;
  analysis_available?: boolean;
}


export interface SessionResultResponse {
  episode_id: string;

  scores: Scores;

  stage_results: StageResult[];

  completed_stages: string[];

  is_complete: boolean;

  fallback_mode?: boolean;
  analysis_available?: boolean;
}
