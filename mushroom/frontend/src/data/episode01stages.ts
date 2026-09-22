export interface DialogueMessage {
  sender: string;
  text: string;
  // 지정하면 텍스트 대신 이미지로 표시 (Instagram DM 연출용)
  // "product": 상품 사진(DietPillPhoto) / "review": 후기 인증샷(DietReviewPhoto)
  image?: "product" | "review" | "pill";
}



export interface GameStage {
  id: number;
  stageid: string;
  title: string;
  location: string;
  description: string;
  messages: DialogueMessage[];
  question: string;
  evaluation: string[];
  scoreType: string;
  // 답변 제출 후 NPC가 되받아치는 한 줄 반응 (백엔드 연동 전 임시 목업 —
  // 나중에는 이 자리에 /chat 응답의 npc_response가 들어갈 예정)
  reaction?: string;
}

export const episode01Stages: GameStage[] = [
  // =========================
  // Stage 1 : 위험 인지
  // =========================
  {
    id: 1,
    stageid: "EP01_STAGE01",
    title: "위험 인지",
    location: "스터디 단체 채팅방",

    description:
      "고등학교 2학년인 당신은 중간고사를 앞두고 있습니다. 평소 친하게 지내던 친구의 스터디 그룹에 참여했습니다.",

    messages: [
      { sender: "지우", text: "나 요즘 이거 먹고 공부하는데 잠이 하나도 안 온다." },
      { sender: "지우", text: "집중도 엄청 잘 됨." },
      { sender: "지우", text: "", image: "pill" },
      { sender: "주원", text: "나도 써봄." },
      { sender: "주원", text: "효과 좋음." },
    ],

    question:
      "포장지가 없는 알약 사진이 올라왔습니다. 이 상황에서는 어떻게 대응하시겠습니까?",

    evaluation: [
      "알약의 출처를 의심하는가?",
      "안전성을 확인하려 하는가?",
      "단순 공부 비법으로 받아들이는가?",
    ],

    scoreType: "위험 인지",

    reaction: "에이, 한번 먹어본다고 큰일 나겠어?",
  },

  // =========================
  // Stage 2 : 거절
  // =========================
  {
    id: 2,
    stageid: "EP01_STAGE02",
    title: "거절",
    location: "다음 날 학교 쉬는 시간",

    description:
      "다음 날, 스터디 그룹의 친구가 쉬는 시간에 당신에게 다가옵니다.",

    messages: [
      { sender: "지우", text: "어제 채팅방 봤지?" },
      { sender: "지우", text: "시험 끝날 때까지만 먹어봐." },
      { sender: "지우", text: "다들 하는데 뭐." },
    ],

    question:
      "친구가 계속 알약을 권하고 있습니다. 친구에게 어떻게 답하겠습니까?",

    evaluation: [
      "명확하게 거절하는가?",
      "우물쭈물하는가?",
      "관계 때문에 수용하는가?",
    ],

    scoreType: "거절 대응",

    reaction: "치, 너무 빡빡하게 구는 거 아니냐.",
  },

  // =========================
  // Stage 3 : 압박 증가
  // =========================
  {
    id: 3,
    stageid: "EP01_STAGE03",
    title: "압박 증가",
    location: "학교 교실",

    description:
      "당신이 거절하자 친구가 약간 서운한 표정을 짓습니다. 주변 친구들도 대화를 듣고 있습니다.",

    messages: [
      { sender: "지우", text: "너만 안 한다고?" },
      { sender: "지우", text: "우리 못 믿어?" },
    ],

    question:
      "주변 친구들이 지켜보고 있는 상황입니다. 어떻게 행동하겠습니까?",

    evaluation: [
      "또래의 압력에도 자신의 판단을 유지하는가?",
      "자신의 의사를 분명하게 표현하는가?",
    ],

    scoreType: "거절 대응 심화",

    reaction: "...흠, 알았어. 근데 좀 서운하네.",
  },

  // =========================
  // Stage 4 : 도움 요청
  // =========================
  {
    id: 4,
    stageid: "EP01_STAGE04",
    title: "도움 요청",
    location: "며칠 뒤 수업 시간",

    description:
      "며칠 뒤, 스터디방 학생 중 한 명이 수업 시간에 갑자기 심한 어지럼증을 호소합니다.",

    messages: [
      { sender: "지우", text: "선생님한테는 말하지 말자." },
      { sender: "지우", text: "괜히 우리까지 문제 된다." },
    ],

    question:
      "친구들은 이 사실을 숨기려고 합니다. 당신은 어떤 행동을 하겠습니까?",

    evaluation: [
      "도움이 필요한 상황임을 인식하는가?",
      "적절한 도움 대상을 떠올리는가?",
    ],

    scoreType: "도움 요청",

    reaction: "너 진짜 말할 거야? 나중에 딴소리하지 마라.",
  },

  // =========================
  // Stage 5 : 최종 판단
  // =========================
  {
    id: 5,
    stageid: "EP01_STAGE05",
    title: "최종 판단",
    location: "그날 밤 스터디 단체 채팅방",

    description:
      "그날 밤, 스터디방 방장(지우)이 단체 채팅방에 메시지를 보냅니다.",

    messages: [
      { sender: "지우", text: "오늘 있었던 일은 비밀이다." },
      { sender: "지우", text: "채팅 기록도 지워." },
    ],

    question:
      "스터디방 방장이 사건을 숨기려고 합니다. 당신은 어떻게 대응하겠습니까?",

    evaluation: [
      "상황을 숨기라는 요구에 따르지 않는가?",
      "책임 있는 행동을 하려고 하는가?",
      "적절한 도움을 적극적으로 요청하려 하는가?",
    ],

    scoreType: "도움 요청 심화",

    reaction: "...진심이냐? 후회 안 해?",
  },
];