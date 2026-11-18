#!/usr/bin/env python3
"""R52-T009 checker: Explain resource behavior — object comparison."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const equals = (a, b) => {{
  if (a === b) return true;
  if (a instanceof Date && b instanceof Date)
    return a.getTime() === b.getTime();
  if (!a || !b || (typeof a !== 'object' && typeof b !== 'object'))
    return a === b;
  if (a.prototype !== b.prototype) return false;
  const keys = Object.keys(a);
  if (keys.length !== Object.keys(b).length) return false;
  return keys.every(k => equals(a[k], b[k]));
}};

const jsonEquals = (a, b) => JSON.stringify(a) === JSON.stringify(b);

const tests = [
  // 1. Worked examples
  {{ name: 'identical objects', a: {{ name: 'John', age: 26 }}, b: {{ name: 'John', age: 26 }}, expected: true }},
  {{ name: 'undefined age mismatch', a: {{ name: 'John' }}, b: {{ name: 'John', age: undefined }}, expected: false }},
  {{ name: 'array vs indexed object', a: [1, 2, 3], b: {{ 0: 1, 1: 2, 2: 3 }}, expected: true }},
  // 2. Resource scaling & order sensitivity
  {{ name: 'differing key orders', a: {{ a: 1, b: 2 }}, b: {{ b: 2, a: 1 }}, expected: true }},
  // 3. Boundary cases
  {{ name: 'empty objects', a: {{}}, b: {{}}, expected: true }},
  {{ name: 'empty arrays', a: [], b: [], expected: true }},
  {{ name: 'nested empty', a: {{ a: {{}} }}, b: {{ a: {{}} }}, expected: true }},
  {{ name: 'different primitive types', a: {{ x: 1 }}, b: {{ x: '1' }}, expected: false }}
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const t of tests) {{
  const actual = equals(t.a, t.b);
  const exp = forceWrong ? !t.expected : t.expected;
  const pass = actual === exp;
  results.push({{ name: t.name, expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: ${{t.name}} => got ${{actual}}, expected ${{exp}}`);
    failed++;
  }}
}}

// Resource behavior: verify JSON.stringify key-order pitfall
const orderSensitiveInJson = jsonEquals({{ a: 1, b: 2 }}, {{ b: 2, a: 1 }});
if (orderSensitiveInJson !== false) {{
  console.error('FAIL: JSON.stringify unexpectedly did not exhibit key-order sensitivity');
  failed++;
}}

console.log(JSON.stringify(results, null, 2));
process.exit(failed > 0 ? 1 : 0);
"""

res = subprocess.run(["node", "-e", code], capture_output=True, text=True)
if force_wrong:
    if res.returncode != 0:
        print("Negative test correctly failed with non-zero exit code.")
        sys.exit(0)
    else:
        print("ERROR: Negative test unexpectedly passed!", file=sys.stderr)
        sys.exit(1)

if res.returncode != 0:
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)

with open("work/R52-T009/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T009/results.json")
