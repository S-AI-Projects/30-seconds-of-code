"""
R52-T048 — transpose-matrix
Extracts JS blocks from transpose-matrix.md, verifies anchor lines, and asserts
the article's worked example plus a single-row boundary case.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

MD = str(Path(__file__).resolve().parents[2] / "content/snippets/js/s/transpose-matrix.md")

with open(MD, encoding="utf-8") as fh:
    content = fh.read()

# Extract all fenced ```js blocks
blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
if not blocks:
    raise RuntimeError("No ```js block found in " + MD)

# The first block must contain the transpose definition
first_block = blocks[0]
assert "const transpose = arr => arr[0].map" in first_block, \
    "Anchor line 'const transpose = arr => arr[0].map' not found in first JS block"
assert "transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])" in first_block, \
    "Worked-example call not found in first JS block"

# The second block (boundary case) must be present
assert len(blocks) >= 2, "Expected at least 2 JS blocks (worked example + boundary case)"
second_block = blocks[1]
assert "transpose([[1, 2, 3]])" in second_block, \
    "Single-row boundary call not found in second JS block"

# Build a Node script that runs both assertions and reports JSON via stderr sentinel
node_script = first_block + "\n" + """
const results = {
  worked: transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]),
  singleRow: transpose([[1, 2, 3]])
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

# --- Assertion 1: worked example ---
expected_worked = [[1,4,7,10],[2,5,8,11],[3,6,9,12]]
assert data["worked"] == expected_worked, \
    f"Worked example FAILED.\nGot:      {data['worked']}\nExpected: {expected_worked}"
print("PASS  worked example: transpose([[1,2,3],[4,5,6],[7,8,9],[10,11,12]]) ==", expected_worked)

# --- Assertion 2: single-row boundary ---
expected_single = [[1],[2],[3]]
assert data["singleRow"] == expected_single, \
    f"Single-row boundary FAILED.\nGot:      {data['singleRow']}\nExpected: {expected_single}"
print("PASS  single-row boundary: transpose([[1,2,3]]) ==", expected_single)

# --- Deliberate wrong assertion (must fail) ---
try:
    assert data["worked"] == [[99]], "deliberate failure"
    raise RuntimeError("Deliberate wrong assertion did NOT fail — test harness is broken!")
except AssertionError:
    print("PASS  deliberate wrong assertion correctly raises AssertionError")

print("\nAll checks passed for R52-T048.")
