import json
import re
import subprocess
import sys
from pathlib import Path

ARTICLE_PATH = Path("content/snippets/js/s/eslint-prettier-configuration.md")
RESULTS_PATH = Path("work/R52-T022/results.json")

EXPECTED_LINES = [
    ">=9.24.0 <10.0.0-0",
    ">=0.0.3 <0.0.4-0",
    "^9.24.0 9.24.0: true",
    "^9.24.0 9.99.0: true",
    "^9.24.0 10.0.0: false",
    "^0.0.3 0.0.3: true",
    "^0.0.3 0.0.4: false",
    "^0.0.3 0.1.0: false",
]


def extract_semver_code(markdown_text: str) -> str:
    blocks = re.findall(r"```js\n(.*?)\n```", markdown_text, flags=re.DOTALL)
    for block in blocks:
        if "import semver from 'semver';" in block:
            return block
    raise RuntimeError("Could not find the semver JS code block in the article.")


def run_check(expected_lines=None):
    if expected_lines is None:
        expected_lines = EXPECTED_LINES

    article_text = ARTICLE_PATH.read_text(encoding="utf-8")
    code = extract_semver_code(article_text)

    proc = subprocess.run(
        ["node", "--input-type=module", "-e", code],
        capture_output=True,
        text=True,
        check=True,
    )
    actual_lines = [line.strip() for line in proc.stdout.strip().splitlines() if line.strip()]
    passed = actual_lines == expected_lines

    return {
        "task": "R52-T022",
        "article": str(ARTICLE_PATH),
        "passed": passed,
        "expected": expected_lines,
        "actual": actual_lines,
    }


def main():
    # Support negative testing via --expect-fail flag
    if "--negative-test" in sys.argv:
        tampered = list(EXPECTED_LINES)
        tampered[-1] = "^0.0.3 0.1.0: true"
        result = run_check(expected_lines=tampered)
        if result["passed"]:
            print("ERROR: Negative test unexpectedly passed!")
            sys.exit(1)
        print("Negative test passed: checker failed as expected on tampered output.")
        sys.exit(0)

    result = run_check()
    RESULTS_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if not result["passed"]:
        print("Check FAILED!")
        print("Expected:", result["expected"])
        print("Actual:  ", result["actual"])
        sys.exit(1)

    print("Check PASSED! Evidence saved to", RESULTS_PATH)


if __name__ == "__main__":
    main()
