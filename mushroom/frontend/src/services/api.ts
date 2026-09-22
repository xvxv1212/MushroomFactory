import type {
  ChatRequest,
  ChatResponse,
} from "../types/chat";

import type {
  SessionCreateResponse,
  SessionStateResponse,
  SessionResultResponse,
} from "../types/session";

import {
  applyRemoteChatResult,
  createFallbackChat,
  createFallbackSession,
  deleteFallbackSession,
  getFallbackSessionResult,
  getFallbackSessionState,
  isFallbackSession,
  mirrorRemoteSession,
  promoteSessionToFallback,
} from "./resilience";

/*
 * =====================================================================
 * DB/백엔드 담당 실행 흐름 확인
 * ---------------------------------------------------------------------
 * 브라우저 개발자도구(F12) > Console에서 아래 형식의 로그를 볼 수 있습니다.
 *
 * [FRONT-FLOW][IN]  frontend/src/services/api.ts::sendChat {...}
 * [FRONT-FLOW][HTTP] frontend/src/services/api.ts::apiFetch {...}
 * [FRONT-FLOW][OUT] frontend/src/services/api.ts::sendChat {...}
 *
 * 사용자 입력 message는 기본적으로 원문을 숨기고 길이만 표시합니다.
 * 로컬 테스트에서 꼭 원문이 필요할 때만 frontend/.env에
 * VITE_FLOW_TRACE_INCLUDE_MESSAGE=1 을 설정하세요.
 * =====================================================================
 */

const FLOW_TRACE = (import.meta.env.VITE_FLOW_TRACE ?? "1") !== "0";
const FLOW_TRACE_INCLUDE_MESSAGE =
  (import.meta.env.VITE_FLOW_TRACE_INCLUDE_MESSAGE ?? "0") === "1";

function sanitizeTrace(value: unknown, key = ""): unknown {
  const normalizedKey = key.toLowerCase();

  if (
    ["password", "api_key", "apikey", "token", "authorization", "secret"].includes(
      normalizedKey
    )
  ) {
    return "<redacted>";
  }

  if (
    ["message", "user_message"].includes(normalizedKey) &&
    typeof value === "string" &&
    !FLOW_TRACE_INCLUDE_MESSAGE
  ) {
    return `<hidden len=${value.length}>`;
  }

  if (Array.isArray(value)) {
    return value.map((item) => sanitizeTrace(item));
  }

  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([childKey, childValue]) => [
        childKey,
        sanitizeTrace(childValue, childKey),
      ])
    );
  }

  return value;
}

function traceApi(
  functionName: string,
  event: string,
  data?: unknown
) {
  if (!FLOW_TRACE) return;

  console.log(
    `[FRONT-FLOW][${event}] frontend/src/services/api.ts::${functionName}`,
    sanitizeTrace(data)
  );
}

/*
 * 개발 중에는 Vite가 /api 요청을 127.0.0.1:8000으로 프록시합니다.
 * Backend 또는 DB/AI 일부가 장애여도 학생 학습 흐름이 멈추지 않도록
 * 각 API 함수는 검수된 frontend fallback으로 자동 전환합니다.
 */
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "/api"
).replace(/\/$/, "");

async function apiFetch(
  path: string,
  init?: RequestInit,
  timeoutMs = 4000
): Promise<Response> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  const method = init?.method ?? "GET";

  traceApi("apiFetch", "HTTP_IN", {
    method,
    path: `${API_BASE_URL}${path}`,
    timeoutMs,
  });

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
    });

    traceApi("apiFetch", "HTTP_OUT", {
      method,
      path: `${API_BASE_URL}${path}`,
      status: response.status,
      ok: response.ok,
    });

    return response;
  } catch (error) {
    traceApi("apiFetch", "HTTP_ERROR", {
      method,
      path: `${API_BASE_URL}${path}`,
      error: error instanceof Error ? error.message : String(error),
    });
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function sendChat(
  data: ChatRequest
): Promise<ChatResponse> {
  traceApi("sendChat", "IN", data);

  if (isFallbackSession(data.session_id)) {
    const fallback = createFallbackChat(data);
    traceApi("sendChat", "OUT_LOCAL_FALLBACK", fallback);
    return fallback;
  }

  try {
    const response = await apiFetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }, 22000);

    if (!response.ok) {
      throw new Error("CHAT_API_UNAVAILABLE");
    }

    const result = (await response.json()) as ChatResponse;
    applyRemoteChatResult(data, result);
    traceApi("sendChat", "OUT", result);
    return result;
  } catch (error) {
    traceApi("sendChat", "FALLBACK", {
      session_id: data.session_id,
      error: error instanceof Error ? error.message : String(error),
    });

    promoteSessionToFallback(data.session_id);
    const fallback = createFallbackChat(data);
    traceApi("sendChat", "OUT_LOCAL_FALLBACK", fallback);
    return fallback;
  }
}

export async function createSession(
  episodeId: string
): Promise<SessionCreateResponse> {
  traceApi("createSession", "IN", {
    episode_id: episodeId,
  });

  try {
    const response = await apiFetch("/sessions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        episode_id: episodeId,
      }),
    }, 3500);

    if (!response.ok) {
      throw new Error("SESSION_API_UNAVAILABLE");
    }

    const result = (await response.json()) as SessionCreateResponse;
    mirrorRemoteSession(result);
    traceApi("createSession", "OUT", result);
    return result;
  } catch (error) {
    traceApi("createSession", "FALLBACK", {
      episode_id: episodeId,
      error: error instanceof Error ? error.message : String(error),
    });

    const fallback = createFallbackSession(episodeId);
    traceApi("createSession", "OUT_LOCAL_FALLBACK", fallback);
    return fallback;
  }
}

export async function getSessionState(
  sessionId: string
): Promise<SessionStateResponse> {
  traceApi("getSessionState", "IN", {
    session_id: sessionId,
  });

  if (isFallbackSession(sessionId)) {
    const localState = getFallbackSessionState(sessionId);
    if (localState) {
      traceApi("getSessionState", "OUT_LOCAL_FALLBACK", localState);
      return localState;
    }
  }

  try {
    const response = await apiFetch(`/sessions/${sessionId}`, undefined, 3500);

    if (!response.ok) {
      throw new Error("SESSION_STATE_UNAVAILABLE");
    }

    const result = (await response.json()) as SessionStateResponse;
    traceApi("getSessionState", "OUT", result);
    return result;
  } catch (error) {
    traceApi("getSessionState", "FALLBACK", {
      session_id: sessionId,
      error: error instanceof Error ? error.message : String(error),
    });

    const fallback = promoteSessionToFallback(sessionId);
    const localState = fallback ? getFallbackSessionState(sessionId) : null;

    if (localState) {
      traceApi("getSessionState", "OUT_LOCAL_FALLBACK", localState);
      return localState;
    }

    throw new Error("진행 상태를 복구하지 못했습니다.");
  }
}

export async function getSessionResult(
  sessionId: string
): Promise<SessionResultResponse> {
  traceApi("getSessionResult", "IN", {
    session_id: sessionId,
  });

  if (isFallbackSession(sessionId)) {
    const localResult = getFallbackSessionResult(sessionId);
    if (localResult) {
      traceApi("getSessionResult", "OUT_LOCAL_FALLBACK", localResult);
      return localResult;
    }
  }

  try {
    const response = await apiFetch(
      `/sessions/${sessionId}/result`,
      undefined,
      3500
    );

    if (!response.ok) {
      throw new Error("SESSION_RESULT_UNAVAILABLE");
    }

    const result = (await response.json()) as SessionResultResponse;
    traceApi("getSessionResult", "OUT", result);
    return result;
  } catch (error) {
    traceApi("getSessionResult", "FALLBACK", {
      session_id: sessionId,
      error: error instanceof Error ? error.message : String(error),
    });

    const localResult = getFallbackSessionResult(sessionId);

    if (localResult) {
      traceApi("getSessionResult", "OUT_LOCAL_FALLBACK", localResult);
      return localResult;
    }

    throw new Error("결과 정보를 불러오지 못했습니다.");
  }
}

export async function deleteSession(
  sessionId: string
): Promise<void> {
  traceApi("deleteSession", "IN", {
    session_id: sessionId,
  });

  deleteFallbackSession(sessionId);

  if (sessionId.startsWith("local-")) {
    traceApi("deleteSession", "OUT_LOCAL_ONLY", {
      session_id: sessionId,
    });
    return;
  }

  try {
    const response = await apiFetch(`/sessions/${sessionId}`, {
      method: "DELETE",
    }, 2500);

    traceApi("deleteSession", "OUT", {
      session_id: sessionId,
      status: response.status,
      ok: response.ok,
    });
  } catch (error) {
    traceApi("deleteSession", "DELETE_FAILED_BEST_EFFORT", {
      session_id: sessionId,
      error: error instanceof Error ? error.message : String(error),
    });
  }
}
