#!/usr/bin/env python3
"""
R52-T020 check script for browser-os-detection.md  §Navigator.platform
- Extracts the isMac code from the §Navigator.platform section of the article
- Simulates navigator.platform with known values and asserts expected results
- Tests the mutant (startsWith instead of includes) and verifies it fails where
  the correct implementation passes — distinguishing the two
- Saves results to work/R52-T020/results.json
- Exits non-zero when any assertion fails

NOTE: navigator.platform is a browser API; we simulate it in Node.js by
injecting a mock global so the extracted code runs without a real browser.
"""

import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARTICLE = os.path.join(
    REPO_ROOT, "content", "snippets", "js", "s", "browser-os-detection.md"
)
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")

# ---------------------------------------------------------------------------
# 1. Read article and extract the §Navigator.platform code block
# ---------------------------------------------------------------------------
with open(ARTICLE, encoding="utf-8") as fh:
    source = fh.read()

# Extract from the Navigator.platform section only (up to the next ##)
platform_section_match = re.search(
    r"## `Navigator\.platform`.*?(?=\n## |\Z)", source, re.DOTALL
)
if not platform_section_match:
    print("FAIL: Could not find §Navigator.platform section", file=sys.stderr)
    sys.exit(1)

platform_section = platform_section_match.group(0)

# Extract the first ```js block from that section (the isMac definition)
js_block_match = re.search(r"```js\n(.*?)```", platform_section, re.DOTALL)
if not js_block_match:
    print("FAIL: No ```js block in §Navigator.platform section", file=sys.stderr)
    sys.exit(1)

article_block = js_block_match.group(1).rstrip()
print("Extracted §Navigator.platform code block:")
print(article_block)
print()

# Extract only the isMac line (not the comment lines)
ismac_line = next(
    (l for l in article_block.splitlines() if l.strip().startswith("const isMac")),
    None,
)
if not ismac_line:
    print("FAIL: Could not find 'const isMac' line in block", file=sys.stderr)
    sys.exit(1)

print(f"isMac line: {ismac_line!r}\n")

# ---------------------------------------------------------------------------
# 2. Build Node.js test script — mock navigator.platform, run isMac
# ---------------------------------------------------------------------------
node_script = r"""
// --- Simulated navigator for Node.js ---
// The article's isMac uses navigator.platform.toLowerCase().includes('mac')
// We inject a mock navigator so the extracted code runs outside the browser.

const results = {};

function testIsMac(platformValue) {
  const navigator = { platform: platformValue };
  """ + ismac_line + r"""
  return isMac;
}

// --- Article's worked example ---
// navigator.platform = 'MacIntel'  → isMac should be true
results.macIntel = testIsMac('MacIntel');

// --- Intermediate values (step-by-step as shown in article) ---
// 'MacIntel'.toLowerCase() === 'macintel'
results.stepLower = 'MacIntel'.toLowerCase();
// 'macintel'.includes('mac') === true
results.stepIncludes = 'macintel'.includes('mac');

// --- Boundary: Windows platform → false ---
results.win32 = testIsMac('Win32');

// --- Boundary: Linux platform → false ---
results.linuxX86 = testIsMac('Linux x86_64');

// --- Ambiguous: iPad on iPadOS 13+ reports 'MacIntel' → true (same as Mac) ---
results.ipadMacIntel = testIsMac('MacIntel');   // true — cannot distinguish from Mac

// --- Mutant test: startsWith instead of includes ---
// The correct implementation uses .includes('mac')
// A one-operation mutant uses .startsWith('mac') instead
// They differ on a string where 'mac' appears but NOT at position 0
function testMutant(platformValue) {
  const navigator = { platform: platformValue };
  // MUTANT: startsWith instead of includes
  const isMac = navigator.platform.toLowerCase().startsWith('mac');
  return isMac;
}

// 'MacIntel' → both agree (mac is at start after toLowerCase)
results.mutant_macIntel_correct = testIsMac('MacIntel');
results.mutant_macIntel_mutant  = testMutant('MacIntel');

// 'something_mac' → includes=true, startsWith=false  ← distinguishing input
results.mutant_distinguish_correct = testIsMac('something_mac');
results.mutant_distinguish_mutant  = testMutant('something_mac');

// --- Wrong-result guard: Win32 must NOT be true ---
results.win32_isNotMac = (results.win32 === false);

process.stdout.write(JSON.stringify(results));
"""

# ---------------------------------------------------------------------------
# 3. Run with Node.js
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

print("=== Assertions ===")

# Article's worked example
assert_eq(
    "isMac with platform='MacIntel' (article example)",
    actual.get("macIntel"),
    True,
)

# Intermediate step values (documents the chain)
assert_eq(
    "'MacIntel'.toLowerCase() intermediate value",
    actual.get("stepLower"),
    "macintel",
)
assert_eq(
    "'macintel'.includes('mac') intermediate value",
    actual.get("stepIncludes"),
    True,
)

# Boundary: non-Mac platforms
assert_eq(
    "isMac with platform='Win32' (boundary: Windows)",
    actual.get("win32"),
    False,
)
assert_eq(
    "isMac with platform='Linux x86_64' (boundary: Linux)",
    actual.get("linuxX86"),
    False,
)

# Mutant distinguishing test
assert_eq(
    "correct .includes('mac') on 'MacIntel'",
    actual.get("mutant_macIntel_correct"),
    True,
)
assert_eq(
    "mutant .startsWith('mac') on 'MacIntel' (same result — not distinguishing)",
    actual.get("mutant_macIntel_mutant"),
    True,
)
assert_eq(
    "correct .includes('mac') on 'something_mac' → True (distinguishing input)",
    actual.get("mutant_distinguish_correct"),
    True,
)
assert_eq(
    "mutant .startsWith('mac') on 'something_mac' → False (mutant FAILS here)",
    actual.get("mutant_distinguish_mutant"),
    False,
)

# Wrong-result guard
assert_true(
    "Win32 isMac is False (wrong-result guard)",
    actual.get("win32_isNotMac"),
)

# ---------------------------------------------------------------------------
# 5. Save results log
# ---------------------------------------------------------------------------
log = {
    "node_version": node_version,
    "article_path": ARTICLE,
    "ismac_line": ismac_line,
    "inputs": {
        "article_example": "platform='MacIntel' → isMac=true",
        "boundary_win32": "platform='Win32' → isMac=false",
        "boundary_linux": "platform='Linux x86_64' → isMac=false",
        "mutant_distinguishing": "platform='something_mac': correct=true, mutant=false",
    },
    "expected": {
        "macIntel": True,
        "stepLower": "macintel",
        "stepIncludes": True,
        "win32": False,
        "linuxX86": False,
        "mutant_macIntel_correct": True,
        "mutant_macIntel_mutant": True,
        "mutant_distinguish_correct": True,
        "mutant_distinguish_mutant": False,
        "win32_isNotMac": True,
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

print(f"\nAll {10} assertions passed.")
