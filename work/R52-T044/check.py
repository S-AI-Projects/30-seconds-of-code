#!/usr/bin/env python3
"""
Check script for R52-T044: singleton-proxy
Extracts and executes the actual changed JavaScript examples from content/snippets/js/s/singleton-proxy.md,
asserts published expected output/state, verifies the singleton identity invariant on the fixture
plus at least 5 bounded variations, and ensures deliberate wrong results fail.
"""

import json
import os
import re
import subprocess
import sys

def run_snippet(js_code1, js_code2, expected_overrides=None):
    # Combine definition and usage code
    runner_script = f"""
{js_code1}

{js_code2}

// Invariant tests on 5 bounded variations:
const var1 = new MySingletonClass();               // 0 args (boundary)
const var2 = new MySingletonClass(12345);           // numeric arg
const var3 = new MySingletonClass({{ mode: 'test' }}); // object arg
const var4 = new MySingletonClass(['a', 'b']);      // array arg
const var5 = new MySingletonClass(null);            // null arg

const results = {{
  firstMsg: myObj.msg,
  secondMsg: myObj2.msg,
  firstEqualsSecond: myObj === myObj2,
  boundaryEqualsFirst: myObj === myObj3,
  var1EqualsFirst: myObj === var1,
  var2EqualsFirst: myObj === var2,
  var3EqualsFirst: myObj === var3,
  var4EqualsFirst: myObj === var4,
  var5EqualsFirst: myObj === var5
}};

console.error('__JSON_START__' + JSON.stringify(results) + '__JSON_END__');
"""

    proc = subprocess.run(
        ["node", "-e", runner_script],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node execution failed with exit code {proc.returncode}:\n{proc.stderr}")

    match = re.search(r"__JSON_START__(.*?)__JSON_END__", proc.stderr)
    if not match:
        raise RuntimeError(f"JSON output delimiter not found in node output:\nstdout: {proc.stdout}\nstderr: {proc.stderr}")

    results = json.loads(match.group(1))

    exp_first_msg = expected_overrides.get("firstMsg", "first") if expected_overrides else "first"
    exp_second_msg = expected_overrides.get("secondMsg", "first") if expected_overrides else "first"
    exp_identity = expected_overrides.get("firstEqualsSecond", True) if expected_overrides else True

    assert results["firstMsg"] == exp_first_msg, f"Expected firstMsg={exp_first_msg!r}, got {results['firstMsg']!r}"
    assert results["secondMsg"] == exp_second_msg, f"Expected secondMsg={exp_second_msg!r}, got {results['secondMsg']!r}"
    assert results["firstEqualsSecond"] is exp_identity, f"Expected identity={exp_identity}, got {results['firstEqualsSecond']}"
    assert results["boundaryEqualsFirst"] is True, "Expected boundary case myObj === myObj3 to be true"

    # Verify invariant across all 5 bounded variations:
    assert results["var1EqualsFirst"] is True, "Variation 1 (0 args) failed singleton invariant"
    assert results["var2EqualsFirst"] is True, "Variation 2 (number) failed singleton invariant"
    assert results["var3EqualsFirst"] is True, "Variation 3 (object) failed singleton invariant"
    assert results["var4EqualsFirst"] is True, "Variation 4 (array) failed singleton invariant"
    assert results["var5EqualsFirst"] is True, "Variation 5 (null) failed singleton invariant"

    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(os.path.join(base_dir, "S-AI-Project")):
        proj_dir = os.path.join(base_dir, "S-AI-Project")
    else:
        proj_dir = base_dir

    snippet_path = os.path.join(proj_dir, "content", "snippets", "js", "s", "singleton-proxy.md")
    if not os.path.isfile(snippet_path):
        print(f"ERROR: Snippet file not found: {snippet_path}", file=sys.stderr)
        sys.exit(1)

    with open(snippet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract JavaScript blocks
    code_blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
    if len(code_blocks) < 2:
        print(f"ERROR: Expected at least 2 JavaScript blocks, found {len(code_blocks)}", file=sys.stderr)
        sys.exit(1)

    js_code1 = code_blocks[0]
    js_code2 = code_blocks[1]

    # Verify critical anchor strings
    if "const singletonify = (className) =>" not in js_code1:
        print("ERROR: singletonify definition missing from block 1", file=sys.stderr)
        sys.exit(1)

    required_lines = [
        "const myObj = new MySingletonClass('first');",
        "const myObj2 = new MySingletonClass('second');",
        "const myObj3 = new MySingletonClass();",
        "myObj === myObj3;",
    ]
    for line in required_lines:
        if line not in js_code2:
            print(f"ERROR: Required line missing from snippet: {line}", file=sys.stderr)
            sys.exit(1)

    # 1. Run actual extracted snippet
    actual_results = run_snippet(js_code1, js_code2)
    print(f"PASS: Actual snippet execution and invariant verified: {actual_results}")

    # 2. Test deliberate wrong expectation fails
    failed_on_wrong = False
    try:
        run_snippet(js_code1, js_code2, expected_overrides={"firstEqualsSecond": False})
    except AssertionError:
        failed_on_wrong = True

    if not failed_on_wrong:
        print("ERROR: Check did not fail on deliberate wrong identity expectation!", file=sys.stderr)
        sys.exit(1)

    failed_on_wrong_msg = False
    try:
        run_snippet(js_code1, js_code2, expected_overrides={"secondMsg": "second"})
    except AssertionError:
        failed_on_wrong_msg = True

    if not failed_on_wrong_msg:
        print("ERROR: Check did not fail on deliberate wrong secondMsg expectation!", file=sys.stderr)
        sys.exit(1)

    print("PASS: Deliberate wrong assertions correctly triggered non-zero failures.")
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    main()
