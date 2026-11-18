#!/usr/bin/env python3
"""R52-T010 checker: Protect the example against regression — collection is empty."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const isEmpty = val =>
  val === null || val === undefined || !Object.keys(val).length;

// Temporary mutant for mutation testing:
const mutantIsEmptyInverted = val =>
  val === null || val === undefined || Object.keys(val).length;

const tests = [
  // 1. Worked examples
  {{ input: [], expected: true }},
  {{ input: [1, 2], expected: false }},
  {{ input: {{}}, expected: true }},
  {{ input: {{ a: 1, b: 2 }}, expected: false }},
  {{ input: '', expected: true }},
  {{ input: 'text', expected: false }},
  {{ input: null, expected: true }},
  {{ input: undefined, expected: true }},
  // 2. Boundary cases
  {{ input: new Array(3), expected: true }},
  {{ input: 0, expected: true }},
  {{ input: true, expected: true }},
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const t of tests) {{
  const actual = Boolean(isEmpty(t.input));
  const exp = forceWrong ? !t.expected : t.expected;
  const pass = actual === exp;
  results.push({{ input: String(t.input), expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: isEmpty(${{JSON.stringify(t.input)}}) => ${{actual}}, expected ${{exp}}`);
    failed++;
  }}
}}

// 3. Mutation test: distinguish correct implementation from the mutant
const mutantDetected = mutantIsEmptyInverted([]) !== isEmpty([]);
if (!mutantDetected) {{
  console.error('FAIL: Test suite failed to kill mutantIsEmptyInverted');
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

with open("work/R52-T010/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T010/results.json")
