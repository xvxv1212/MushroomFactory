import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import manyangResult from "../assets/마냥_홈 소개.png";

import { deleteSession, getSessionResult } from "../services/api";
import type { SessionResultResponse } from "../types/session";
import { scoreLimits } from "../data/scoreLimits";

// =====================================================================
// ResultPage (에피소드 결과 화면) — 라우트: "/result"
// ---------------------------------------------------------------------
// PlayPage에서 마지막 Stage를 끝내면 이동해오는 화면입니다. URL 쿼리
// 파라미터로 episodeId, sessionId를 받습니다.
//   예) /result?episodeId=EP01&sessionId=abcd-1234
//
//
// [Backend 연동 참고 — 이 페이지가 호출하는 API 3개]
//
// 1) GET /api/sessions/{sessionId}/result  (services/api.ts: getSessionResult)
//    - 진입 시 자동 호출. 응답 형태는 types/session.ts의
//      SessionResultResponse를 그대로 기대합니다.
//      { episode_id, scores: {risk_awareness, refusal, help_request},
//        stage_results: [{stage_id, feedback, scores}], completed_stages,
//        is_complete }
//    - sessionId가 URL에 없으면 이 API 자체를 호출하지 않고
//      "결과 정보를 찾을 수 없습니다" 에러만 보여줍니다.
//
// 2) DELETE /api/sessions/{sessionId}  (services/api.ts: deleteSession)
//    - "다시 도전하기" 버튼을 눌렀을 때만 호출됩니다. 실패해도
//      화면 흐름은 그대로 진행합니다(에러를 사용자에게 보여주지 않음).
//
// 3) (간접) PlayPage의 POST /api/sessions
//    - "다시 도전하기" / "다른 상황 연습하러 가기"를 누르면 브라우저의
//      sessionStorage에서 `manyang_session_{episodeId}` 키를 지운 뒤
//      이동합니다. 그래야 PlayPage가 재진입 시 이전 세션을 복구하지
//      않고 완전히 새 세션을 생성합니다. (아래 handleRetry 참고)
//
// [점수 % 계산 관련]
// scores는 원점수(정수)로 내려오는데, 화면에는 %로 보여줍니다.
// 항목별 만점은 Backend가 내려주는 게 아니라 프론트 `data/scoreLimits.ts`에
// 하드코딩되어 있어요 (현재 EP01~03 전부 위험 인지/거절 대응/도움 요청
// 각 3점 만점). Backend의 실제 채점 만점이 바뀌면 이 파일도 같이
// 맞춰줘야 퍼센트가 정확합니다.
// =====================================================================

function ResultPage() {
  const [searchParams] = useSearchParams();
  const episodeId = searchParams.get("episodeId") ?? "EP01";
  const sessionId = searchParams.get("sessionId");

  const [result, setResult] = useState<SessionResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(!!sessionId);
  const [errorMessage, setErrorMessage] = useState(
    sessionId ? "" : "결과 정보를 찾을 수 없습니다."
  );

  // "다시 도전하기"를 누른 뒤 DELETE 요청 + 이동이 끝날 때까지의
  // 짧은 처리 시간을 표시하기 위한 상태입니다. 이 상태가 true인
  // 동안은 아래 두 버튼을 모두 비활성화해서, 사용자가 여러 번
  // 클릭해 DELETE 요청이 중복으로 나가거나 페이지 이동이 꼬이는 걸
  // 막습니다. (실패해도 흐름은 그대로 진행하므로 별도 에러 처리는
  // 하지 않습니다 - handleRetry 내부 주석 참고)
  const [isRetrying, setIsRetrying] = useState(false);

  // fetchResult를 다시 호출할 수 있게 useEffect 밖으로 뺀 함수.
  // "결과 불러오기 실패 시 다시 시도" 버튼에서도 재사용합니다.
  const fetchResult = async (targetSessionId: string) => {
    try {
      setIsLoading(true);
      setErrorMessage("");

      // GET /api/sessions/{sessionId}/result 호출.
      // 응답 형태(SessionResultResponse)는 이 파일 상단 주석 참고.
      const data = await getSessionResult(targetSessionId);
      setResult(data);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "결과를 불러오지 못했습니다."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    let cancelled = false;

    async function loadResult() {
      try {
        setErrorMessage("");

        // GET /api/sessions/{sessionId}/result 호출 (진입 시 1회)
        const data = await getSessionResult(sessionId as string);

        if (!cancelled) {
          setResult(data);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            error instanceof Error
              ? error.message
              : "결과를 불러오지 못했습니다."
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadResult();

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  // "다시 불러오기" 버튼 핸들러 (getSessionResult 실패 시에만 노출).
  // useEffect 안의 loadResult와 로직이 거의 같지만, 매번 새
  // AbortController/cancelled 플래그를 만들 필요 없이 그냥
  // fetchResult를 재호출하면 됩니다 - 페이지를 벗어나지 않는 한
  // 이 화면에서 sessionId가 바뀔 일이 없기 때문입니다.
  const handleRetryFetch = () => {
    if (sessionId) {
      fetchResult(sessionId);
    }
  };

  const handleRetry = async () => {
    if (isRetrying) {
      return;
    }

    setIsRetrying(true);

    const targetEpisodeId = result?.episode_id ?? episodeId;

    if (sessionId) {
      try {
        // DELETE /api/sessions/{sessionId} — 지금 끝난 세션을 지움.
        // 실패해도(이미 지워졌거나 네트워크 오류) 사용자에게 에러를
        // 보여주지 않고 그냥 새로 시작하는 흐름을 계속 진행합니다.
        // 이 세션은 어차피 결과 화면까지 온 "끝난" 세션이라, 삭제가
        // 안 되더라도 사용자 경험상 치명적이지 않기 때문입니다.
        await deleteSession(sessionId);
      } catch {
        // 삭제 실패해도 새로 시작하는 흐름은 계속 진행
      }
    }

    // 브라우저에 남아있는 "이 에피소드의 마지막 세션" 기록을 지웁니다.
    // 이걸 안 지우면 PlayPage가 재진입 시 방금 끝난(완료된) 세션을
    // 그대로 복구해버려서, "다시 도전하기"를 눌러도 새 시도가 아니라
    // 이미 끝난 결과 화면으로 다시 돌아오는 것처럼 보일 수 있습니다.
    sessionStorage.removeItem(`manyang_session_${targetEpisodeId}`);

    window.location.assign(`/play/${targetEpisodeId}`);
  };

  const handleGoToEpisodes = () => {
    sessionStorage.removeItem(`manyang_session_${episodeId}`);

    window.location.assign("/episodes");
  };

  const limits =
    scoreLimits[result?.episode_id ?? episodeId] ??
    scoreLimits.EP01;

  const analysisAvailable = result?.analysis_available !== false;

  const toPercent = (value: number, limit: number) => {
    if (limit <= 0) {
      return 0;
    }

    return Math.min(100, Math.round((value / limit) * 100));
  };

  const statItems = result && analysisAvailable
    ? [
        {
          key: "riskAwareness",
          label: "위험 인지",
          value: toPercent(result.scores.risk_awareness, limits.risk_awareness),
        },
        {
          key: "refusal",
          label: "거절 대응",
          value: toPercent(result.scores.refusal, limits.refusal),
        },
        {
          key: "helpRequest",
          label: "도움 요청",
          value: toPercent(result.scores.help_request, limits.help_request),
        },
      ]
    : [];

  return (
    <main className="result-page">
      <div className="result-hero">
        <div className="home-character-box">
          <img
            src={manyangResult}
            alt="마냥이 캐릭터"
            className="home-character-img"
          />
        </div>

        <div className="home-bubble home-bubble--right">
          <p>
            수고했다냥! Episode를 무사히 마쳤다옹.
            <br />
            오늘 연습한 대응, 실제 상황에서도 꼭 기억해두자냥.
          </p>
        </div>
      </div>

      {isLoading && <p className="result-loading">결과를 불러오는 중이에요...</p>}

      {/* getSessionResult 실패 시: 에러 문구 + 재시도 버튼.
          sessionId 자체가 없는 경우(URL에 쿼리파라미터 누락)에도
          같은 자리에 안내가 뜨지만, 그때는 sessionId가 없어서
          재시도해도 의미가 없으므로 버튼을 숨깁니다. */}
      {errorMessage && (
        <div className="api-error">
          <p>{errorMessage}</p>

          {sessionId && (
            <button
              type="button"
              className="api-error-retry"
              onClick={handleRetryFetch}
              disabled={isLoading}
            >
              다시 불러오기
            </button>
          )}
        </div>
      )}

      {/* result.is_complete는 Backend가 "이 세션이 마지막 Stage까지
          끝난 상태인지"를 알려주는 값입니다. false인데도 이 화면에
          왔다는 건 - 예를 들어 사용자가 URL을 직접 조작했거나, 진행
          중간에 북마크해둔 결과 링크로 돌아온 경우 - 지금 보여주는
          점수/피드백이 "최종 결과"가 아니라 "지금까지의 중간 기록"일
          수 있다는 뜻이라, 그 사실을 명확히 알려줍니다. */}
      {result && !result.is_complete && (
        <div className="result-incomplete-banner">
          ⚠️ 아직 이 에피소드를 끝까지 진행하지 않은 상태예요. 지금까지
          진행한 기록만 보여드릴게요.
        </div>
      )}

      {result && (
        <>
          {!analysisAvailable && (
            <section className="result-fallback-card" aria-label="기본 학습 모드 결과">
              <strong>기본 학습 모드로 끝까지 완료했어요.</strong>
              <p>
                서버 또는 AI 연결이 일시적으로 불안정해 검수된 시나리오와
                코칭으로 학습을 진행했습니다. 이 경우 숫자 점수는 정확한 AI
                평가가 아니므로 표시하지 않습니다.
              </p>
            </section>
          )}

          {analysisAvailable && (
          <section className="result-stats">
            <p className="result-stats-title">오늘의 기록</p>

            {/* completed_stages: Backend가 실제로 완료 처리한 Stage id
                목록입니다. 몇 단계나 진행했는지 요약해서 보여줍니다. */}
            <p className="result-stats-subtitle">
              총 {result.completed_stages.length}개 단계 완료
            </p>

            {statItems.map((item) => (
              <div className="result-stat" key={item.key}>
                <span className="result-stat-label">{item.label}</span>

                <div className="result-stat-track">
                  <div
                    className="result-stat-fill"
                    style={{ width: `${item.value}%` }}
                  />
                </div>

                <span className="result-stat-value">{item.value}%</span>
              </div>
            ))}
          </section>
          )}

          {result.stage_results.length > 0 && (
            <section className="result-stage-feedback">
              <p className="result-stats-title">단계별 마냥이 피드백</p>

              {result.stage_results.map((stage) => (
                <div className="result-stage-item" key={stage.stage_id}>
                  <strong>{stage.stage_id}</strong>
                  <p>{stage.feedback}</p>

                  {/* stage.scores: 이 Stage 하나에서 받은 원점수(각
                      0~3점, Backend StageScores 기준)입니다. 위쪽
                      "오늘의 기록"이 전체 Stage 누적 총점이라면, 이건
                      "이 한 Stage에서 어느 항목을 얼마나 잘했는지"를
                      보여줍니다. */}
                  {analysisAvailable && stage.analysis_available !== false && (
                    <div className="result-stage-scores">
                      <span>위험 인지 {stage.scores.risk_awareness}</span>
                      <span>거절 대응 {stage.scores.refusal}</span>
                      <span>도움 요청 {stage.scores.help_request}</span>
                    </div>
                  )}
                </div>
              ))}
            </section>
          )}
        </>
      )}

      <div className="result-actions">
        {/* isRetrying인 동안 두 버튼을 모두 막습니다 - "다시
            도전하기"만 막으면, 그 사이 "다른 상황 연습하러 가기"를
            눌러 DELETE 요청이 끝나기 전에 다른 페이지로 넘어가
            버리는 애매한 상태를 방지할 수 있습니다. */}
        <button
          type="button"
          className="home-start-button"
          onClick={handleRetry}
          disabled={isRetrying}
        >
          {isRetrying ? "처리 중..." : "다시 도전하기"}
        </button>

        <button
          type="button"
          className="home-start-button home-start-button--outline"
          onClick={handleGoToEpisodes}
          disabled={isRetrying}
        >
          다른 상황 연습하러 가기
        </button>
      </div>

      <footer className="home-footer">
        <p>
          청소년 상담전화 <strong>1388</strong> · 마약류 중독관리센터{" "}
          <strong>1899-0893</strong>
        </p>
      </footer>
    </main>
  );
}

export default ResultPage;
