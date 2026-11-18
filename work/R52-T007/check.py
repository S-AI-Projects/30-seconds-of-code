#!/usr/bin/env python3
"""R52-T007 checker: Derive result step by step for first/last date of month."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const firstDateOfMonth = (date = new Date()) =>
  new Date(date.getFullYear(), date.getMonth(), 1);

const lastDateOfMonth = (date = new Date()) =>
  new Date(date.getFullYear(), date.getMonth() + 1, 0);

const pad = n => String(n).padStart(2, '0');
const toYMD = d => `${{d.getFullYear()}}-${{pad(d.getMonth() + 1)}}-${{pad(d.getDate())}}`;

const tests = [
  // Worked example
  {{ fn: 'first', date: '2015-08-11', expected: '2015-08-01' }},
  {{ fn: 'last',  date: '2015-08-11', expected: '2015-08-31' }},
  // Intermediate step extraction test for 2015-08-11
  {{ fn: 'deriveYear',  date: '2015-08-11', expected: 2015 }},
  {{ fn: 'deriveMonth', date: '2015-08-11', expected: 7 }}, // 0-indexed August
  // Boundaries
  {{ fn: 'last',  date: '2024-02-10', expected: '2024-02-29' }}, // Leap year
  {{ fn: 'last',  date: '2023-02-10', expected: '2023-02-28' }}, // Non-leap year
  {{ fn: 'first', date: '2023-12-25', expected: '2023-12-01' }}, // December first
  {{ fn: 'last',  date: '2023-12-25', expected: '2023-12-31' }}, // December last
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const t of tests) {{
  const d = new Date(t.date);
  let actual;
  if (t.fn === 'first') actual = toYMD(firstDateOfMonth(d));
  else if (t.fn === 'last') actual = toYMD(lastDateOfMonth(d));
  else if (t.fn === 'deriveYear') actual = d.getFullYear();
  else if (t.fn === 'deriveMonth') actual = d.getMonth();

  const exp = forceWrong ? (typeof t.expected === 'string' ? '1999-01-01' : 999) : t.expected;
  const pass = actual === exp;
  results.push({{ fn: t.fn, input: t.date, expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: ${{t.fn}}(${{t.date}}) => ${{actual}}, expected ${{exp}}`);
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

with open("work/R52-T007/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T007/results.json")
