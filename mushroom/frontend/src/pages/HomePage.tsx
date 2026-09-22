import manyangSitting from "../assets/마냥_기본.png";
import manyangLying from "../assets/마냥_홈 소개.png";

// =====================================================================
// HomePage (첫 화면) — 라우트: "/"
// ---------------------------------------------------------------------
// 사이트에 처음 들어왔을 때 가장 먼저 보이는 화면입니다.
// 사용자가 제공한 와이어프레임 이미지의 4단 구조를 그대로 따라 만들었습니다.
//
//   1) home-header  : 좌측 상단 로고 아이콘 + 서비스명
//   2) home-hero     : (왼쪽) 마냥이 캐릭터 이미지 /
//                       (오른쪽) 말풍선 형태의 캐릭터 소개
//   3) home-cta      : (왼쪽) 말풍선 형태의 시작 유도 문구 + 버튼 /
//                       (오른쪽) 마냥이 캐릭터 이미지
//   4) home-footer   : 마약 관련 전문기관 안내(전화번호 등)
//
// 각 섹션의 실제 문구/이미지 배치는 팀 논의에 따라 자유롭게 바꿔도
// 되도록 구조와 클래스명을 최대한 단순하게 유지했습니다.
// (스타일은 frontend/src/index.css 안의 "Home page" 섹션에 있습니다.)
//
// [Backend 연동 참고]
// 이 페이지는 Backend API를 전혀 호출하지 않습니다. 순수 정적 화면이고,
// "시작하기" 버튼을 누르면 세션/사용자 정보 없이 그냥 /tutorial로
// 이동만 합니다. (실제 세션 생성은 PlayPage 진입 시 처음 일어납니다.)
// =====================================================================

function HomePage() {
  // "시작하기" 버튼을 누르면 기존 온보딩 플로우(TutorialPage)로 이동합니다.
  const handleStart = () => {
    window.location.href = "/tutorial";
  };

  return (
    <main className="home-page">
      {/* home-content: 헤더+캐릭터 소개+시작 유도를 한 덩어리로 묶어서
          화면(뷰포트) 안에서 세로로 가운데 정렬되게 합니다. 하단 안내
          문구(home-footer)는 이 블록 밖에서 항상 맨 아래에 붙습니다. */}
      <div className="home-content">
      {/* =====================================================
          1) 상단 헤더 : 로고 아이콘 + 서비스명
          - 모든 페이지 상단에 공통으로 뜨는 <Header /> (App.tsx)로
            분리되어 이제 이 페이지에서는 따로 렌더링하지 않습니다.
      ===================================================== */}

      {/* =====================================================
          2) 캐릭터 소개 섹션 (와이어프레임 2번째 줄)
          - home-character-box : 캐릭터 이미지를 담는 카드.
            지금은 "마냥_기본.png"(앉아서 손을 든 포즈)를 사용합니다.
          - home-bubble--right : 캐릭터 오른쪽에 붙는 말풍선.
            꼬리(tail)가 왼쪽(캐릭터 쪽)을 향하도록 CSS로 처리했습니다.
          - 말풍선 안 문구는 자리 표시용 초안입니다. 실제 캐릭터
            소개 카피가 정해지면 <p> 내용만 바꾸면 됩니다.
      ===================================================== */}
      <section className="home-hero">
        <div className="home-character-box">
          <img
            src={manyangSitting}
            alt="마냥이 캐릭터"
            className="home-character-img"
          />
        </div>

        <div className="home-bubble home-bubble--right">
          {/* TODO: 실제 캐릭터 소개 카피로 교체 */}
          <p>
            안녕하냥, 나는 마냥이다옹! 위험한 순간, 거절하기 어려운 순간에
            너와 함께 연습할거다냥. 실제 대화처럼 다양한 상황을 겪어보면서
            나를 지키는 방법을 같이 배워보자냥.
          </p>
        </div>
      </section>

      {/* =====================================================
          3) 시작 유도 섹션 (와이어프레임 3번째 줄)
          - home-bubble--left : 시작 유도 문구 + 버튼이 들어가는
            말풍선. 꼬리가 오른쪽(캐릭터 쪽)을 향합니다.
          - home-start-button : 실제 이동 로직은 위쪽 handleStart
            함수에서 관리합니다. 지금은 /tutorial로 이동합니다.
          - home-character-box : 두 번째 캐릭터 이미지 카드.
            "마냥_홈 소개.png"(누워서 쉬는 포즈)를 사용해 첫 번째
            섹션과 다른 포즈로 변화를 줬습니다.
      ===================================================== */}
      <section className="home-cta">
        <div className="home-bubble home-bubble--left">
          {/* TODO: 실제 시작 유도 카피로 교체 */}
          <p>오늘은 어떤 상황을 함께 연습해볼까냥?</p>

          <button
            type="button"
            className="home-start-button"
            onClick={handleStart}
          >
            시작하기
          </button>
        </div>

        <div className="home-character-box">
          <img
            src={manyangLying}
            alt="마냥이 캐릭터"
            className="home-character-img"
          />
        </div>
      </section>
      </div>

      {/* =====================================================
          4) 하단 안내 섹션 (와이어프레임 마지막 줄)
          - 마약 관련 전문기관 연락처를 안내하는 영역입니다.
      ===================================================== */}
      <footer className="home-footer">
        {/* TODO: 실제 검증된 기관명 · 전화번호로 교체 완료 */}
        <p>
          청소년 사이버상담센터 <strong>1388</strong> · 24시 마약류 상담센터{" "}
          <strong>1899-0893</strong> · 한국마약퇴치운동본부{" "}
          <strong>1342-1342</strong>
        </p>
      </footer>
    </main>
  );
}

export default HomePage;
