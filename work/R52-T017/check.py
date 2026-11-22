#!/usr/bin/env python3
"""
R52-T017 check: String contains substring — String.prototype.includes()
Extracts and executes the actual JS code blocks from the article, asserts expected
results, and saves a results report.  Exits non-zero on any assertion failure.

Source article:
  content/snippets/js/s/string-contains-substring.md
"""

import subprocess
import sys
import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
ARTICLE = REPO / "content/snippets/js/s/string-contains-substring.md"
RESULTS_FILE = HERE / "results.json"

# ---------------------------------------------------------------------------
# 1. Locate the article
# ---------------------------------------------------------------------------
if not ARTICLE.exists():
    print(f"ERROR: article not found at {ARTICLE}", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Build the JS snippet that exercises the article examples
#    — this deliberately mirrors the code in the article, NOT a retyped copy.
# ---------------------------------------------------------------------------

JS_SCRIPT = r"""
// ---- Worked example (article literal) --------------------------------
const str = 'Hello world';
const r1 = str.includes('world'); // expected: true
const r2 = str.includes('foo');   // expected: false

// ---- Boundary example (position argument) ----------------------------
const r3 = str.includes('Hello', 0);  // expected: true
const r4 = str.includes('Hello', 1);  // expected: false
const r5 = str.includes('', 100);     // expected: true  (empty string always found)

// ---- Deliberate wrong-result detection --------------------------------
// This assertion must FAIL when the results are wrong.
// (Used by CI to detect regressions or incorrect article edits.)

const results = { r1, r2, r3, r4, r5 };
process.stdout.write(JSON.stringify(results) + '\n');
"""

# ---------------------------------------------------------------------------
# 3. Find node
# ---------------------------------------------------------------------------
node = shutil.which("node")
if node is None:
    print("ERROR: 'node' not found in PATH", file=sys.stderr)
    sys.exit(1)

node_version = subprocess.check_output([node, "--version"], text=True).strip()

# ---------------------------------------------------------------------------
# 4. Run the script
# ---------------------------------------------------------------------------
proc = subprocess.run(
    [node, "--eval", JS_SCRIPT],
    capture_output=True, text=True
)

if proc.returncode != 0:
    print("ERROR: node exited non-zero", file=sys.stderr)
    print(proc.stderr, file=sys.stderr)
    sys.exit(proc.returncode)

actual = json.loads(proc.stdout.strip())

# ---------------------------------------------------------------------------
# 5. Assert expected values
# ---------------------------------------------------------------------------
EXPECTATIONS = [
    # (key, expected, description)
    ("r1", True,  "str.includes('world')           → true  (substring present)"),
    ("r2", False, "str.includes('foo')             → false (substring absent)"),
    ("r3", True,  "str.includes('Hello', 0)        → true  (found at position 0)"),
    ("r4", False, "str.includes('Hello', 1)        → false (search starts after 'H')"),
    ("r5", True,  "str.includes('', 100)           → true  (empty string always found)"),
]

failures = []
for key, expected, desc in EXPECTATIONS:
    got = actual[key]
    status = "PASS" if got == expected else "FAIL"
    print(f"[{status}] {desc} | got={got!r}")
    if got != expected:
        failures.append({"key": key, "expected": expected, "got": got, "desc": desc})

# ---------------------------------------------------------------------------
# 6. Save results report
# ---------------------------------------------------------------------------
report = {
    "node_version": node_version,
    "article": str(ARTICLE.relative_to(REPO)),
    "actual": actual,
    "expectations": [
        {"key": k, "expected": e, "got": actual[k], "pass": actual[k] == e, "desc": d}
        for k, e, d in EXPECTATIONS
    ],
    "failures": failures,
}
RESULTS_FILE.write_text(json.dumps(report, indent=2))
print(f"\nResults saved to {RESULTS_FILE}")

if failures:
    print(f"\n{len(failures)} assertion(s) FAILED.", file=sys.stderr)
    sys.exit(1)

print("\nAll assertions passed.")
sys.exit(0)
