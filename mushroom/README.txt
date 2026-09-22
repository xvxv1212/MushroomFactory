Git 사용 규칙

작업 시작 전에 항상:
git checkout main
git pull origin main



자기 Branch 이동:
git checkout feature/game-ui


작업 완료 후:
git add .
git commit -m "feat: NPC 대화 화면 구현"
git push origin feature/game-ui



GitHub에서:
feature/game-ui
      ↓
Pull Request
      ↓
main

Merge합니다.


## 📁 Frontend 폴더 구조 및 역할

프로젝트는 Vite + React + TypeScript 기반으로 구성되어 있습니다.

```text
frontend/
└─ src/
   ├─ assets/
   ├─ components/
   │  ├─ common/
   │  ├─ episode/
   │  └─ game/
   ├─ pages/
   ├─ services/
   ├─ types/
   ├─ data/
   ├─ App.tsx
   ├─ App.css
   ├─ index.css
   └─ main.tsx
src/pages

하나의 전체 화면(Page)을 담당합니다.

예:

HomePage.tsx : 홈 화면
TutorialPage.tsx : 마냥이 튜토리얼
EpisodeListPage.tsx : 에피소드 선택
PlayPage.tsx : NPC 대화 및 게임 진행
ResultPage.tsx : 에피소드 결과
ProfilePage.tsx : 대응능력 프로필

규칙

새로운 화면을 만들 때는 pages에 생성합니다.
여러 페이지에서 재사용하는 UI는 여기에 만들지 않고 components에 만듭니다.
src/components

페이지 안에서 반복해서 사용하는 UI 컴포넌트를 관리합니다.

components/common

여러 화면에서 공통으로 사용하는 UI

예:

Header.tsx
Button.tsx
ProgressBar.tsx
components/episode

에피소드 관련 UI

예:

EpisodeCard.tsx
components/game

게임 진행 화면에서 사용하는 UI

예:

NPCBubble.tsx
UserInput.tsx
ManyangCoach.tsx
FeedbackCard.tsx
src/services

Frontend와 Backend의 통신을 담당합니다.

예:

api.ts

FastAPI 서버 호출, Chat API, Episode API 등의 코드를 이곳에서 관리합니다.

규칙

페이지 안에 직접 fetch()를 반복해서 작성하지 않습니다.
API 호출 코드는 가급적 services에 모읍니다.
src/types

TypeScript 데이터 타입을 관리합니다.

예:

episode.ts
chat.ts

Episode, ChatResponse, Scores 등 Frontend에서 공통으로 사용하는 데이터 구조를 정의합니다.

src/data

Backend가 완성되기 전 사용하는 Mock 데이터를 관리합니다.

예:

mockEpisodes.ts

현재는 EP01 개발 및 화면 테스트에 사용하고,
추후 Backend API 연결 후 실제 데이터로 교체합니다.

src/assets

이미지, 아이콘, 캐릭터 파일을 관리합니다.

assets/
├─ images/
├─ icons/
└─ characters/

예:

마냥이 캐릭터 이미지 → characters
배경 이미지 → images
버튼/상태 아이콘 → icons
📌 주요 파일
main.tsx

React 애플리케이션의 시작점입니다.

일반적으로 수정할 일이 많지 않습니다.

App.tsx

전체 페이지 Route를 관리합니다.

예:

/
→ /tutorial
→ /episodes
→ /play/EP01
→ /result
→ /profile

새로운 페이지 URL을 추가할 경우 App.tsx의 Router도 수정해야 합니다.

⚠️ 팀 개발 규칙
한 페이지 전체 → pages
재사용 UI → components
Backend 통신 → services
TypeScript 데이터 구조 → types
임시 테스트 데이터 → data
이미지/캐릭터 → assets
다른 담당자의 파일을 크게 수정하기 전에 팀에 공유
기능별 Branch에서 작업 후 Pull Request
node_modules는 GitHub에 올리지 않음
API 구조 변경 시 Frontend/Backend 담당자 모두에게 공유

이 설명을 README에 넣어두면 특히 `pages = 화면`, `components = 화면 속 부품`, `services = 서버 통신`, `data = 임시 데이터`라는 기준이 명확해집니다. 기존 답변에서도 이 구분을 같은 방식으로 잡고 있습니다. :contentReference[oaicite:1]{index=1}

그리고 **폴더 역할만 적는 것보다 README에 3가지를 더 넣는 걸 권합니다.** `프로젝트 실행 방법`, `브랜치/커밋 규칙`, `현재 개발 우선순위`입니다. 그렇게 해두면 새 팀원이 README 하나만 읽고도 바로 작업을 시작할 수 있습니다.

예를 들어 맨 위에는 이것도 넣으세요.

```markdown
## 🚀 Frontend 실행 방법

```bash
cd frontend
npm install
npm run dev

브라우저에서 터미널에 표시되는 Local 주소로 접속합니다.

예:
http://localhost:5173


현재 단계라면 README를 단순 소개 문서가 아니라 **팀 개발 규칙서**처럼 만드는 게 좋습니다.
