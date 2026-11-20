#!/usr/bin/env python3
"""
Check script for R52-T042: prefix-css-property
Extracts and executes the actual changed JavaScript example from content/snippets/js/s/prefix-css-property.md,
asserts published expected output/state, tests boundary conditions, and ensures deliberate wrong results fail.
"""

import json
import os
import re
import subprocess
import sys

def run_snippet(js_code, expected_overrides=None):
    runner_script = f"""
// Mock DOM environment for Document.body.style
const mockStyle = {{
  appearance: 'auto',
  webkitAppearance: 'auto'
}};

global.document = {{
  body: {{
    style: mockStyle
  }}
}};

// Run the extracted code
{js_code}

const results = {{
  appearance: prefix('appearance'),
  nonExistent: prefix('nonExistentProperty')
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

    exp_appearance = expected_overrides.get("appearance", "appearance") if expected_overrides else "appearance"
    exp_non_existent = expected_overrides.get("nonExistent", None) if expected_overrides else None

    assert results["appearance"] == exp_appearance, f"Expected appearance={exp_appearance!r}, got {results['appearance']!r}"
    assert results["nonExistent"] == exp_non_existent, f"Expected nonExistent={exp_non_existent!r}, got {results['nonExistent']!r}"

    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(os.path.join(base_dir, "S-AI-Project")):
        proj_dir = os.path.join(base_dir, "S-AI-Project")
    else:
        proj_dir = base_dir

    snippet_path = os.path.join(proj_dir, "content", "snippets", "js", "s", "prefix-css-property.md")
    if not os.path.isfile(snippet_path):
        print(f"ERROR: Snippet file not found: {snippet_path}", file=sys.stderr)
        sys.exit(1)

    with open(snippet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract the main implementation code block (block containing `const prefix = prop =>`)
    code_blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
    if not code_blocks:
        print("ERROR: No JavaScript code blocks found in snippet", file=sys.stderr)
        sys.exit(1)

    # Find the block containing the prefix function
    prefix_block = None
    for block in code_blocks:
        if "const prefix = prop =>" in block:
            prefix_block = block
            break

    if not prefix_block:
        print("ERROR: Code block containing prefix function not found", file=sys.stderr)
        sys.exit(1)

    # Check key contracts are present in the published snippet
    required_lines = [
        "const prefix = prop => {",
        "prefix('appearance');",
        "prefix('nonExistentProperty'); // null",
    ]
    for line in required_lines:
        if line not in prefix_block:
            print(f"ERROR: Expected code line missing from snippet: {line}", file=sys.stderr)
            sys.exit(1)

    # 1. Run actual extracted snippet and assert results
    actual_results = run_snippet(prefix_block)
    print(f"PASS: Actual snippet execution results verified: {actual_results}")

    # 2. Test deliberate wrong expectation fails for appearance
    failed_on_wrong_appearance = False
    try:
        run_snippet(prefix_block, expected_overrides={"appearance": "deliberate-wrong"})
    except AssertionError:
        failed_on_wrong_appearance = True

    if not failed_on_wrong_appearance:
        print("ERROR: Check did not fail on deliberate wrong appearance expectation!", file=sys.stderr)
        sys.exit(1)

    # 3. Test deliberate wrong expectation fails for nonExistentProperty
    failed_on_wrong_boundary = False
    try:
        run_snippet(prefix_block, expected_overrides={"nonExistent": "fake"})
    except AssertionError:
        failed_on_wrong_boundary = True

    if not failed_on_wrong_boundary:
        print("ERROR: Check did not fail on deliberate wrong boundary expectation!", file=sys.stderr)
        sys.exit(1)

    print("PASS: Deliberate wrong assertions correctly triggered non-zero failures.")
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    main()
