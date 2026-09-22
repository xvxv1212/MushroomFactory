import pytest

from app.services.ai_service import evaluate_response


@pytest.mark.asyncio
async def test_ai_response_contract():

    stage_data = {
        "stage_id": "EP01_STAGE02",
        "title": "거절",

        "scene": {
            "location": "학교 쉬는 시간",
            "description": "친구가 정체가 불분명한 약을 권하고 있다."
        },

        "npc_messages": [
            "어제 채팅방 봤지?",
            "시험 끝날 때까지만 먹어봐.",
            "다들 하는데 뭐."
        ],

        "question":
            "친구에게 어떻게 답하겠습니까?",

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

    result = await evaluate_response(
        episode_id="EP01",
        stage_id="EP01_STAGE02",
        user_message="난 안 먹을래. 무슨 약인지도 모르잖아.",
        stage_data=stage_data
    )

    assert "npc_response" in result
    assert "feedback" in result
    assert "scores" in result

    assert "risk_awareness" in result["scores"]
    assert "refusal" in result["scores"]
    assert "help_request" in result["scores"]

    assert 0 <= result["scores"]["risk_awareness"] <= 3
    assert 0 <= result["scores"]["refusal"] <= 3
    assert 0 <= result["scores"]["help_request"] <= 3