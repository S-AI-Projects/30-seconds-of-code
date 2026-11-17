import json
import re
import subprocess
import sys
from pathlib import Path

ARTICLE_PATH = Path("content/snippets/js/s/encodeuri-encodeuricomponent.md")
DIST_HTML_PATH = Path("dist/js/s/encodeuri-encodeuricomponent/index.html")
RESULTS_PATH = Path("work/R52-T023/results.json")

EXPECTED_COMPARISON_LINES = [
    "component(part): my-page%23with%2Cspeci%40l%26%2F%22characters%22%3F",
    "uri(part):       my-page#with,speci@l&/%22characters%22?",
    "component(full): https%3A%2F%2Fmy-website.com%2Fmy-page%3Fquery%3D%22a%25b%22%26user%3D1",
    "uri(full):       https://my-website.com/my-page?query=%22a%25b%22&user=1",
    'component(empty): ""',
    'uri(empty):       ""',
    "component(delim): %3B%2C%2F%3F%3A%40%26%3D%2B%24%23",
    "uri(delim):       ;,/?:@&=+$#",
]


def get_tool_version(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def extract_js_blocks(markdown_text):
    blocks = re.findall(r"```js\n(.*?)```", markdown_text, flags=re.DOTALL)
    if len(blocks) < 3:
        raise AssertionError(f"Expected at least 3 ```js``` blocks in {ARTICLE_PATH}, found {len(blocks)}")
    return blocks


def run_node(code):
    proc = subprocess.run(
        ["node", "-"],
        input=code,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.rstrip() for line in proc.stdout.splitlines()]


def verify_inline_comment_block(block_text):
    lines = block_text.strip().splitlines()
    setup_lines = []
    checks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("const "):
            setup_lines.append(line)
        elif (line.startswith("encodeURIComponent(") or line.startswith("encodeURI(")) and i + 1 < len(lines):
            expr = line.split(";")[0].strip()
            comment_line = lines[i + 1].strip()
            match = re.match(r"^//\s*'(.*)'$", comment_line)
            if not match:
                raise AssertionError(f"Missing expected single-quoted comment after: {line}")
            checks.append((expr, match.group(1)))
            i += 1
        i += 1

    if len(checks) != 2:
        raise AssertionError(f"Expected 2 inline expression checks per worked block, found {len(checks)}")

    script = "\n".join(setup_lines + [f"console.log({expr});" for expr, _ in checks]) + "\n"
    actual = run_node(script)
    expected = [exp for _, exp in checks]
    return {
        "expressions": [expr for expr, _ in checks],
        "expected": expected,
        "actual": actual,
        "passed": actual == expected,
    }


def extract_documented_output(block_text):
    output_lines = []
    in_output = False
    for line in block_text.splitlines():
        stripped = line.strip()
        if stripped == "// Output:":
            in_output = True
            continue
        if in_output and stripped.startswith("// "):
            output_lines.append(stripped[3:])
    return output_lines


def run_check(expected_lines=None):
    if expected_lines is None:
        expected_lines = EXPECTED_COMPARISON_LINES

    markdown_text = ARTICLE_PATH.read_text(encoding="utf-8")
    blocks = extract_js_blocks(markdown_text)

    block1_result = verify_inline_comment_block(blocks[0])
    block2_result = verify_inline_comment_block(blocks[1])

    comparison_block = blocks[2]
    documented_output = extract_documented_output(comparison_block)
    actual_lines = run_node(comparison_block)

    rendered_checked = False
    if DIST_HTML_PATH.exists():
        html = DIST_HTML_PATH.read_text(encoding="utf-8")
        assert "Comparison and boundary behavior" in html, "Rendered HTML missing comparison section"
        assert "encodeURIComponent" in html and "encodeURI" in html, "Rendered HTML missing method names"
        assert "%3B%2C%2F%3F%3A%40%26%3D%2B%24%23" in html, "Rendered HTML missing delimiter boundary output"
        rendered_checked = True

    passed = (
        block1_result["passed"]
        and block2_result["passed"]
        and documented_output == actual_lines
        and actual_lines == expected_lines
    )

    return {
        "task": "R52-T023",
        "article": str(ARTICLE_PATH),
        "passed": passed,
        "tool_versions": {
            "python": sys.version.split()[0],
            "node": get_tool_version(["node", "--version"]),
            "npm": get_tool_version(["npm", "--version"]),
        },
        "inputs": {
            "partOfURL": 'my-page#with,speci@l&/"characters"?',
            "fullURL": 'https://my-website.com/my-page?query="a%b"&user=1',
            "empty": "",
            "delimiters": ";,/?:@&=+$#",
        },
        "worked_examples": {
            "encodeURIComponent_block": block1_result,
            "encodeURI_block": block2_result,
        },
        "documented_output": documented_output,
        "expected": expected_lines,
        "actual": actual_lines,
        "rendered_html_verified": rendered_checked,
    }


def main():
    if "--negative-test" in sys.argv:
        tampered = list(EXPECTED_COMPARISON_LINES)
        tampered[-1] = "uri(delim):       %3B%2C%2F%3F%3A%40%26%3D%2B%24%23"
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
