from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "content/snippets/js/s/get-selected-text.md"
WORK_DIR = ROOT / "work" / "R52-T021"
REPORT = WORK_DIR / "results.json"

EXPECTED_OUTPUT = "Lorem ipsum\n\n"


def run_javascript(source, initial_selection):
    harness = r"""
const selected = { value: INITIAL_SELECTION };
const selection = {
  toString() {
    return selected.value;
  },
  removeAllRanges() {
    selected.value = "";
  }
};

globalThis.window = {
  getSelection() {
    return selection;
  }
};

console.assert = (condition, ...message) => {
  if (!condition) {
    throw new Error(message.join(" ") || "Assertion failed");
  }
};
""".replace(
        "INITIAL_SELECTION",
        json.dumps(initial_selection)
    )

    return subprocess.run(
        ["node", "-e", harness + "\n" + source],
        capture_output=True,
        text=True
    )


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    if not ARTICLE.exists():
        raise FileNotFoundError(f"Article not found: {ARTICLE}")

    content = ARTICLE.read_text()

    match = re.search(r"```js\s*\n(.*?)\n```", content, re.DOTALL)

    if not match:
        raise ValueError("JavaScript code block not found in the article.")

    # Execute the actual JavaScript extracted from the published article.
    source = match.group(1)

    node_version = subprocess.run(
        ["node", "--version"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    # Positive test: the expected selection should pass.
    positive = run_javascript(source, "Lorem ipsum")

    # Negative test: a deliberately incorrect selection must fail.
    negative = run_javascript(source, "WRONG TEXT")

    positive_passed = (
        positive.returncode == 0
        and positive.stdout == EXPECTED_OUTPUT
    )

    negative_passed = (
        negative.returncode != 0
        and 'Expected "Lorem ipsum".' in negative.stderr
    )

    report = {
        "article": str(ARTICLE.relative_to(ROOT)),
        "input": {
            "selected_text": "Lorem ipsum",
            "selection_after_remove_all_ranges": ""
        },
        "expected_output": EXPECTED_OUTPUT,
        "actual_output": positive.stdout,
        "positive_test_exit_code": positive.returncode,
        "positive_test_passed": positive_passed,
        "negative_test_input": "WRONG TEXT",
        "negative_test_exit_code": negative.returncode,
        "negative_test_passed": negative_passed,
        "negative_test_error": negative.stderr,
        "python_version": sys.version,
        "node_version": node_version
    }

    REPORT.write_text(json.dumps(report, indent=2) + "\n")

    print("Positive test:", "PASSED" if positive_passed else "FAILED")
    print("Actual output:", repr(positive.stdout))
    print("Negative test:", "PASSED" if negative_passed else "FAILED")
    print("Evidence saved to:", REPORT.relative_to(ROOT))

    if not positive_passed or not negative_passed:
        print("\nChecker failed. Inspect the results.json file.")
        if positive.stderr:
            print(positive.stderr)
        sys.exit(1)

    print("\nAll JavaScript checks passed.")


if __name__ == "__main__":
    main()
