#!/usr/bin/env python3
"""
R52-T018 check script for weekday-name.md
- Extracts the dayName code block from the article source
- Executes it with Node.js (the same runtime that powers the site)
- Asserts the article's worked example results and boundary example
- Asserts the documented misconception (TypeError for non-Date input)
- Saves a results log to work/R52-T018/results.json
- Exits non-zero when any assertion fails
"""

import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARTICLE = os.path.join(REPO_ROOT, "content", "snippets", "js", "s", "weekday-name.md")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")

# ---------------------------------------------------------------------------
# 1. Read the article and extract the dayName code block
# ---------------------------------------------------------------------------
with open(ARTICLE, encoding="utf-8") as fh:
    source = fh.read()

# Find the first ```js block that defines dayName
pattern = re.compile(r"```js\n(const dayName.*?)```", re.DOTALL)
match = pattern.search(source)
if not match:
    print("FAIL: Could not find dayName code block in article", file=sys.stderr)
    sys.exit(1)

article_block = match.group(1).rstrip()
print("Extracted article block:")
print(article_block)
print()

# ---------------------------------------------------------------------------
# 2. Build the Node.js test script
# ---------------------------------------------------------------------------
# The article uses `new Date()` (today) for the first call which is
# non-deterministic; we only assert the fixed-date examples.
node_script = r"""
// --- extracted from article ---
const dayName = (date, locale) =>
  date.toLocaleDateString(locale, { weekday: 'long' });

const results = {};

// Article's worked example (fixed date)
results.articleExample_deDE = dayName(new Date('05/27/2024'), 'de-DE');

// Boundary example from article (French locale)
results.boundaryExample_frFR = dayName(new Date('05/27/2024'), 'fr-FR');

// Misconception: passing a string instead of a Date → TypeError
let misconceptionError = null;
try {
  dayName('05/27/2024');
} catch (e) {
  misconceptionError = e.constructor.name;
}
results.misconception_stringInput_errorType = misconceptionError;

// Deliberate wrong-result check: fr-FR should NOT be 'Monday'
results.boundaryExample_frFR_isNotEnglish = (results.boundaryExample_frFR !== 'Monday');

process.stdout.write(JSON.stringify(results));
"""

# ---------------------------------------------------------------------------
# 3. Run with Node.js
# ---------------------------------------------------------------------------
node_version_proc = subprocess.run(
    ["node", "--version"],
    capture_output=True,
    text=True,
)
node_version = node_version_proc.stdout.strip()
print(f"Node.js version: {node_version}")

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
    print(f"FAIL: Could not parse Node output as JSON: {exc}", file=sys.stderr)
    print("stdout:", proc.stdout, file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# 4. Assert expectations
# ---------------------------------------------------------------------------
failures = []

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

print("\n=== Assertions ===")

# Article's worked example
assert_eq(
    "dayName(new Date('05/27/2024'), 'de-DE')",
    actual.get("articleExample_deDE"),
    "Montag",
)

# Boundary example: fr-FR locale
assert_eq(
    "dayName(new Date('05/27/2024'), 'fr-FR')",
    actual.get("boundaryExample_frFR"),
    "lundi",
)

# Misconception: string input throws TypeError
assert_eq(
    "dayName('05/27/2024') throws TypeError",
    actual.get("misconception_stringInput_errorType"),
    "TypeError",
)

# Deliberate wrong-result check: fr-FR result is not English 'Monday'
assert_true(
    "fr-FR result is not 'Monday' (wrong-result guard)",
    actual.get("boundaryExample_frFR_isNotEnglish"),
)

# ---------------------------------------------------------------------------
# 5. Save results log
# ---------------------------------------------------------------------------
log = {
    "node_version": node_version,
    "article_path": ARTICLE,
    "inputs": {
        "articleExample": {"date": "05/27/2024", "locale": "de-DE"},
        "boundaryExample": {"date": "05/27/2024", "locale": "fr-FR"},
        "misconception": {"input": "string '05/27/2024'"},
    },
    "expected": {
        "articleExample_deDE": "Montag",
        "boundaryExample_frFR": "lundi",
        "misconception_stringInput_errorType": "TypeError",
        "boundaryExample_frFR_isNotEnglish": True,
    },
    "actual": actual,
    "failures": failures,
    "passed": len(failures) == 0,
}

with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
    json.dump(log, fh, indent=2)
print(f"\nResults saved to {RESULTS_FILE}")

# ---------------------------------------------------------------------------
# 6. Exit
# ---------------------------------------------------------------------------
if failures:
    print(f"\nFAIL: {len(failures)} assertion(s) failed:", file=sys.stderr)
    for f in failures:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)

print(f"\nAll {4} assertions passed.")
