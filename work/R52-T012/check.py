#!/usr/bin/env python3
"""
R52-T012 · check.py
====================
Extracts the first ```js code block from the authoritative article
  content/snippets/js/s/partially-apply-function.md
  (section: "Prepend arguments to a function", anchors: partial, greet)
and executes it with Node.js, asserting that:

  1. The literal worked example:
       greetHello('John')  =>  'Hello John!'
  2. The boundary example (all args pre-filled, zero remaining needed):
       greetHelloJohn()    =>  'Hello John!'
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
    REPO_ROOT, "content", "snippets", "js", "s", "partially-apply-function.md"
)

# ---------------------------------------------------------------------------
# 1. Extract the FIRST ```js ... ``` fence (Prepend section)
# ---------------------------------------------------------------------------
def extract_first_js_block(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    m = re.search(r"```js\n(.*?)```", source, re.DOTALL)
    if not m:
        sys.exit(f"ERROR: no ```js code block found in {path}")
    return m.group(1)


# ---------------------------------------------------------------------------
# 2. Build assertion harness around the extracted code
# ---------------------------------------------------------------------------
def build_harness(article_code: str) -> str:
    return """
// ---- Article code (verbatim from partially-apply-function.md, Prepend section) ----
{code}

// ---- Assertion harness (R52-T012/check.py) ----
function assert(label, actual, expected) {{
  if (actual !== expected) {{
    console.error('[FAIL] ' + label);
    console.error('  expected: ' + JSON.stringify(expected));
    console.error('  actual:   ' + JSON.stringify(actual));
    process.exitCode = 1;
  }} else {{
    console.log('[PASS] ' + label);
  }}
}}

// 1. Literal worked example from article
assert('greetHello("John")', greetHello('John'), 'Hello John!');

// 2. Boundary: all arguments pre-filled — zero remaining args needed.
//    Precondition: partials already satisfies greet's full parameter list,
//    so the returned function called with no arguments still returns correctly.
assert('greetHelloJohn() all-args-prefilled boundary', greetHelloJohn(), 'Hello John!');

// 3. Deliberate wrong-result probe — must FAIL to prove harness catches errors
(function() {{
  const savedCode = process.exitCode;
  process.exitCode = 0;
  assert('deliberate-wrong-result-probe', greetHello('John'), 'WRONG OUTPUT');
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
        fh.write("=== INPUT (extracted from partially-apply-function.md, first js block) ===\n")
        fh.write(article_code)
        fh.write("\n\n=== EXPECTED RESULTS ===\n")
        fh.write("greetHello('John')       =>  'Hello John!'  (literal worked example)\n")
        fh.write("greetHelloJohn()         =>  'Hello John!'  (boundary: all args pre-filled)\n")
        fh.write("deliberate wrong result  =>  FAIL detected\n")


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
