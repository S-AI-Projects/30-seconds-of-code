#!/usr/bin/env python3
"""
Check script for R52-T043: enum
Extracts and executes the actual changed JavaScript examples from content/snippets/js/s/enum.md,
asserts published expected output/state, tests boundary conditions, and ensures deliberate wrong results fail.
"""

import json
import os
import re
import subprocess
import sys

def run_snippet(js_code, expected_overrides=None):
    runner_script = f"""
{js_code}

const results = {{
  daysEnum_monday: daysEnum.monday,
  daysEnum_sunday: daysEnum.sunday,
  daysEnum_frozen: Object.isFrozen(daysEnum),
  daysEnumAlt_monday: daysEnumAlt.monday,
  daysEnumAlt_sunday: daysEnumAlt.sunday,
  daysEnumAlt_frozen: Object.isFrozen(daysEnumAlt),
  daysEnum_equals_daysEnumAlt: JSON.stringify(daysEnum) === JSON.stringify(daysEnumAlt),
  emptyEnum_frozen: Object.isFrozen(emptyEnum),
  emptyEnumAlt_frozen: Object.isFrozen(emptyEnumAlt),
  emptyEnum_equals_emptyEnumAlt: JSON.stringify(emptyEnum) === JSON.stringify(emptyEnumAlt),
  emptyEnum_keys_count: Object.keys(emptyEnum).length,
  emptyEnumAlt_keys_count: Object.keys(emptyEnumAlt).length
}};

console.log(JSON.stringify(results));
"""

    proc = subprocess.run(
        ["node", "-e", runner_script],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node execution failed with exit code {proc.returncode}:\n{proc.stderr}")

    results = json.loads(proc.stdout.strip())

    exp_monday = expected_overrides.get("monday", 0) if expected_overrides else 0
    exp_sunday = expected_overrides.get("sunday", 6) if expected_overrides else 6
    exp_alt_equals = expected_overrides.get("equals", True) if expected_overrides else True

    assert results["daysEnum_monday"] == exp_monday, f"Expected daysEnum.monday={exp_monday}, got {results['daysEnum_monday']}"
    assert results["daysEnum_sunday"] == exp_sunday, f"Expected daysEnum.sunday={exp_sunday}, got {results['daysEnum_sunday']}"
    assert results["daysEnum_frozen"] is True, "Expected daysEnum to be frozen"
    assert results["daysEnumAlt_monday"] == exp_monday, f"Expected daysEnumAlt.monday={exp_monday}, got {results['daysEnumAlt_monday']}"
    assert results["daysEnumAlt_sunday"] == exp_sunday, f"Expected daysEnumAlt.sunday={exp_sunday}, got {results['daysEnumAlt_sunday']}"
    assert results["daysEnumAlt_frozen"] is True, "Expected daysEnumAlt to be frozen"
    assert results["daysEnum_equals_daysEnumAlt"] is exp_alt_equals, f"Expected comparison equality={exp_alt_equals}, got {results['daysEnum_equals_daysEnumAlt']}"

    assert results["emptyEnum_frozen"] is True, "Expected emptyEnum to be frozen"
    assert results["emptyEnumAlt_frozen"] is True, "Expected emptyEnumAlt to be frozen"
    assert results["emptyEnum_equals_emptyEnumAlt"] is True, "Expected empty enums to match"
    assert results["emptyEnum_keys_count"] == 0, "Expected emptyEnum to have 0 keys"
    assert results["emptyEnumAlt_keys_count"] == 0, "Expected emptyEnumAlt to have 0 keys"

    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(os.path.join(base_dir, "S-AI-Project")):
        proj_dir = os.path.join(base_dir, "S-AI-Project")
    else:
        proj_dir = base_dir

    snippet_path = os.path.join(proj_dir, "content", "snippets", "js", "s", "enum.md")
    if not os.path.isfile(snippet_path):
        print(f"ERROR: Snippet file not found: {snippet_path}", file=sys.stderr)
        sys.exit(1)

    with open(snippet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract first js block
    code_blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
    if not code_blocks:
        print("ERROR: No JavaScript code blocks found in snippet", file=sys.stderr)
        sys.exit(1)

    block1 = code_blocks[0]

    # Verify literal target code is present
    required_lines = [
        "const daysEnum = Object.freeze({",
        "monday: 0,",
        "tuesday: 1,",
        "wednesday: 2,",
        "thursday: 3,",
        "friday: 4,",
        "saturday: 5,",
        "sunday: 6",
        "const createEnum = (...keys) =>",
        "const emptyEnum = Object.freeze({});",
        "const emptyEnumAlt = createEnum();",
    ]
    for line in required_lines:
        if line not in block1:
            print(f"ERROR: Required code line missing from snippet: {line}", file=sys.stderr)
            sys.exit(1)

    # 1. Run actual extracted snippet
    actual_results = run_snippet(block1)
    print(f"PASS: Actual snippet execution results verified: {actual_results}")

    # 2. Test deliberate wrong expectation fails
    failed_on_wrong = False
    try:
        run_snippet(block1, expected_overrides={"monday": 999})
    except AssertionError:
        failed_on_wrong = True

    if not failed_on_wrong:
        print("ERROR: Check did not fail on deliberate wrong expectation!", file=sys.stderr)
        sys.exit(1)

    failed_on_wrong_equality = False
    try:
        run_snippet(block1, expected_overrides={"equals": False})
    except AssertionError:
        failed_on_wrong_equality = True

    if not failed_on_wrong_equality:
        print("ERROR: Check did not fail on deliberate wrong comparison expectation!", file=sys.stderr)
        sys.exit(1)

    print("PASS: Deliberate wrong assertions correctly triggered non-zero failures.")
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    main()
