import subprocess
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent


scripts = [
    "validate_episode.py",
    "validate_branches.py",
    "validate_ai_contract.py",
    "calculate_score.py"
]


print("\n======================")
print("EP01 Scenario QA 시작")
print("======================\n")


for script in scripts:

    print(
        f"\n[실행] {script}"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(
                TOOLS_DIR
                / script
            )
        ]
    )

    if result.returncode != 0:

        print(
            f"\n실패: {script}"
        )

        sys.exit(1)


print(
    "\n======================"
)

print(
    "Scenario QA 완료"
)

print(
    "======================"
)