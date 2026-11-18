#!/usr/bin/env python3
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNIPPET_PATH = ROOT / "content/snippets/js/s/add-key-value-pair-to-object.md"
RESULTS_PATH = Path(__file__).resolve().parent / "results.json"

def extract_code(md_text: str) -> str:
    m = re.search(r"## Dot notation\s+.*?```js\n(.*?)\n```", md_text, flags=re.DOTALL)
    if not m:
        raise RuntimeError("Could not extract ```js block under ## Dot notation")
    return m.group(1)

def tool_versions() -> dict:
    v = {"python": sys.version.split()[0]}
    for cmd, k in [(["node", "--version"], "node"), (["npm", "--version"], "npm")]:
        v[k] = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
    return v

def run_check(js_code: str, tamper: bool = False) -> dict:
    exp = {"a": 1, "b": 2, "c": 3} if not tamper else {"a": 1, "b": 2, "c": 999}
    harness = f"""
const assert = require('node:assert/strict');
{js_code}
const exp = {json.dumps(exp)};
assert.deepStrictEqual(obj, exp);
assert.deepStrictEqual(emptyObj, {{ $id_1: 42 }});
const track = init => {{
  const steps = [{{ ...init }}];
  const proxy = new Proxy({{ ...init }}, {{ set(t, k, v) {{ t[k] = v; steps.push({{ ...t }}); return true; }} }});
  return {{ proxy, steps }};
}};
const w = track({{ a: 1 }});
assert.strictEqual((w.proxy.b = 2), 2);
assert.strictEqual((w.proxy.c = 3), 3);
assert.deepStrictEqual(w.steps, [{{ a: 1 }}, {{ a: 1, b: 2 }}, exp]);
const b = track({{}});
b.proxy.$id_1 = 0; b.proxy.$id_1 = 42;
assert.deepStrictEqual(b.steps, [{{}}, {{ $id_1: 0 }}, {{ $id_1: 42 }}]);
process.stdout.write(JSON.stringify({{ cases: [
  {{ name: 'worked_intermediate', input: {{ a: 1 }}, expected: [{{ a: 1 }}, {{ a: 1, b: 2 }}, exp], actual: w.steps, passed: true }},
  {{ name: 'worked_final', input: {{ a: 1 }}, expected: exp, actual: obj, passed: true }},
  {{ name: 'boundary_intermediate', input: {{}}, expected: [{{}}, {{ $id_1: 0 }}, {{ $id_1: 42 }}], actual: b.steps, passed: true }},
  {{ name: 'boundary_final', input: {{}}, expected: {{ $id_1: 42 }}, actual: emptyObj, passed: true }}
] }}, null, 2));
"""
    p = subprocess.run(["node", "-e", harness], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Node verification failed:\n{p.stderr or p.stdout}")
    return json.loads(p.stdout)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--negative-test", action="store_true")
    args = ap.parse_args()
    js_code = extract_code(SNIPPET_PATH.read_text(encoding="utf-8"))
    if args.negative_test:
        try:
            run_check(js_code, tamper=True)
        except RuntimeError:
            print("Negative test passed: checker failed as expected on tampered output.")
            return 0
        print("Negative test FAILED.", file=sys.stderr)
        return 1
    out = run_check(js_code, tamper=False)
    RESULTS_PATH.write_text(json.dumps({
        "task": "R52-T026", "snippet": str(SNIPPET_PATH.relative_to(ROOT)),
        "tool_versions": tool_versions(), "status": "PASSED", **out
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Check PASSED! Evidence saved to {RESULTS_PATH.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
