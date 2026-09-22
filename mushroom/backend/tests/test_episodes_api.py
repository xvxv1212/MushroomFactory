def test_episode_list(
    client
):

    response = client.get(
        "/api/episodes"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert len(data) >= 1

    assert (
        data[0]["episode_id"]
        == "EP01"
    )


def test_episode_detail(
    client
):

    response = client.get(
        "/api/episodes/EP01"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["total_stages"]
        == 5
    )

    assert (
        len(data["stages"])
        == 5
    )


def test_stage_detail(
    client
):

    response = client.get(
        "/api/episodes/"
        "EP01/stages/"
        "EP01_STAGE01"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["evaluation_axis"]
        == "risk_awareness"
    )


def test_episode_not_found(
    client
):

    response = client.get(
        "/api/episodes/EP99"
    )

    assert (
        response.status_code
        == 404
    )