"""
R52-T049 — reorder-function-arguments
Extracts JS blocks from content/snippets/js/s/reorder-function-arguments.md,
verifies anchor lines, and asserts the article's worked example plus a single-argument boundary case.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

MD = Path("content/snippets/js/s/reorder-function-arguments.md")
if not MD.exists():
    MD = Path("S-AI-Project/content/snippets/js/s/reorder-function-arguments.md")

with open(MD, encoding="utf-8") as fh:
    content = fh.read()

# Extract all fenced ```js blocks
blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
if not blocks:
    raise RuntimeError("No ```js block found in " + str(MD))

# The first block must contain the flip definition and worked examples
first_block = blocks[0]
assert "const flip = fn => (first, ...rest) => fn(...rest, first);" in first_block, \
    "Anchor line 'const flip = fn => (first, ...rest) => fn(...rest, first);' not found in first JS block"
assert "const parseInteger = flip(Number.parseInt);" in first_block, \
    "Worked example parseInteger not found in first JS block"
assert "parseInteger(8, '10');" in first_block, \
    "Worked example call parseInteger(8, '10') not found in first JS block"
assert "parseIntegerBase16('10');" in first_block, \
    "Worked example call parseIntegerBase16('10') not found in first JS block"

# The second block (boundary case) must be present
assert len(blocks) >= 2, "Expected at least 2 JS blocks (worked example + boundary case)"
second_block = blocks[1]
assert "identity('hello')" in second_block, \
    "Single-argument boundary call not found in second JS block"

# Build a Node script that runs both assertions and reports JSON via stderr sentinel
node_script = first_block + "\n" + second_block + "\n" + """
const results = {
  worked1: parseInteger(8, '10'),
  worked2: parseIntegerBase16('10'),
  boundary: identity('hello')
};
console.error('__JSON_START__' + JSON.stringify(results) + '__JSON_END__');
"""

proc = subprocess.run(
    ["node", "-e", node_script],
    capture_output=True, text=True
)
if proc.returncode != 0:
    print("STDOUT:", proc.stdout)
    print("STDERR:", proc.stderr)
    raise RuntimeError(f"Node exited with code {proc.returncode}")

m = re.search(r"__JSON_START__(.*?)__JSON_END__", proc.stderr)
if not m:
    raise RuntimeError("JSON sentinel not found in stderr.\nSTDERR: " + proc.stderr)

data = json.loads(m.group(1))

# --- Assertion 1: worked example 1 ---
expected_worked1 = 8
assert data["worked1"] == expected_worked1, \
    f"Worked example 1 FAILED.\nGot:      {data['worked1']}\nExpected: {expected_worked1}"
print("PASS  worked example 1: parseInteger(8, '10') ==", expected_worked1)

# --- Assertion 2: worked example 2 ---
expected_worked2 = 16
assert data["worked2"] == expected_worked2, \
    f"Worked example 2 FAILED.\nGot:      {data['worked2']}\nExpected: {expected_worked2}"
print("PASS  worked example 2: parseIntegerBase16('10') ==", expected_worked2)

# --- Assertion 3: single-argument boundary ---
expected_boundary = 'hello'
assert data["boundary"] == expected_boundary, \
    f"Single-argument boundary FAILED.\nGot:      {data['boundary']}\nExpected: {expected_boundary}"
print("PASS  single-argument boundary: identity('hello') ==", expected_boundary)

# --- Deliberate wrong assertion (must fail) ---
try:
    assert data["worked1"] == 999, "deliberate failure"
    raise RuntimeError("Deliberate wrong assertion did NOT fail — test harness is broken!")
except AssertionError:
    print("PASS  deliberate wrong assertion correctly raises AssertionError")

print("\nAll checks passed for R52-T049.")
