stage01 = {
    "stage_id": "EP01_STAGE01",

    "title": "위험 인지",

    "scene": {
        "location": "스터디 단체 채팅방",
        "description": (
            "학생들이 출처를 알 수 없는 알약에 대해 "
            "공부가 잘된다고 이야기하고 있다."
        )
    },

    "npc_messages": [
        "나 요즘 이거 먹고 공부하는데 잠이 하나도 안 온다.",
        "집중도 엄청 잘 됨.",
        "나도 써봄.",
        "효과 좋음."
    ],

    "question":
        "이 상황에서 어떤 점이 가장 신경 쓰이나요?",

    "evaluation": {
        "risk_awareness": {
            "max_score": 3,
            "criteria": [
                "알약의 출처를 의심하는가?",
                "안전성을 확인하려 하는가?",
                "단순 공부 비법으로 받아들이지 않는가?"
            ]
        }
    }
}