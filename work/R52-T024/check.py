#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNIPPET_PATH = ROOT / "content/snippets/js/s/tf-idf-inverted-index.md"
RESULTS_PATH = Path(__file__).resolve().parent / "results.json"


def extract_tokenization_code(md_text: str) -> str:
    match = re.search(
        r"## Tokenization\s+.*?```js\n(.*?)\n```",
        md_text,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("Could not extract ```js block under ## Tokenization")
    return match.group(1)


def get_tool_versions() -> dict:
    versions = {"python": sys.version.split()[0]}
    for cmd, key in [(["node", "--version"], "node"), (["npm", "--version"], "npm")]:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        versions[key] = proc.stdout.strip()
    return versions


def run_node_harness(js_code: str, tamper: bool = False) -> dict:
    expected_worked = [
        "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog", ""
    ]
    if tamper:
        expected_worked = ["WRONG_TOKEN"]

    harness = f"""
{js_code}

const assert = require('node:assert/strict');

// 1. Verify the article's literal worked example and boundary example
const expectedWorked = {json.dumps(expected_worked)};
assert.deepStrictEqual(tokens, expectedWorked, 'Worked example tokens mismatch');

const expectedBoundary = ['', 'state-of-the-art', "nlp's", '1st', 'rule', ''];
assert.deepStrictEqual(boundaryTokens, expectedBoundary, 'Boundary example tokens mismatch');

// 2. Define the invariant checker for tokenize(str)
const ALLOWED_RE = /^[a-z0-9\\-']*$/;
function checkInvariant(inputStr) {{
  const out = tokenize(inputStr);
  assert.ok(Array.isArray(out), 'Output must be an array');
  for (const tkn of out) {{
    assert.strictEqual(typeof tkn, 'string', 'Each token must be a string');
    assert.match(tkn, ALLOWED_RE, `Disallowed character in token: ${{JSON.stringify(tkn)}}`);
    assert.strictEqual(tkn, tkn.toLowerCase(), `Token not lowercase: ${{JSON.stringify(tkn)}}`);
  }}
  // Re-tokenizing joined non-empty tokens is idempotent when at least one non-empty token exists
  const nonEmpty = out.filter(t => t.length > 0);
  if (nonEmpty.length > 0) {{
    assert.deepStrictEqual(
      tokenize(nonEmpty.join(' ')),
      nonEmpty,
      'Re-tokenizing joined non-empty tokens must be idempotent'
    );
  }}
  return out;
}}

// 3. Test fixture + 6 bounded variations
const cases = [
  {{ name: 'fixture', input: text, expected: expectedWorked }},
  {{ name: 'boundary_punct_and_apostrophe', input: boundaryText, expected: expectedBoundary }},
  {{ name: 'empty_string', input: '', expected: [''] }},
  {{ name: 'only_delimiters', input: '!!! --- ???', expected: ['', '---', ''] }},
  {{ name: 'single_char_and_digits', input: 'A 1 I 0', expected: ['a', '1', 'i', '0'] }},
  {{ name: 'mixed_case_hyphens_apostrophes', input: "Don't STOP co-op_2026!", expected: ["don't", 'stop', 'co-op', '2026', ''] }},
  {{ name: 'unicode_and_whitespace_delimiters', input: ' café\\tnaïve\\nJS ', expected: ['', 'caf', 'na', 've', 'js', ''] }},
];

const results = cases.map(c => {{
  const actual = checkInvariant(c.input);
  assert.deepStrictEqual(actual, c.expected, `Mismatch on case ${{c.name}}`);
  return {{
    name: c.name,
    input: c.input,
    expected: c.expected,
    actual,
    passed: true,
  }};
}});

process.stdout.write(JSON.stringify({{ cases: results }}, null, 2));
"""
    proc = subprocess.run(
        ["node", "-e", harness],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node verification failed:\n{proc.stderr or proc.stdout}")
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-test", action="store_true")
    args = parser.parse_args()

    md_text = SNIPPET_PATH.read_text(encoding="utf-8")
    js_code = extract_tokenization_code(md_text)

    if args.negative_test:
        try:
            run_node_harness(js_code, tamper=True)
        except RuntimeError:
            print("Negative test passed: checker failed as expected on tampered output.")
            return 0
        print("Negative test FAILED: checker unexpectedly passed on tampered output.", file=sys.stderr)
        return 1

    run_output = run_node_harness(js_code, tamper=False)
    report = {
        "task": "R52-T024",
        "snippet": str(SNIPPET_PATH.relative_to(ROOT)),
        "tool_versions": get_tool_versions(),
        "status": "PASSED",
        **run_output,
    }
    RESULTS_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Check PASSED! Evidence saved to {RESULTS_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
