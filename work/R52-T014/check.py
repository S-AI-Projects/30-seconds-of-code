#!/usr/bin/env python3
"""
R52-T014 · check.py
====================
Extracts the first ```js code block from the authoritative article
  content/snippets/js/s/initialize-array-with-range.md
  (section: "Initialize array with a numeric range", anchor: range)
and executes it with Node.js, asserting:

  Invariant: for range(end, start=0, step=1)
    - result.length === Math.ceil((end - start) / step)  [or 0 when end <= start]
    - result[i]     === start + i * step                 for all i

  Tested on the article's three literal examples + five bounded variations
  plus the boundary case (empty range).

Exits non-zero on any assertion failure or subprocess error.
"""

import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARTICLE   = os.path.join(
    REPO_ROOT, "content", "snippets", "js", "s", "initialize-array-with-range.md"
)

# ---------------------------------------------------------------------------
# 1. Extract the FIRST ```js ... ``` fence (range function + examples)
# ---------------------------------------------------------------------------
def extract_first_js_block(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    m = re.search(r"```js\n(.*?)```", source, re.DOTALL)
    if not m:
        sys.exit(f"ERROR: no ```js code block found in {path}")
    return m.group(1)


# ---------------------------------------------------------------------------
# 2. Build assertion harness
# ---------------------------------------------------------------------------
def build_harness(article_code: str) -> str:
    return r"""
// ---- Article code (verbatim from initialize-array-with-range.md, first js block) ----
{code}

// ---- Assertion harness (R52-T014/check.py) ----
let failures = 0;

function assert(label, actual, expected) {{
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a !== e) {{
    console.error('[FAIL] ' + label);
    console.error('  expected: ' + e);
    console.error('  actual:   ' + a);
    failures++;
    process.exitCode = 1;
  }} else {{
    console.log('[PASS] ' + label);
  }}
}}

// Invariant checker: every element === start + i*step AND length is correct
function checkInvariant(label, end, start = 0, step = 1) {{
  const r = range(end, start, step);
  const expLen = Math.max(0, Math.ceil((end - start) / step));
  assert(label + ' length', r.length, expLen);
  r.forEach((v, i) => {{
    const exp = +(start + i * step).toFixed(10); // avoid float drift
    const got = +v.toFixed(10);
    if (got !== exp) {{
      console.error('[FAIL] ' + label + ' element[' + i + '] expected ' + exp + ' got ' + got);
      failures++;
      process.exitCode = 1;
    }}
  }});
  if (r.every((v, i) => +v.toFixed(10) === +(start + i * step).toFixed(10))) {{
    console.log('[PASS] ' + label + ' invariant (start+i*step)');
  }}
}}

// --- Article's three literal examples ---
assert('range(5)',       range(5),       [0, 1, 2, 3, 4]);
assert('range(7, 3)',    range(7, 3),    [3, 4, 5, 6]);
assert('range(9, 0, 2)', range(9, 0, 2), [0, 2, 4, 6, 8]);

// --- Boundary: end === start → empty array ---
assert('range(0) empty boundary', range(0), []);

// --- Five bounded variations exercising the invariant ---
checkInvariant('range(1)',         1);           // single element [0]
checkInvariant('range(3,1,5)',     3, 1, 5);     // step > gap → [1]
checkInvariant('range(10,1,3)',    10, 1, 3);    // [1,4,7]
checkInvariant('range(6,2,2)',     6, 2, 2);     // [2,4]
checkInvariant('range(100,0,25)', 100, 0, 25);   // [0,25,50,75]

// --- Deliberate wrong-result probe ---
(function() {{
  const savedFailures = failures;
  const savedCode = process.exitCode;
  // temporarily suppress real failure tracking
  const probeResult = JSON.stringify(range(5)) !== JSON.stringify([9, 9, 9, 9, 9]);
  if (probeResult) {{
    console.error('[FAIL] deliberate-wrong-result-probe');
    console.error('  expected: [9,9,9,9,9]');
    console.error('  actual:   ' + JSON.stringify(range(5)));
    console.log('[PASS] deliberate-wrong-result-probe correctly detected');
    // restore: real failures unchanged
    failures = savedFailures;
    process.exitCode = failures > 0 ? 1 : savedCode;
  }} else {{
    console.error('[FAIL] deliberate-wrong-result-probe was NOT detected – harness broken');
    process.exitCode = 1;
  }}
}})();
""".format(code=article_code.rstrip())


# ---------------------------------------------------------------------------
# 3. Run under Node.js
# ---------------------------------------------------------------------------
def run_node(js_source: str) -> int:
    result = subprocess.run(
        ["node", "--input-type=module", "-"],
        input=js_source.encode(),
        capture_output=False,
    )
    return result.returncode


# ---------------------------------------------------------------------------
# 4. Record evidence
# ---------------------------------------------------------------------------
def record_evidence(article_code: str):
    evidence_dir = os.path.dirname(__file__)
    node_ver = subprocess.run(
        ["node", "--version"], capture_output=True, text=True
    ).stdout.strip()

    with open(os.path.join(evidence_dir, "results.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"Node version: {node_ver}\n\n")
        fh.write("=== INPUT (extracted from initialize-array-with-range.md, first js block) ===\n")
        fh.write(article_code)
        fh.write("\n\n=== INVARIANT ===\n")
        fh.write("For range(end, start=0, step=1):\n")
        fh.write("  result.length === Math.ceil((end - start) / step)  (0 when end<=start)\n")
        fh.write("  result[i]     === start + i * step  for all i\n\n")
        fh.write("=== EXPECTED RESULTS ===\n")
        fh.write("range(5)         => [0,1,2,3,4]      (literal article example)\n")
        fh.write("range(7,3)       => [3,4,5,6]         (literal article example)\n")
        fh.write("range(9,0,2)     => [0,2,4,6,8]       (literal article example)\n")
        fh.write("range(0)         => []                 (boundary: end===start)\n")
        fh.write("range(1)         => [0]                (variation: single element)\n")
        fh.write("range(3,1,5)     => [1]                (variation: step > gap)\n")
        fh.write("range(10,1,3)    => [1,4,7]            (variation: custom step)\n")
        fh.write("range(6,2,2)     => [2,4]              (variation: even step)\n")
        fh.write("range(100,0,25)  => [0,25,50,75]       (variation: large step)\n")
        fh.write("deliberate wrong => FAIL detected\n")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    article_code = extract_first_js_block(ARTICLE)
    record_evidence(article_code)
    js = build_harness(article_code)
    rc = run_node(js)
    sys.exit(rc)


if __name__ == "__main__":
    main()
