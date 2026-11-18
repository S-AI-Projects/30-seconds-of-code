#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNIPPET_PATH = ROOT / "content/snippets/js/s/callbacks.md"
RESULTS_PATH = Path(__file__).resolve().parent / "results.json"


def extract_sync_callback_code(md_text: str) -> str:
    match = re.search(
        r"## Synchronous callbacks\s+.*?```js\n(.*?)\n```",
        md_text,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("Could not extract ```js block under ## Synchronous callbacks")
    return match.group(1)


def get_tool_versions() -> dict:
    versions = {"python": sys.version.split()[0]}
    for cmd, key in [(["node", "--version"], "node"), (["npm", "--version"], "npm")]:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        versions[key] = proc.stdout.strip()
    return versions


def run_node_harness(js_code: str, tamper: bool = False) -> dict:
    expected_logs = [3, 5, 7] if not tamper else [999]

    harness = f"""
const assert = require('node:assert/strict');
const capturedLogs = [];
const origLog = console.log;
let reportPayload;

try {{
  console.log = (...args) => {{
    capturedLogs.push(args[0]);
  }};

{js_code}

  assert.deepStrictEqual(capturedLogs, {json.dumps(expected_logs)}, 'Logged output mismatch');
  assert.deepStrictEqual(mapped, [undefined, undefined, undefined], 'Side-effect map return mismatch');
  assert.deepStrictEqual(doubled, [3, 5, 7], 'Stateless map output mismatch');
  assert.deepStrictEqual(emptyMapped, [], 'Empty array boundary mismatch');
  assert.deepStrictEqual(zeroMapped, [1], 'Zero element boundary mismatch');

  const logsBefore = capturedLogs.length;
  const repeatDoubled = nums.map(doublePlusOne);
  const signedDoubled = [-2, -1, 0, 1, 2].map(doublePlusOne);
  assert.strictEqual(capturedLogs.length, logsBefore, 'Pure callback must not emit console logs');
  assert.deepStrictEqual(repeatDoubled, doubled, 'Repeated map call must be deterministic');
  assert.deepStrictEqual(signedDoubled, [-3, -1, 1, 3, 5], 'Signed integer variation mismatch');

  reportPayload = {{
    cases: [
      {{ name: 'worked_example_logs', input: [1, 2, 3], expected: {json.dumps(expected_logs)}, actual: capturedLogs, passed: true }},
      {{ name: 'worked_example_map_return', input: [1, 2, 3], expected: [null, null, null], actual: mapped.map(v => (v === undefined ? null : v)), passed: true }},
      {{ name: 'stateless_double_plus_one', input: [1, 2, 3], expected: [3, 5, 7], actual: doubled, passed: true }},
      {{ name: 'boundary_empty_array', input: [], expected: [], actual: emptyMapped, passed: true }},
      {{ name: 'boundary_zero_element', input: [0], expected: [1], actual: zeroMapped, passed: true }},
      {{ name: 'reproducible_signed_integers', input: [-2, -1, 0, 1, 2], expected: [-3, -1, 1, 3, 5], actual: signedDoubled, passed: true }},
    ]
  }};
}} finally {{
  console.log = origLog;
}}

assert.strictEqual(console.log, origLog, 'console.log was not restored');
process.stdout.write(JSON.stringify(reportPayload, null, 2));
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
    js_code = extract_sync_callback_code(md_text)

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
        "task": "R52-T025",
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
