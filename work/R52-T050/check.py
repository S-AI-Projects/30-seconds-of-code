"""
R52-T050 — check-array-values-are-truthy
Extracts JS blocks from content/snippets/js/s/check-array-values-are-truthy.md,
verifies anchor lines, asserts the article's worked examples, boundary case,
and verifies mutation testing (distinguishing arr.every from mutant arr.some).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

MD = Path("content/snippets/js/s/check-array-values-are-truthy.md")
if not MD.exists():
    MD = Path("S-AI-Project/content/snippets/js/s/check-array-values-are-truthy.md")

with open(MD, encoding="utf-8") as fh:
    content = fh.read()

# Extract all fenced ```js blocks
blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
if not blocks:
    raise RuntimeError("No ```js block found in " + str(MD))

# The first block must contain the all definition and worked examples
first_block = blocks[0]
assert "const all = (arr, fn = Boolean) => arr.every(fn);" in first_block, \
    "Anchor line 'const all = (arr, fn = Boolean) => arr.every(fn);' not found in first JS block"
assert "all([4, 2, 3], x => x > 1);" in first_block, \
    "Worked example call all([4, 2, 3], x => x > 1) not found in first JS block"
assert "all([1, 2, 3]);" in first_block, \
    "Worked example call all([1, 2, 3]) not found in first JS block"

# The second block (boundary case) must be present
assert len(blocks) >= 2, "Expected at least 2 JS blocks"
second_block = blocks[1]
assert "all([]);" in second_block, \
    "Boundary call all([]) not found in second JS block"
assert "all([], () => false);" in second_block, \
    "Boundary call all([], () => false) not found in second JS block"

# The third block (regression protection) must be present
assert len(blocks) >= 3, "Expected at least 3 JS blocks"
third_block = blocks[2]
assert "all([1, 0, 3]);" in third_block, \
    "Regression check call all([1, 0, 3]) not found in third JS block"

# Build a Node script that runs assertions and tests the mutant
node_script = first_block + "\n" + second_block + "\n" + third_block + "\n" + """
const mutantSome = (arr, fn = Boolean) => arr.some(fn);

const results = {
  worked1: all([4, 2, 3], x => x > 1),
  worked2: all([1, 2, 3]),
  emptyDefault: all([]),
  emptyFalsePredicate: all([], () => false),
  mixedValues: all([1, 0, 3]),
  mutantMixed: mutantSome([1, 0, 3]),
  mutantEmpty: mutantSome([])
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

# --- Assertion 1: worked examples ---
assert data["worked1"] is True, f"Worked example 1 FAILED: {data['worked1']}"
print("PASS  worked example 1: all([4, 2, 3], x => x > 1) == true")

assert data["worked2"] is True, f"Worked example 2 FAILED: {data['worked2']}"
print("PASS  worked example 2: all([1, 2, 3]) == true")

# --- Assertion 2: boundary cases (empty array) ---
assert data["emptyDefault"] is True, f"Boundary case empty array FAILED: {data['emptyDefault']}"
print("PASS  boundary case: all([]) == true (vacuous truth)")

assert data["emptyFalsePredicate"] is True, f"Boundary case with false predicate FAILED: {data['emptyFalsePredicate']}"
print("PASS  boundary case: all([], () => false) == true")

# --- Assertion 3: regression check (mixed truthy/falsy) ---
assert data["mixedValues"] is False, f"Regression check mixed values FAILED: {data['mixedValues']}"
print("PASS  regression check: all([1, 0, 3]) == false")

# --- Assertion 4: mutant killed ---
# The mutant (arr.some) returns true on [1, 0, 3], which differs from correct all implementation (false)
assert data["mutantMixed"] is True, "Mutant did not return true on mixed array"
assert data["mutantMixed"] != data["mixedValues"], \
    "Mutant was NOT distinguished from correct implementation on mixed array!"
print("PASS  mutant (arr.some) killed on [1, 0, 3]: mutant returned true, correct all returned false")

# Mutant also fails on empty array (returns false instead of true)
assert data["mutantEmpty"] is False, "Mutant did not return false on empty array"
assert data["mutantEmpty"] != data["emptyDefault"], \
    "Mutant was NOT distinguished on empty array!"
print("PASS  mutant (arr.some) killed on empty array: mutant returned false, correct all returned true")

# --- Deliberate wrong assertion (must fail) ---
try:
    assert data["worked1"] is False, "deliberate failure"
    raise RuntimeError("Deliberate wrong assertion did NOT fail — test harness is broken!")
except AssertionError:
    print("PASS  deliberate wrong assertion correctly raises AssertionError")

print("\nAll checks passed for R52-T050.")
