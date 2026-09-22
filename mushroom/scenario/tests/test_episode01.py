from pathlib import Path

from scenario.validate_scenario import (
    validate_episode
)


def test_episode01_contract():

    scenario_root = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    episode = (
        scenario_root
        / "episodes"
        / "episode01.json"
    )

    errors = validate_episode(
        episode
    )

    assert errors == [], (
        "\n".join(errors)
    )