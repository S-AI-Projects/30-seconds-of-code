#!/usr/bin/env python3
"""
Check script for R52-T046: value-as-number
Extracts and executes the actual changed JavaScript example from content/snippets/js/s/value-as-number.md.
Tests parseFloat vs valueAsNumber on literal numeric input, validates intermediate annotated values,
and verifies boundary behavior when value is empty (returning NaN).
"""

import json
import os
import re
import subprocess
import sys

def run_snippet(js_code, expected_overrides=None):
    runner_script = f"""
class MockHTMLInputElement {{
  constructor(id, type = 'number', value = '') {{
    this.id = id;
    this.type = type;
    this.value = value;
  }}
  get valueAsNumber() {{
    if (this.type !== 'number') return NaN;
    if (this.value === '') return NaN;
    const num = Number(this.value);
    return Number.isNaN(num) ? NaN : num;
  }}
}}

const elements = new Map([
  ['quantity-input', new MockHTMLInputElement('quantity-input', 'number', '42.5')],
  ['empty-input', new MockHTMLInputElement('empty-input', 'number', '')]
]);

global.document = {{
  getElementById: (id) => elements.get(id) || null
}};

// Execute the extracted snippet
{js_code}

const results = {{
  parsedQuantity: quantity,
  quantityValue: quantityInput.value,
  directValueAsNumber: quantityInput.valueAsNumber,
  emptyValueAsNumberIsNaN: Number.isNaN(emptyInput.valueAsNumber)
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

    exp_quantity = expected_overrides.get("parsedQuantity", 42.5) if expected_overrides else 42.5
    exp_nan = expected_overrides.get("emptyValueAsNumberIsNaN", True) if expected_overrides else True

    assert results["parsedQuantity"] == exp_quantity, f"Expected parsedQuantity={exp_quantity}, got {results['parsedQuantity']}"
    assert results["quantityValue"] == "42.5", f"Expected intermediate string '42.5', got {results['quantityValue']!r}"
    assert results["directValueAsNumber"] == exp_quantity, f"Expected directValueAsNumber={exp_quantity}, got {results['directValueAsNumber']}"
    assert results["emptyValueAsNumberIsNaN"] is exp_nan, f"Expected emptyValueAsNumberIsNaN={exp_nan}, got {results['emptyValueAsNumberIsNaN']}"

    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(os.path.join(base_dir, "S-AI-Project")):
        proj_dir = os.path.join(base_dir, "S-AI-Project")
    else:
        proj_dir = base_dir

    snippet_path = os.path.join(proj_dir, "content", "snippets", "js", "s", "value-as-number.md")
    if not os.path.isfile(snippet_path):
        print(f"ERROR: Snippet file not found: {snippet_path}", file=sys.stderr)
        sys.exit(1)

    with open(snippet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract JavaScript blocks
    code_blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
    if not code_blocks:
        print("ERROR: No JavaScript code blocks found in snippet", file=sys.stderr)
        sys.exit(1)

    js_code = code_blocks[0]

    # Verify critical anchor strings
    required_lines = [
        "const quantityInput = document.getElementById('quantity-input');",
        "quantity = parseFloat(quantityInput.value);",
        "quantity = quantityInput.valueAsNumber;",
        "emptyInput.valueAsNumber; // NaN",
    ]
    for line in required_lines:
        if line not in js_code:
            print(f"ERROR: Required line missing from snippet: {line}", file=sys.stderr)
            sys.exit(1)

    # 1. Run actual extracted snippet
    actual_results = run_snippet(js_code)
    print(f"PASS: Actual snippet execution results verified: {actual_results}")

    # 2. Test deliberate wrong expectation fails
    failed_on_wrong = False
    try:
        run_snippet(js_code, expected_overrides={"parsedQuantity": 999})
    except AssertionError:
        failed_on_wrong = True

    if not failed_on_wrong:
        print("ERROR: Check did not fail on deliberate wrong expectation!", file=sys.stderr)
        sys.exit(1)

    print("PASS: Deliberate wrong assertions correctly triggered non-zero failures.")
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    main()
