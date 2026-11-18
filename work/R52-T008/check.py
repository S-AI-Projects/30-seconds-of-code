#!/usr/bin/env python3
"""R52-T008 checker: Document a failure or limitation — byte size."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const byteSize = str => new Blob([str]).size;
const safeByteSize = str => typeof str === 'string' ? new Blob([str]).size : undefined;

const tests = [
  // Worked example
  {{ input: 'Hello World', expected: 11 }},
  {{ input: '😀', expected: 4 }},
  // Boundary cases
  {{ input: '', expected: 0 }},
  {{ input: 'a', expected: 1 }},
  {{ input: 'é', expected: 2 }},
  {{ input: '字', expected: 3 }},
  {{ input: 'अ', expected: 3 }},
  // Documented limitation / coercion failure cases
  {{ input: {{}}, expected: 15, fn: 'byteSize' }}, // '[object Object]'
  {{ input: null, expected: 4, fn: 'byteSize' }},  // 'null'
  {{ input: 12345, expected: 5, fn: 'byteSize' }}, // '12345'
  // Safe variant returns undefined for non-strings
  {{ input: {{}}, expected: undefined, fn: 'safeByteSize' }},
  {{ input: null, expected: undefined, fn: 'safeByteSize' }}
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const t of tests) {{
  const fn = t.fn === 'safeByteSize' ? safeByteSize : byteSize;
  const actual = fn(t.input);
  const exp = forceWrong ? 999 : t.expected;
  const pass = actual === exp;
  results.push({{ input: String(t.input), fn: t.fn || 'byteSize', expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: byteSize(${{t.input}}) => ${{actual}}, expected ${{exp}}`);
    failed++;
  }}
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

with open("work/R52-T008/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T008/results.json")
