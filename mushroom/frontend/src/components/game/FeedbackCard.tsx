import type {
  Scores
} from "../../types/chat";


interface FeedbackCardProps {
  scoreType: string;
  scores: Scores;
  limits: Scores;
}


export default function FeedbackCard({
  scoreType,
  scores,
  limits,
}: FeedbackCardProps) {

  const toPercent = (
    score: number,
    limit: number
  ) => {

    if (limit <= 0) {
      return 0;
    }

    return Math.min(
      100,
      Math.round(
        score / limit * 100
      )
    );
  };


  const risk =
    toPercent(
      scores.risk_awareness,
      limits.risk_awareness
    );

  const refusal =
    toPercent(
      scores.refusal,
      limits.refusal
    );

  const help =
    toPercent(
      scores.help_request,
      limits.help_request
    );


  return (
    <div className="feedback-card">

      <div className="evaluation-target">

        <div className="evaluation-target-label">

          <span className="evaluation-target-title">
            이번 단계 평가 영역
          </span>

          <strong className="evaluation-target-value">
            {scoreType}
          </strong>

        </div>

        <div className="evaluation-axes">

          <div className="mini-stat">
            <span className="mini-stat-label">
              위험 인지
            </span>

            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{
                  width: `${risk}%`,
                }}
              />
            </div>

            <span className="mini-stat-value">
              {risk}%
            </span>
          </div>


          <div className="mini-stat">
            <span className="mini-stat-label">
              거절 대응
            </span>

            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{
                  width: `${refusal}%`,
                }}
              />
            </div>

            <span className="mini-stat-value">
              {refusal}%
            </span>
          </div>


          <div className="mini-stat">
            <span className="mini-stat-label">
              도움 요청
            </span>

            <div className="mini-stat-track">
              <div
                className="mini-stat-fill"
                style={{
                  width: `${help}%`,
                }}
              />
            </div>

            <span className="mini-stat-value">
              {help}%
            </span>
          </div>

        </div>

      </div>

    </div>
  );
}
