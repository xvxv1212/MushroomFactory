import json

from pathlib import Path

from app.ai.prompts import (
    build_user_prompt
)


def load_real_stage():

    project_root = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    scenario_path = (
        project_root
        / "scenario"
        / "episodes"
        / "episode01.json"
    )

    with open(
        scenario_path,
        "r",
        encoding="utf-8"
    ) as file:

        episode = json.load(
            file
        )

    return episode["stages"][0]


def test_prompt_uses_real_scenario_fields():

    stage = load_real_stage()

    prompt = build_user_prompt(
        episode_id="EP01",
        stage_id="EP01_STAGE01",
        user_message=(
            "포장도 없고 출처를 "
            "모르니까 위험해 보여."
        ),
        stage_data=stage
    )

    assert (
        "스터디 단체 채팅방"
        in prompt
    )

    assert (
        "포장지가 없는 알약"
        in prompt
    )

    assert (
        "알약의 출처를 의심하는가"
        in prompt
    )

    assert (
        "risk_awareness"
        in prompt
    )

    assert "None" not in prompt