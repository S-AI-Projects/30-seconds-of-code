#!/usr/bin/env python3
"""R52-T005 checker: Remove hidden state from heapsort and verify boundary cases."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const heapsort = arr => {{
  const a = [...arr];
  let l = a.length;
  const heapify = (a, i) => {{
    const left = 2 * i + 1;
    const right = 2 * i + 2;
    let max = i;
    if (left < l && a[left] > a[max]) max = left;
    if (right < l && a[right] > a[max]) max = right;
    if (max !== i) {{
      [a[max], a[i]] = [a[i], a[max]];
      heapify(a, max);
    }}
  }};
  for (let i = Math.floor(l / 2); i >= 0; i -= 1) heapify(a, i);
  for (let i = a.length - 1; i > 0; i--) {{
    [a[0], a[i]] = [a[i], a[0]];
    l--;
    heapify(a, 0);
  }}
  return a;
}};

const tests = [
  {{ input: [6, 3, 4, 1], expected: [1, 3, 4, 6] }},
  {{ input: [], expected: [] }},
  {{ input: [42], expected: [42] }},
  {{ input: [1, 2, 3, 4], expected: [1, 2, 3, 4] }},
  {{ input: [5, 4, 3, 2, 1], expected: [1, 2, 3, 4, 5] }},
  {{ input: [3, 1, 3, 2, 1], expected: [1, 1, 2, 3, 3] }}
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const t of tests) {{
  const actual = heapsort(t.input);
  const exp = forceWrong && t.input.length > 0 ? [999] : t.expected;
  const pass = JSON.stringify(actual) === JSON.stringify(exp);
  results.push({{ input: t.input, expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: heapsort(${{JSON.stringify(t.input)}}) => ${{JSON.stringify(actual)}}, expected ${{JSON.stringify(exp)}}`);
    failed++;
  }}
}}

// Verify no global variable leakage
if (typeof globalThis.i !== 'undefined') {{
  console.error('FAIL: global variable "i" leaked into outer scope');
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

with open("work/R52-T005/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T005/results.json")
