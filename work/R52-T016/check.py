#!/usr/bin/env python3
"""
R52-T016 · check.py
====================
Extracts the FIRST ```js code block from the authoritative article
  content/snippets/js/s/remove-matching-array-elements.md
  (section: "Inverting the condition", anchors: negate, remove, isEven)
and executes it with Node.js, asserting that:

  1. remove(nums, isEven) === [1, 3]        (literal article example)
  2. nums is unchanged === [1, 2, 3, 4]     (non-mutation guarantee)
  3. Intermediate: negate(isEven) per element produces correct booleans
  4. Boundary: remove([2,4,6], isEven) === [] (all elements match → empty)
  5. Deliberate wrong result detected.

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
    REPO_ROOT, "content", "snippets", "js", "s", "remove-matching-array-elements.md"
)

# ---------------------------------------------------------------------------
# 1. Extract the FIRST ```js ... ``` fence (Inverting the condition section)
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
// ---- Article code (verbatim from remove-matching-array-elements.md, first js block) ----
{code}

// ---- Assertion harness (R52-T016/check.py) ----
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

// 1. Literal worked example from article
assert('remove(nums, isEven)', remove(nums, isEven), [1, 3]);

// 2. Non-mutation guarantee: original array unchanged
assert('nums unchanged after remove', nums, [1, 2, 3, 4]);

// 3. Intermediate values: negate(isEven) applied to each element
//    negate(isEven)(n) == !isEven(n) — the filter predicate that decides keep/remove
const negIsEven = negate(isEven);
assert('negate(isEven)(1) intermediate', negIsEven(1), true);  // odd  → kept
assert('negate(isEven)(2) intermediate', negIsEven(2), false); // even → removed
assert('negate(isEven)(3) intermediate', negIsEven(3), true);  // odd  → kept
assert('negate(isEven)(4) intermediate', negIsEven(4), false); // even → removed

// 4. Boundary: all elements match → result is empty array
assert('remove([2,4,6], isEven) all-match boundary', remove([2, 4, 6], isEven), []);

// 5. Deliberate wrong-result probe
(function() {{
  const savedCode = process.exitCode;
  process.exitCode = 0;
  assert('deliberate-wrong-result-probe', remove(nums, isEven), [2, 4]);
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
        fh.write("=== INPUT (extracted from remove-matching-array-elements.md, first js block) ===\n")
        fh.write(article_code)
        fh.write("\n\n=== EXPECTED RESULTS ===\n")
        fh.write("remove([1,2,3,4], isEven)  =>  [1, 3]       (literal article example)\n")
        fh.write("nums after remove           =>  [1,2,3,4]    (non-mutation guarantee)\n")
        fh.write("negate(isEven)(1)           =>  true         (intermediate: 1 is odd → kept)\n")
        fh.write("negate(isEven)(2)           =>  false        (intermediate: 2 is even → removed)\n")
        fh.write("negate(isEven)(3)           =>  true         (intermediate: 3 is odd → kept)\n")
        fh.write("negate(isEven)(4)           =>  false        (intermediate: 4 is even → removed)\n")
        fh.write("remove([2,4,6], isEven)     =>  []           (boundary: all match)\n")
        fh.write("deliberate wrong result     =>  FAIL detected\n")


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
