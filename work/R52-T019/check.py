#!/usr/bin/env python3
"""
R52-T019 check script for indexed-object-collections.md  §Indexes
- Extracts the first ```js code block from the article (the §Indexes collection)
- Runs it via Node.js, asserting article's worked examples and boundary cases
- Also asserts that the original bug (obj vs object) is NOT present in the source
- Saves results to work/R52-T019/results.json
- Exits non-zero when any assertion fails
"""

import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARTICLE = os.path.join(
    REPO_ROOT, "content", "snippets", "js", "s", "indexed-object-collections.md"
)
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")

# ---------------------------------------------------------------------------
# 1. Read the article and extract the §Indexes code block (the first ```js block)
# ---------------------------------------------------------------------------
with open(ARTICLE, encoding="utf-8") as fh:
    source = fh.read()

# Find all ```js blocks; the first one is the §Indexes collection
pattern = re.compile(r"```js\n(.*?)```", re.DOTALL)
blocks = pattern.findall(source)
if not blocks:
    print("FAIL: No ```js blocks found in article", file=sys.stderr)
    sys.exit(1)

article_block = blocks[0].rstrip()
print("Extracted §Indexes code block (first ```js```):")
print(article_block[:300])
print("...")
print()

# ---------------------------------------------------------------------------
# 2. Assert the bug is NOT present (obj parameter should be renamed to object)
# ---------------------------------------------------------------------------
failures = []

bug_present = "forEach((obj)" in article_block
if bug_present:
    failures.append(
        "Bug still present: forEach parameter is 'obj' but body references 'object'. "
        "Should be forEach((object) => ...) to match internal references."
    )
    print("  [FAIL] Bug check: forEach((obj) still present (should be (object))")
else:
    print("  [PASS] Bug check: forEach uses (object) consistently — no obj/object mismatch")

# ---------------------------------------------------------------------------
# 3. Build Node.js test script using the extracted article code
# ---------------------------------------------------------------------------
node_script = article_block + r"""

// --- assertions ---
const results = {};

// Article's worked examples (literal inputs and expected outputs)
results.get_243 = JSON.stringify(collection.get(243));
results.get_400 = JSON.stringify(collection.get(400));
results.get_840 = JSON.stringify(collection.get(840));

// Boundary: get a missing id returns undefined, not an error
results.get_999 = collection.get(999);

// Boundary: index size matches the number of added objects
results.indexSize = collection.index.size;

// Time/space: Map.get is O(1) — verify it finds the last-added item instantly
results.mapGet_works = (collection.get(456) !== undefined);

// Deliberate wrong-result guard: get(243) must NOT be 'Apple'
results.get_243_isNotApple = (JSON.parse(results.get_243).name !== 'Apple');

process.stdout.write(JSON.stringify(results));
"""

# ---------------------------------------------------------------------------
# 4. Run with Node.js
# ---------------------------------------------------------------------------
node_version_proc = subprocess.run(
    ["node", "--version"], capture_output=True, text=True
)
node_version = node_version_proc.stdout.strip()
print(f"Node.js version: {node_version}\n")

proc = subprocess.run(
    ["node", "--input-type=module"],
    input=node_script,
    capture_output=True,
    text=True,
)

if proc.returncode != 0:
    print("FAIL: Node.js exited non-zero", file=sys.stderr)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)

try:
    actual = json.loads(proc.stdout)
except json.JSONDecodeError as exc:
    print(f"FAIL: Could not parse Node output: {exc}", file=sys.stderr)
    print("stdout:", proc.stdout, file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# 5. Assert expectations
# ---------------------------------------------------------------------------
def assert_eq(label, got, expected):
    status = "PASS" if got == expected else "FAIL"
    if status == "FAIL":
        failures.append(f"{label}: expected {expected!r}, got {got!r}")
    print(f"  [{status}] {label}: {got!r} (expected {expected!r})")

def assert_true(label, value):
    status = "PASS" if value else "FAIL"
    if status == "FAIL":
        failures.append(f"{label}: expected truthy, got {value!r}")
    print(f"  [{status}] {label}: {value!r}")

def assert_none(label, value):
    status = "PASS" if value is None else "FAIL"
    if status == "FAIL":
        failures.append(f"{label}: expected None/undefined, got {value!r}")
    print(f"  [{status}] {label}: {value!r} (expected undefined/None)")

print("=== Assertions ===")

# Article's worked examples
assert_eq(
    "collection.get(243)",
    actual.get("get_243"),
    '{"id":243,"name":"Cherry"}',
)
assert_eq(
    "collection.get(400)",
    actual.get("get_400"),
    '{"id":400,"name":"Apple"}',
)
assert_eq(
    "collection.get(840)",
    actual.get("get_840"),
    '{"id":840,"name":"Banana"}',
)

# Boundary: missing id → undefined (None in JSON)
assert_none(
    "collection.get(999) → undefined (missing id boundary)",
    actual.get("get_999"),
)

# Index size matches number of added objects
assert_eq(
    "collection.index.size (5 objects added)",
    actual.get("indexSize"),
    5,
)

# Map.get works for last-inserted item
assert_true(
    "collection.get(456) is defined (Map O(1) lookup works)",
    actual.get("mapGet_works"),
)

# Wrong-result guard
assert_true(
    "get(243).name is not 'Apple' (wrong-result guard)",
    actual.get("get_243_isNotApple"),
)

# ---------------------------------------------------------------------------
# 6. Save results log
# ---------------------------------------------------------------------------
log = {
    "node_version": node_version,
    "article_path": ARTICLE,
    "bug_check": {
        "description": "forEach parameter must be 'object' not 'obj' to match body references",
        "passed": not bug_present,
    },
    "inputs": {
        "articleExample_1": {"id": 243, "expected_name": "Cherry"},
        "articleExample_2": {"id": 400, "expected_name": "Apple"},
        "articleExample_3": {"id": 840, "expected_name": "Banana"},
        "boundary_missing": {"id": 999, "expected": "undefined"},
        "boundary_indexSize": {"added": 5, "expected_size": 5},
    },
    "actual": actual,
    "failures": failures,
    "passed": len(failures) == 0,
}

with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
    json.dump(log, fh, indent=2)
print(f"\nResults saved to {RESULTS_FILE}")

# ---------------------------------------------------------------------------
# 7. Exit
# ---------------------------------------------------------------------------
if failures:
    print(f"\nFAIL: {len(failures)} assertion(s) failed:", file=sys.stderr)
    for f in failures:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)

print(f"\nAll {7} assertions passed.")
