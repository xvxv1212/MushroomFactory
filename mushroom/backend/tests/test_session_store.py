from app.core.session_store import (
    MemorySessionStore
)


def test_create_session():

    store = MemorySessionStore()

    session = store.create_session(
        session_id="TEST001",
        episode_id="EP01",
        first_stage="EP01_STAGE01"
    )

    assert session["episode_id"] == "EP01"

    assert (
        session["current_stage"]
        == "EP01_STAGE01"
    )

    assert session["scores"] == {
        "risk_awareness": 0,
        "refusal": 0,
        "help_request": 0
    }

    assert session["is_complete"] is False


def test_get_session():

    store = MemorySessionStore()

    store.create_session(
        session_id="TEST001",
        episode_id="EP01",
        first_stage="EP01_STAGE01"
    )

    session = store.get_session(
        "TEST001"
    )

    assert session is not None

    assert (
        session["episode_id"]
        == "EP01"
    )


def test_apply_stage_result():

    store = MemorySessionStore()

    store.create_session(
        session_id="TEST001",
        episode_id="EP01",
        first_stage="EP01_STAGE01"
    )

    saved = store.apply_stage_result(
        session_id="TEST001",

        stage_id="EP01_STAGE01",

        feedback=(
            "위험성을 잘 인지했어요."
        ),

        scores={
            "risk_awareness": 3,
            "refusal": 0,
            "help_request": 0
        },

        next_stage="EP01_STAGE02"
    )

    assert saved is True

    session = store.get_session(
        "TEST001"
    )

    assert (
        session["scores"][
            "risk_awareness"
        ]
        == 3
    )

    assert (
        session["current_stage"]
        == "EP01_STAGE02"
    )

    assert (
        "EP01_STAGE01"
        in session[
            "completed_stages"
        ]
    )


def test_duplicate_stage():

    store = MemorySessionStore()

    store.create_session(
        session_id="TEST001",
        episode_id="EP01",
        first_stage="EP01_STAGE01"
    )

    scores = {
        "risk_awareness": 3,
        "refusal": 0,
        "help_request": 0
    }

    first = store.apply_stage_result(
        session_id="TEST001",
        stage_id="EP01_STAGE01",
        feedback="첫 번째 평가",
        scores=scores,
        next_stage="EP01_STAGE02"
    )

    second = store.apply_stage_result(
        session_id="TEST001",
        stage_id="EP01_STAGE01",
        feedback="중복 평가",
        scores=scores,
        next_stage="EP01_STAGE02"
    )

    assert first is True
    assert second is False


def test_delete_session():

    store = MemorySessionStore()

    store.create_session(
        session_id="TEST001",
        episode_id="EP01",
        first_stage="EP01_STAGE01"
    )

    deleted = store.delete_session(
        "TEST001"
    )

    assert deleted is True

    assert (
        store.get_session(
            "TEST001"
        )
        is None
    )