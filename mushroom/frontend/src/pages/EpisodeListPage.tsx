import manyangImg from "../assets/마냥_기본.png";

// =====================================================================
// EpisodeListPage (에피소드 선택 목록) — 라우트: "/episodes"
// ---------------------------------------------------------------------
// TutorialPage 다음에 오는 화면으로, 플레이할 에피소드(EP01~EP03)를
// 고르는 목록입니다. 카드를 클릭하면 /play/{episode.id}로 이동합니다.
//
// [Backend 연동 참고]
// - 아래 `episodes` 배열(제목/설명)은 프론트에 하드코딩된 화면 표시용
//   데이터입니다. Backend의 GET /api/episodes 같은 API는 아직 호출하지
//   만 화면에 보여줄 에피소드 목록(episodes 배열)이 코드 안에 직접 텍스트로 박혀 있는 하드코딩된 상태.
// - 다만 `episode.id`("EP01", "EP02", "EP03")는 실제로 Backend에
//   보내는 값과 동일한 규칙이에요. 이 화면 이후 PlayPage에서
//   POST /api/sessions 호출 시 body의 episode_id로 이 값이 그대로
//   전달되고, Backend는 이걸로 scenario/episodes/episode{번호}.json을
//   찾습니다. 즉 새 에피소드를 추가할 땐 이 id 값과 그 JSON 파일명이
//   반드시 일치해야 합니다.
// =====================================================================

interface EpisodeItem {
  id: string;
  num: string;
  title: string;
  description: string;
  locked: boolean;
}

// 하드코딩된 화면 표시용 데이터 (Backend API 응답 아님).
// id 값("EP01" 등)만 Backend와의 실제 계약이고, 나머지(num/title/
// description)는 순수 프론트 문구입니다.
const episodes: EpisodeItem[] = [
  {
    id: "EP01",
    num: "01",
    title: "시험기간 스터디 그룹",
    description: "공부 잘 된다는 약을 권유받으면?",
    locked: false,
  },
  {
    id: "EP02",
    num: "02",
    title: "SNS에서 시작된 유혹",
    description: "SNS에서 살 빠지는 약을 준다는 DM이 왔다면?",
    locked: false,
  },
  {
    id: "EP03",
    num: "03",
    title: "학원가에서 받은 음료",
    description: "학원가에서 낯선 사람이 무료 음료를 나눠준다면?",
    locked: false,
  },
];

function EpisodeListPage() {
  // 여기서는 세션을 만들지 않고 그냥 /play/{id}로 이동만 함.
  // 실제 POST /api/sessions 호출은 PlayPage 진입 시 일어남.
  const handleEpisodeClick = (id: string, locked: boolean) => {
    if (locked) return;
    window.location.assign(`/play/${id}`);
  };

  return (
    <main className="episode-list-page">
      <div className="episode-list-header">
        <div className="mascot">
          <img src={manyangImg} alt="마냥이" className="mascot-img" />
        </div>

        <div className="header-text">
          <p className="header-label">마냥이와 함께하는 거절 연습</p>
          <h1 className="header-title">
            오늘은 어떤 상황을
            <br />
            연습해볼까냥?
          </h1>
        </div>
      </div>

      <ul className="episode-list">
        {episodes.map((episode) => (
          <li key={episode.id}>
            <button
              type="button"
              className="episode-item"
              onClick={() => handleEpisodeClick(episode.id, episode.locked)}
              disabled={episode.locked}
            >
              <span className="episode-item-text">
                <span className="episode-item-num">
                  Episode {episode.num}
                </span>
                <strong className="episode-item-title">
                  {episode.title}
                </strong>
                <span className="episode-item-desc">
                  {episode.description}
                </span>
              </span>

              <span className="episode-item-arrow" aria-hidden="true">
                →
              </span>
            </button>
          </li>
        ))}
      </ul>

      <p className="episode-list-footer">청소년 마약 예방 교육 콘텐츠</p>
    </main>
  );
}

export default EpisodeListPage;
