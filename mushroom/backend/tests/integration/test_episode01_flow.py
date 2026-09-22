from unittest.mock import (
    AsyncMock,
    patch
)


@patch(
    "app.api.chat.evaluate_response",
    new_callable=AsyncMock
)
def test_episode01_full_flow(
    mock_ai,
    client
):

    # Stage마다 반환할 AI 결과
    mock_ai.side_effect = [

        # Stage01
        {
            "npc_response":
                "그렇게 위험할까?",

            "feedback":
                "출처와 안전성을 의심했어요.",

            "scores": {
                "risk_awareness": 3,
                "refusal": 0,
                "help_request": 0
            }
        },

        # Stage02
        {
            "npc_response":
                "진짜 안 먹을 거야?",

            "feedback":
                "명확하게 거절했어요.",

            "scores": {
                "risk_awareness": 0,
                "refusal": 3,
                "help_request": 0
            }
        },

        # Stage03
        {
            "npc_response":
                "우리 못 믿어?",

            "feedback":
                "또래 압박에도 거절을 유지했어요.",

            "scores": {
                "risk_awareness": 0,
                "refusal": 3,
                "help_request": 0
            }
        },

        # Stage04
        {
            "npc_response":
                "선생님한테 말하려고?",

            "feedback":
                "도움이 필요한 상황임을 인지했어요.",

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 3
            }
        },

        # Stage05
        {
            "npc_response":
                "정말 말할 거야?",

            "feedback":
                "상황을 숨기지 않고 도움을 요청했어요.",

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 3
            }
        }
    ]


    # 1. Session 생성
    response = client.post(
        "/api/sessions",
        json={
            "episode_id": "EP01"
        }
    )

    assert response.status_code == 200

    session_id = response.json()[
        "session_id"
    ]


    # 2. Stage01
    response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "episode_id": "EP01",
            "stage_id": "EP01_STAGE01",
            "message":
                "출처를 모르니까 위험해 보여."
        }
    )

    assert response.status_code == 200

    assert (
        response.json()["next_stage"]
        == "EP01_STAGE02"
    )


    # 3. Stage02
    response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "episode_id": "EP01",
            "stage_id": "EP01_STAGE02",
            "message":
                "난 안 먹을래."
        }
    )

    assert response.status_code == 200

    assert (
        response.json()["next_stage"]
        == "EP01_STAGE03"
    )


    # 4. Stage03
    response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "episode_id": "EP01",
            "stage_id": "EP01_STAGE03",
            "message":
                "너희를 못 믿는 게 아니라 난 안 먹을 거야."
        }
    )

    assert response.status_code == 200

    assert (
        response.json()["next_stage"]
        == "EP01_STAGE04"
    )


    # 5. Stage04
    response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "episode_id": "EP01",
            "stage_id": "EP01_STAGE04",
            "message":
                "선생님이나 보건교사에게 알려야 해."
        }
    )

    assert response.status_code == 200

    assert (
        response.json()["next_stage"]
        == "EP01_STAGE05"
    )


    # 6. Stage05
    response = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "episode_id": "EP01",
            "stage_id": "EP01_STAGE05",
            "message":
                "기록을 지우지 않고 믿을 수 있는 어른에게 알릴 거야."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data[
        "next_stage"
    ] is None

    assert (
        data[
            "is_episode_complete"
        ]
        is True
    )


    # 7. 최종 결과
    response = client.get(
        f"/api/sessions/"
        f"{session_id}/result"
    )

    assert response.status_code == 200

    result = response.json()

    assert (
        result["is_complete"]
        is True
    )

    assert (
        len(
            result[
                "completed_stages"
            ]
        )
        == 5
    )

    assert (
        len(
            result[
                "stage_results"
            ]
        )
        == 5
    )

    assert (
        result[
            "scores"
        ][
            "risk_awareness"
        ]
        == 3
    )

    assert (
        result[
            "scores"
        ][
            "refusal"
        ]
        == 6
    )

    assert (
        result[
            "scores"
        ][
            "help_request"
        ]
        == 6
    )