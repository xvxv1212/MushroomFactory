import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main():

    if len(sys.argv) < 2:
        print(
            "사용법: "
            "python validate_branches.py EP01"
        )
        return

    episode_id = sys.argv[1].upper()

    if not episode_id.startswith("EP"):
        print(
            "Episode ID는 EP01, EP02, EP03 "
            "형식이어야 합니다."
        )
        return

    episode_number = episode_id.replace(
        "EP",
        ""
    )

    EPISODE_PATH = (
        BASE_DIR
        / "episodes"
        / f"episode{episode_number}.json"
    )

    BRANCH_PATH = (
        BASE_DIR
        / "branches"
        / f"episode{episode_number}-branches.json"
    )

    if not EPISODE_PATH.exists():
        print(
            f"\n시나리오 파일이 없습니다: "
            f"{EPISODE_PATH}"
        )
        return

    if not BRANCH_PATH.exists():
        print(
            f"\n분기 파일이 없습니다: "
            f"{BRANCH_PATH}"
        )
        return

    episode = load_json(EPISODE_PATH)
    branch_data = load_json(BRANCH_PATH)

    errors = []

    stage_ids = [
        stage["stage_id"]
        for stage in episode["stages"]
    ]

    branch_stages = branch_data.get(
        "stages",
        {}
    )

    # 모든 Stage에 분기가 있는지 확인
    for stage_id in stage_ids:

        if stage_id not in branch_stages:
            errors.append(
                f"{stage_id} 분기가 없습니다."
            )

            continue

        branches = branch_stages[
            stage_id
        ].get("branches", {})

        # high / medium / low 확인
        for level in [
            "high",
            "medium",
            "low"
        ]:

            if level not in branches:
                errors.append(
                    f"{stage_id}에 "
                    f"{level} 분기가 없습니다."
                )

    # next_stage 검사
    for stage_id, stage_data in (
        branch_stages.items()
    ):

        for branch_name, branch in (
            stage_data
            .get("branches", {})
            .items()
        ):

            next_stage = branch.get(
                "next_stage"
            )

            if (
                next_stage is not None
                and next_stage not in stage_ids
            ):
                errors.append(
                    f"{stage_id} / "
                    f"{branch_name}: "
                    f"{next_stage}가 "
                    "존재하지 않습니다."
                )

    if errors:

        print(
            f"\n{episode_id} "
            "분기 검사 실패\n"
        )

        for error in errors:
            print("-", error)

    else:

        print(
            f"\n{episode_id} "
            "분기 검사 성공"
        )

        print(
            "모든 Stage에 "
            "high / medium / low "
            "분기가 존재합니다."
        )


if __name__ == "__main__":
    main()