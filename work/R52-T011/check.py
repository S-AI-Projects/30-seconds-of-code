#!/usr/bin/env python3
"""
R52-T011 · check.py
====================
Extracts the JavaScript code block from the authoritative article
  content/snippets/js/s/make-iterable.md
and executes it with Node.js, asserting that:
  1. The article's literal worked example (IterableNumber(1337)) produces [1,3,3,7].
  2. The boundary example (IterableNumber(5), single digit) produces [5].
  3. A deliberate wrong result is detected and causes the check to fail.

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
ARTICLE   = os.path.join(REPO_ROOT, "content", "snippets", "js", "s", "make-iterable.md")

# ---------------------------------------------------------------------------
# 1. Read the article and extract the first ```js ... ``` fence
# ---------------------------------------------------------------------------
def extract_js_block(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        source = fh.read()

    # Find the first fenced js block
    m = re.search(r"```js\n(.*?)```", source, re.DOTALL)
    if not m:
        sys.exit(f"ERROR: no ```js code block found in {path}")
    return m.group(1)


# ---------------------------------------------------------------------------
# 2. Build a small assertion harness around the extracted code
# ---------------------------------------------------------------------------
def build_harness(article_code: str) -> str:
    harness = """
// ---- Article code (verbatim from make-iterable.md) ----
{code}

// ---- Assertion harness (R52-T011/check.py) ----
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

// 2a. Worked example from article: IterableNumber(1337) → [1, 3, 3, 7]
assert('IterableNumber(1337)', [...new IterableNumber(1337)], [1, 3, 3, 7]);

// 2b. Boundary example: single-digit number → one-element array
assert('IterableNumber(5) single-digit boundary', [...new IterableNumber(5)], [5]);

// 2c. Deliberate wrong-result check – must FAIL to prove the harness catches errors
//     We expect [1,3,3,7] but assert against [9,9,9,9].
//     The inner assert will fire; we capture that and re-raise so check.py exits 0
//     only after confirming the sub-assertion flagged it.
(function() {{
  let failed = false;
  const orig = process.exitCode;
  process.exitCode = 0;         // reset so we can detect the sub-failure
  assert('deliberate-wrong-result-probe', [...new IterableNumber(1337)], [9, 9, 9, 9]);
  if (process.exitCode !== 0) {{
    console.log('[PASS] deliberate-wrong-result-probe correctly detected');
    process.exitCode = orig;    // restore: overall result is still passing
  }} else {{
    console.error('[FAIL] deliberate-wrong-result-probe was NOT detected – harness broken');
    process.exitCode = 1;
  }}
}})();
""".format(code=article_code.rstrip())
    return harness


# ---------------------------------------------------------------------------
# 3. Run the harness with Node.js
# ---------------------------------------------------------------------------
def run_node(js_source: str) -> int:
    result = subprocess.run(
        ["node", "--input-type=module", "-"],
        input=js_source.encode(),
        capture_output=False,
    )
    return result.returncode


# ---------------------------------------------------------------------------
# 4. Record tool versions and evidence
# ---------------------------------------------------------------------------
def record_evidence(article_code: str):
    evidence_dir = os.path.dirname(__file__)

    # Node version
    node_ver = subprocess.run(
        ["node", "--version"], capture_output=True, text=True
    ).stdout.strip()

    with open(os.path.join(evidence_dir, "results.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"Node version: {node_ver}\n\n")
        fh.write("=== INPUT (extracted from make-iterable.md) ===\n")
        fh.write(article_code)
        fh.write("\n\n=== EXPECTED RESULTS ===\n")
        fh.write("[...new IterableNumber(1337)]  =>  [1,3,3,7]\n")
        fh.write("[...new IterableNumber(5)]      =>  [5]\n")
        fh.write("deliberate-wrong (1337 vs 9999) => FAIL detected\n")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    article_code = extract_js_block(ARTICLE)
    record_evidence(article_code)
    js  = build_harness(article_code)
    rc  = run_node(js)
    sys.exit(rc)


if __name__ == "__main__":
    main()
