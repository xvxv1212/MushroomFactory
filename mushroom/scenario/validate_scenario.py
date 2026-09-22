import json
import sys

from pathlib import Path


SCENARIO_DIR = (
    Path(__file__)
    .resolve()
    .parent
    / "episodes"
)


VALID_AXES = {
    "risk_awareness",
    "refusal",
    "help_request"
}


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


def validate_episode(
    file_path: Path
) -> list[str]:

    errors = []

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            episode = json.load(
                file
            )

    except json.JSONDecodeError as exc:

        return [
            f"JSON 오류: {exc}"
        ]


    episode_id = episode.get(
        "episode_id"
    )

    if not episode_id:

        errors.append(
            "episode_id가 없습니다."
        )


    stages = episode.get(
        "stages"
    )

    if not isinstance(
        stages,
        list
    ) or not stages:

        errors.append(
            "stages가 없거나 비어 있습니다."
        )

        return errors


    stage_ids = [
        stage.get(
            "stage_id"
        )
        for stage in stages
    ]


    # Stage ID 중복 검사
    if (
        len(stage_ids)
        != len(set(stage_ids))
    ):

        errors.append(
            "중복된 stage_id가 있습니다."
        )


    for index, stage in enumerate(
        stages,
        start=1
    ):

        stage_id = stage.get(
            "stage_id",
            f"Stage {index}"
        )


        # 필수 필드
        missing = (
            REQUIRED_STAGE_FIELDS
            - set(stage.keys())
        )

        if missing:

            errors.append(
                f"{stage_id}: "
                f"필수 필드 누락 "
                f"{sorted(missing)}"
            )


        # Stage 번호
        if (
            stage.get(
                "stage_number"
            )
            != index
        ):

            errors.append(
                f"{stage_id}: "
                "stage_number 순서가 올바르지 않습니다."
            )


        # Episode ID와 Stage ID 확인
        expected_prefix = (
            f"{episode_id}_STAGE"
        )

        if not stage_id.startswith(
            expected_prefix
        ):

            errors.append(
                f"{stage_id}: "
                "episode_id와 stage_id가 일치하지 않습니다."
            )


        # 평가축 검사
        axis = stage.get(
            "evaluation_axis"
        )

        if (
            axis
            not in VALID_AXES
        ):

            errors.append(
                f"{stage_id}: "
                f"잘못된 evaluation_axis "
                f"({axis})"
            )


        # Messages 검사
        messages = stage.get(
            "messages",
            []
        )

        if not messages:

            errors.append(
                f"{stage_id}: "
                "messages가 비어 있습니다."
            )

        for message in messages:

            if (
                not message.get(
                    "speaker"
                )
                or
                not message.get(
                    "text"
                )
            ):

                errors.append(
                    f"{stage_id}: "
                    "message에 speaker 또는 text가 없습니다."
                )


        # 평가 기준
        criteria = stage.get(
            "evaluation_criteria",
            []
        )

        if not criteria:

            errors.append(
                f"{stage_id}: "
                "evaluation_criteria가 비어 있습니다."
            )


        # next_stage 검사
        next_stage = stage.get(
            "next_stage"
        )

        if (
            next_stage is not None
            and
            next_stage not in stage_ids
        ):

            errors.append(
                f"{stage_id}: "
                f"존재하지 않는 next_stage "
                f"({next_stage})"
            )


    # 마지막 Stage는 반드시 종료
    last_stage = stages[-1]

    if (
        last_stage.get(
            "next_stage"
        )
        is not None
    ):

        errors.append(
            "마지막 Stage의 "
            "next_stage는 null이어야 합니다."
        )


    return errors


def main():

    files = sorted(
        SCENARIO_DIR.glob(
            "episode*.json"
        )
    )

    if not files:

        print(
            "Scenario 파일이 없습니다."
        )

        sys.exit(1)


    has_error = False

    for file_path in files:

        errors = validate_episode(
            file_path
        )

        if errors:

            has_error = True

            print(
                f"\n[FAIL] "
                f"{file_path.name}"
            )

            for error in errors:

                print(
                    f" - {error}"
                )

        else:

            print(
                f"[PASS] "
                f"{file_path.name}"
            )


    if has_error:

        sys.exit(1)


    print(
        "\nScenario validation passed."
    )


if __name__ == "__main__":
    main()