import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "content/snippets/js/s/relative-time-formatting.md"

def extract_example():
    content = ARTICLE.read_text(encoding="utf-8")

    section = re.search(
        r"## Constructing a formatter(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert section, "Could not find 'Constructing a formatter' section"

    code = re.search(r"```js\s*\n(.*?)\n```", section.group(1), re.DOTALL)
    assert code, "Could not find JavaScript example"

    return code.group(1)

def run_example(source):
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".js",
        encoding="utf-8",
    ) as script:
        script.write(source)
        script.flush()

        result = subprocess.run(
            ["node", script.name],
            capture_output=True,
            text=True,
            check=True,
        )

    return result.stdout.strip().splitlines()

def validate(actual, expected):
    assert actual == expected, (
        f"Output mismatch:\nExpected: {expected}\nActual: {actual}"
    )

def main():
    source = extract_example()
    actual = run_example(source)

    expected = ["yesterday", "today"]
    validate(actual, expected)

    # Verify that an incorrect expected result is rejected.
    try:
        validate(actual, ["wrong result", "today"])
    except AssertionError:
        pass
    else:
        raise AssertionError("Checker accepted an incorrect expected result")

    print("PASS: Article example produced the expected outputs.")
    print("PASS: Boundary case produced 'today'.")
    print("PASS: Incorrect expected output was rejected.")

if __name__ == "__main__":
    main()