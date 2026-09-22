def calculate_episode_score(stage_scores, episode_id):
    stage1 = stage_scores[f"{episode_id}_STAGE01"]
    stage2 = stage_scores[f"{episode_id}_STAGE02"]
    stage3 = stage_scores[f"{episode_id}_STAGE03"]
    stage4 = stage_scores[f"{episode_id}_STAGE04"]
    stage5 = stage_scores[f"{episode_id}_STAGE05"]

    risk_awareness = round(
        stage1 / 3 * 100
    )

    refusal = round(
        (stage2 + stage3) / 6 * 100
    )

    help_request = round(
        (stage4 + stage5) / 6 * 100
    )

    return {
        "risk_awareness": risk_awareness,
        "refusal": refusal,
        "help_request": help_request
    }


if __name__ == "__main__":

    test_scores = {
        "EP02_STAGE01": 2,
        "EP02_STAGE02": 3,
        "EP02_STAGE03": 2,
        "EP02_STAGE04": 3,
        "EP02_STAGE05": 2
    }

    result = calculate_episode_score(
        test_scores,
        "EP02"
    )

    print(result)