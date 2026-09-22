from app.core.scenario_engine import (
    load_episode
)


REQUIRED_STAGE_FIELDS = {
    "stage_id",
    "stage_number",
    "title",
    "type",
    "location",
    "description",
    "messages",
    "question",
    "evaluation_axis",
    "evaluation_criteria",
    "next_stage"
}


def test_backend_scenario_contract():

    episode = load_episode(
        "EP01"
    )

    assert episode is not None

    for stage in episode[
        "stages"
    ]:

        assert (
            REQUIRED_STAGE_FIELDS
            .issubset(
                stage.keys()
            )
        )