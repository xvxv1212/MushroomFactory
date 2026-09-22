import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


EPISODE_PATH = (
    BASE_DIR
    / "episodes"
    / "episode01.json"
)

BRANCH_PATH = (
    BASE_DIR
    / "branches"
    / "episode01-branches.json"
)

AI_FIXTURE_PATH = (
    BASE_DIR
    / "fixtures"
    / "ai-evaluation-response.json"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def score_to_branch(score):

    if score == 3:
        return "high"

    if score == 2:
        return "medium"

    return "low"


def main():

    episode = load_json(
        EPISODE_PATH
    )

    branch_data = load_json(
        BRANCH_PATH
    )

    ai_response = load_json(
        AI_FIXTURE_PATH
    )

    errors = []

    # --------------------
    # AI 필수 필드 검사
    # --------------------

    required_fields = [
        "stage_id",
        "axis",
        "score"
    ]

    for field in required_fields:

        if field not in ai_response:

            errors.append(
                f"AI Response에 "
                f"{field}가 없습니다."
            )


    if errors:

        print("\nAI Contract 검사 실패\n")

        for error in errors:
            print("-", error)

        return


    stage_id = ai_response[
        "stage_id"
    ]

    axis = ai_response[
        "axis"
    ]

    score = ai_response[
        "score"
    ]


    # --------------------
    # Stage 존재 검사
    # --------------------

    stages = {
        stage["stage_id"]: stage
        for stage
        in episode["stages"]
    }


    if stage_id not in stages:

        errors.append(
            f"존재하지 않는 Stage입니다: "
            f"{stage_id}"
        )

    else:

        expected_axis = (
            stages[stage_id][
                "evaluation_axis"
            ]
        )

        # --------------------
        # Axis 검사
        # --------------------

        if axis != expected_axis:

            errors.append(
                f"{stage_id}의 평가축은 "
                f"{expected_axis}이어야 하지만 "
                f"{axis}가 전달되었습니다."
            )


    # --------------------
    # Score 검사
    # --------------------

    if not isinstance(score, int):

        errors.append(
            "score는 정수여야 합니다."
        )

    elif score < 0 or score > 3:

        errors.append(
            f"score 범위 오류: {score}"
        )


    # --------------------
    # Branch Mapping 검사
    # --------------------

    if (
        isinstance(score, int)
        and 0 <= score <= 3
    ):

        branch = score_to_branch(
            score
        )

        branch_stages = (
            branch_data[
                "stages"
            ]
        )

        if stage_id in branch_stages:

            branches = (
                branch_stages[
                    stage_id
                ]["branches"]
            )

            if branch not in branches:

                errors.append(
                    f"{stage_id}에 "
                    f"{branch} 분기가 없습니다."
                )


    # --------------------
    # 결과
    # --------------------

    if errors:

        print(
            "\nAI ↔ Scenario "
            "계약 검사 실패\n"
        )

        for error in errors:

            print(
                "-",
                error
            )

    else:

        selected_branch = (
            score_to_branch(
                score
            )
        )

        print(
            "\nAI ↔ Scenario "
            "계약 검사 성공"
        )

        print(
            f"Stage : {stage_id}"
        )

        print(
            f"Axis : {axis}"
        )

        print(
            f"Score : {score}"
        )

        print(
            f"Branch : "
            f"{selected_branch}"
        )


if __name__ == "__main__":
    main()