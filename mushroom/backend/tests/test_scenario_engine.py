from app.core.scenario_engine import (
    load_episode,
    get_stage,
    get_total_stages,
    list_episodes
)


def test_load_episode():

    episode = load_episode(
        "EP01"
    )

    assert episode is not None

    assert (
        episode["episode_id"]
        == "EP01"
    )

    assert (
        episode["title"]
        == "시험기간 스터디 그룹"
    )


def test_get_stage():

    stage = get_stage(
        "EP01",
        "EP01_STAGE01"
    )

    assert stage is not None

    assert (
        stage["evaluation_axis"]
        == "risk_awareness"
    )

    assert (
        "messages"
        in stage
    )


def test_total_stages():

    assert (
        get_total_stages(
            "EP01"
        )
        == 5
    )


def test_invalid_episode():

    episode = load_episode(
        "EP99"
    )

    assert episode is None


def test_list_episodes():

    episodes = list_episodes()

    assert len(
        episodes
    ) >= 1

    assert any(
        episode[
            "episode_id"
        ] == "EP01"

        for episode in episodes
    )