#!/usr/bin/env python3
"""
R52-T015 · check.py
====================
Extracts the ```js code block from the authoritative article
  content/snippets/js/s/immutable-object-proxy.md
  (anchor: immutable)
and executes it with Node.js, asserting that:

  1. Setting any property on an immutable proxy throws 'This object is immutable.'
     - immutableTerm.name = 'hi'           (article example 1)
     - immutableTerm.id   = 2              (article example 2)
     - immutableProperty.value = 'pronoun' (article example 3, nested)
  2. Boundary: read access is unaffected — get trap returns values normally.
     - immutableTerm.id    === 1
     - immutableTerm.value === 'hello'
  3. A deliberate wrong result (expecting no error) is detected.

No seeds/dates/locale needed — the example is fully deterministic.
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
    REPO_ROOT, "content", "snippets", "js", "s", "immutable-object-proxy.md"
)

# ---------------------------------------------------------------------------
# 1. Extract the ```js ... ``` fence
# ---------------------------------------------------------------------------
def extract_js_block(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    m = re.search(r"```js\n(.*?)```", source, re.DOTALL)
    if not m:
        sys.exit(f"ERROR: no ```js code block found in {path}")
    return m.group(1)


# ---------------------------------------------------------------------------
# 2. Build assertion harness
#    The article code uses bare throw statements (not inside try/catch).
#    We wrap each mutation attempt in a try/catch in the harness.
# ---------------------------------------------------------------------------
def build_harness(article_code: str) -> str:
    # Strip the bare throw lines from article code — the harness re-runs them
    # inside try/catch so they don't abort the script.
    # We keep the fixture + proxy definition; skip the last 5 lines (mutation calls).
    lines = article_code.rstrip().splitlines()
    # Find the first mutation line (starts with 'immutableTerm.name')
    cut = next(
        (i for i, l in enumerate(lines) if l.strip().startswith('immutableTerm.name')),
        len(lines)
    )
    setup_code = "\n".join(lines[:cut])

    return r"""
// ---- Article setup code (verbatim from immutable-object-proxy.md) ----
{setup}

// ---- Assertion harness (R52-T015/check.py) ----
function assertThrows(label, fn, expectedMsg) {{
  try {{
    fn();
    console.error('[FAIL] ' + label + ' — expected an error but none was thrown');
    process.exitCode = 1;
  }} catch (e) {{
    if (e.message === expectedMsg) {{
      console.log('[PASS] ' + label);
    }} else {{
      console.error('[FAIL] ' + label);
      console.error('  expected error: ' + expectedMsg);
      console.error('  actual error:   ' + e.message);
      process.exitCode = 1;
    }}
  }}
}}

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

const ERR = 'This object is immutable.';

// 1. Article examples: each mutation must throw
assertThrows('immutableTerm.name = "hi"',
  () => {{ immutableTerm.name = 'hi'; }}, ERR);

assertThrows('immutableTerm.id = 2',
  () => {{ immutableTerm.id = 2; }}, ERR);

assertThrows('immutableProperty.value = "pronoun"',
  () => {{ immutableProperty.value = 'pronoun'; }}, ERR);

// 2. Boundary: read access unaffected
assert('immutableTerm.id read (get trap passthrough)',   immutableTerm.id,    1);
assert('immutableTerm.value read (get trap passthrough)', immutableTerm.value, 'hello');

// 3. Deliberate wrong-result probe — expect no error thrown (should FAIL)
(function() {{
  const savedCode = process.exitCode;
  process.exitCode = 0;
  let threw = false;
  try {{ immutableTerm.id = 99; }} catch(e) {{ threw = true; }}
  // probe: we wrongly assert it did NOT throw
  if (!threw) {{
    console.error('[FAIL] deliberate-wrong-result-probe was NOT detected – harness broken');
    process.exitCode = 1;
  }} else {{
    // correctly: it DID throw, so our wrong assertion is caught
    console.error('[FAIL] deliberate-wrong-result-probe');
    console.error('  expected: no error (deliberately wrong)');
    console.error('  actual:   error thrown — This object is immutable.');
    console.log('[PASS] deliberate-wrong-result-probe correctly detected');
    process.exitCode = savedCode;
  }}
}})();
""".format(setup=setup_code)


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
        fh.write("=== INPUT (extracted from immutable-object-proxy.md) ===\n")
        fh.write(article_code)
        fh.write("\n\n=== EXPECTED RESULTS ===\n")
        fh.write("immutableTerm.name = 'hi'          => throws 'This object is immutable.'\n")
        fh.write("immutableTerm.id = 2               => throws 'This object is immutable.'\n")
        fh.write("immutableProperty.value='pronoun'  => throws 'This object is immutable.'\n")
        fh.write("immutableTerm.id  (read)           => 1       (boundary: get passthrough)\n")
        fh.write("immutableTerm.value (read)         => 'hello' (boundary: get passthrough)\n")
        fh.write("deliberate wrong result            => FAIL detected\n")
        fh.write("\nNote: no seeds/dates/locale needed — example is fully deterministic.\n")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    article_code = extract_js_block(ARTICLE)
    record_evidence(article_code)
    js = build_harness(article_code)
    rc = run_node(js)
    sys.exit(rc)


if __name__ == "__main__":
    main()
