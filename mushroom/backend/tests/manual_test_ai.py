import asyncio

from app.services.ai_service import evaluate_response


stage_data = {
    "stage_id": "EP01_STAGE02",

    "title": "거절",

    "scene": {
        "location": "학교 쉬는 시간",
        "description": "친구가 정체가 확인되지 않은 알약을 권유한다."
    },

    "npc_messages": [
        "어제 채팅방 봤지?",
        "시험 끝날 때까지만 먹어봐.",
        "다들 하는데 뭐."
    ],

    "question": "친구에게 어떻게 답하겠습니까?",

    "evaluation": {
        "refusal": {
            "max_score": 3,
            "criteria": [
                "명확하게 거절하는가?",
                "우물쭈물하지 않는가?",
                "관계 때문에 수용하지 않는가?"
            ]
        }
    }
}


# async def main():

#     result = await evaluate_response(
#         episode_id="EP01",
#         stage_id="EP01_STAGE02",
#         user_message="난 안 먹을래. 뭔지도 모르는데 먹고 싶지 않아.",
#         stage_data=stage_data
#     )

#     print(result)


# asyncio.run(main())

async def main():

    print("1. AI 테스트 시작")

    result = await evaluate_response(
        episode_id="EP01",
        stage_id="EP01_STAGE02",
        user_message="너나 먹어",
        stage_data=stage_data
    )

    print("2. AI 응답 받음")
    print(result)


asyncio.run(main())