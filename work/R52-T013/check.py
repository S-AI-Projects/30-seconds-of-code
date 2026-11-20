#!/usr/bin/env python3
"""
R52-T013 · check.py
====================
Extracts the SECOND (final) ```js code block from the authoritative article
  content/snippets/js/s/formatting-day-hour-ranges.md
  (section: "Solution" / "Definition", anchor: formatDayRanges)
and executes it with Node.js, asserting that:

  1. The literal worked example (inputData with Tue-Sat) produces the
     exact outputData documented in the article's Definition section.
  2. The boundary example (empty input []) produces ['Everyday: Closed'].
     Intermediate state: reduce groups all 7 days as hours='Closed',
     days.length===7 triggers the 'Everyday' label in the map step.
  3. A deliberate wrong result is detected and causes the check to exit non-zero.

Exits non-zero on any assertion failure or subprocess error.
"""

import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARTICLE   = os.path.join(
    REPO_ROOT, "content", "snippets", "js", "s", "formatting-day-hour-ranges.md"
)

# ---------------------------------------------------------------------------
# 1. Extract all ```js ... ``` fences and combine first + last
#    - First block: defines inputData (from the Definition section)
#    - Last block:  final formatDayRanges + result + boundaryResult
# ---------------------------------------------------------------------------
def extract_js_blocks(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    # Strip highlight markers like ```js {20-28}
    source = re.sub(r"```js \{[^}]+\}", "```js", source)
    blocks = re.findall(r"```js\n(.*?)```", source, re.DOTALL)
    if len(blocks) < 2:
        sys.exit(f"ERROR: expected at least 2 ```js blocks in {path}, found {len(blocks)}")
    # Combine: inputData definition (block 0) + final solution (block -1)
    return blocks[0].rstrip() + "\n\n" + blocks[-1].rstrip()


# ---------------------------------------------------------------------------
# 2. Build assertion harness
# ---------------------------------------------------------------------------
def build_harness(article_code: str) -> str:
    return r"""
// ---- Article code (verbatim from formatting-day-hour-ranges.md, final js block) ----
{code}

// ---- Assertion harness (R52-T013/check.py) ----
function assert(label, actual, expected) {{
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a !== e) {{
    console.error('[FAIL] ' + label);
    console.error('  expected: ' + e);
    console.error('  actual:   ' + a);
    process.exitCode = 1;
  }} else {{
    console.log('[PASS] ' + label);
  }}
}}

// 1. Literal worked example from the article
assert(
  'formatDayRanges(inputData)',
  result,
  ['Monday: Closed', 'Tuesday - Friday: 09:00 - 17:00', 'Saturday: 10:00 - 14:00', 'Sunday: Closed']
);

// 2. Boundary: empty input
//    Intermediate: reduce folds all 7 days into {{ days:[all7], hours:'Closed' }}
//    days.length===7 → map emits 'Everyday: Closed'
assert(
  'formatDayRanges([]) empty-input boundary',
  boundaryResult,
  ['Everyday: Closed']
);

// 3. Deliberate wrong-result probe — must FAIL to prove harness catches errors
(function() {{
  const savedCode = process.exitCode;
  process.exitCode = 0;
  assert('deliberate-wrong-result-probe', result, ['WRONG']);
  if (process.exitCode !== 0) {{
    console.log('[PASS] deliberate-wrong-result-probe correctly detected');
    process.exitCode = savedCode;
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
        fh.write("=== INPUT (extracted from formatting-day-hour-ranges.md, block[0]+block[-1]) ===\n")
        fh.write(article_code)
        fh.write("\n\n=== EXPECTED RESULTS ===\n")
        fh.write("formatDayRanges(inputData) =>\n")
        fh.write("  ['Monday: Closed', 'Tuesday - Friday: 09:00 - 17:00',\n")
        fh.write("   'Saturday: 10:00 - 14:00', 'Sunday: Closed']\n\n")
        fh.write("formatDayRanges([]) (boundary: empty input) =>\n")
        fh.write("  ['Everyday: Closed']\n")
        fh.write("  Intermediate: all 7 days grouped as {days:[all7], hours:'Closed'},\n")
        fh.write("  days.length===7 triggers 'Everyday' label in map step.\n\n")
        fh.write("deliberate wrong result => FAIL detected\n")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    article_code = extract_js_blocks(ARTICLE)
    record_evidence(article_code)
    js = build_harness(article_code)
    rc = run_node(js)
    sys.exit(rc)


if __name__ == "__main__":
    main()
