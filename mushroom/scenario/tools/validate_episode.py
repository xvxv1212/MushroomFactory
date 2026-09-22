import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_episode(episode, rubric):
    errors = []

    # 1. 기본 정보 검사
    if "episode_id" not in episode:
        errors.append("episode_id가 없습니다.")

    if "title" not in episode:
        errors.append("title이 없습니다.")

    if "stages" not in episode:
        errors.append("stages가 없습니다.")
        return errors

    stages = episode["stages"]

    # 2. Stage 수 확인
    if len(stages) != episode.get("total_stages"):
        errors.append(
            f"total_stages={episode.get('total_stages')}인데 "
            f"실제 Stage 수는 {len(stages)}개입니다."
        )

    stage_ids = []

    for stage in stages:

        required_fields = [
            "stage_id",
            "stage_number",
            "title",
            "messages",
            "question",
            "evaluation_axis",
            "evaluation_criteria",
            "next_stage"
        ]

        for field in required_fields:
            if field not in stage:
                errors.append(
                    f"{stage.get('stage_id', 'UNKNOWN')}에 "
                    f"{field}가 없습니다."
                )

        if "stage_id" in stage:
            stage_ids.append(stage["stage_id"])

    # 3. Stage ID 중복 검사
    if len(stage_ids) != len(set(stage_ids)):
        errors.append("중복된 stage_id가 있습니다.")

    # 4. Stage 번호 검사
    stage_numbers = [
        stage.get("stage_number")
        for stage in stages
    ]

    expected_numbers = list(range(1, len(stages) + 1))

    if stage_numbers != expected_numbers:
        errors.append(
            f"Stage 번호가 올바르지 않습니다. "
            f"현재={stage_numbers}, "
            f"기대값={expected_numbers}"
        )

    # 5. next_stage 연결 검사
    for stage in stages:

        next_stage = stage.get("next_stage")

        if next_stage is not None and next_stage not in stage_ids:
            errors.append(
                f"{stage['stage_id']}의 next_stage "
                f"{next_stage}가 존재하지 않습니다."
            )

    # 6. 마지막 Stage 검사
    if stages:
        last_stage = stages[-1]

        if last_stage.get("next_stage") is not None:
            errors.append(
                "마지막 Stage의 next_stage는 null이어야 합니다."
            )

    # 7. Rubric 검사
    rubric_stages = rubric.get("stages", {})

    for stage in stages:

        stage_id = stage.get("stage_id")

        if stage_id not in rubric_stages:
            errors.append(
                f"{stage_id}에 대한 Rubric이 없습니다."
            )

    return errors


def main():

    # 실행할 Episode ID
    # 예: python validate_episode.py EP02
    episode_id = sys.argv[1] if len(sys.argv) > 1 else "EP01"

    # EP02 → 02
    episode_number = episode_id[-2:]

    # 실제 파일명:
    # episode02.json
    # episode02-rubric.json
    episode_path = (
        BASE_DIR
        / "episodes"
        / f"episode{episode_number}.json"
    )

    rubric_path = (
        BASE_DIR
        / "rubrics"
        / f"episode{episode_number}-rubric.json"
    )

    # Episode 파일 존재 여부 확인
    if not episode_path.exists():
        print(f"파일이 없습니다: {episode_path}")
        return

    # Rubric 파일 존재 여부 확인
    if not rubric_path.exists():
        print(f"파일이 없습니다: {rubric_path}")
        return

    # JSON 로드
    episode = load_json(episode_path)
    rubric = load_json(rubric_path)

    # Episode 검증
    errors = validate_episode(
        episode,
        rubric
    )

    print(f"\n{episode_id} 시나리오 검사 시작\n")

    if errors:

        print("검사 실패\n")

        for error in errors:
            print(f"- {error}")

    else:

        print("검사 성공")
        print(
            f"{episode_id} 시나리오 구조에 문제가 없습니다."
        )

        print("\nStage 흐름")

        for stage in episode["stages"]:

            print(
                f"{stage['stage_id']} "
                f"→ {stage.get('next_stage')}"
            )


if __name__ == "__main__":
    main()
