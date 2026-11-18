#!/usr/bin/env python3
"""R52-T003 checker: Compare two methods — date range generator."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const dateRange = function* (start, end, step = 1) {{
  for (let d = new Date(start); d < new Date(end); d.setDate(d.getDate() + step))
    yield new Date(d);
}};
const dateRangeArray = (start, end, step = 1) => {{
  const result = [];
  for (let d = new Date(start); d < new Date(end); d.setDate(d.getDate() + step))
    result.push(new Date(d));
  return result;
}};

const fmt = d => d.toISOString().slice(0, 10);
const gen  = [...dateRange('2021-06-01', '2021-06-04')].map(fmt);
const arr  = dateRangeArray('2021-06-01', '2021-06-04').map(fmt);
const expected = ['2021-06-01','2021-06-02','2021-06-03'];

const gen2 = [...dateRange('2021-06-01','2021-06-07',2)].map(fmt);
const arr2 = dateRangeArray('2021-06-01','2021-06-07',2).map(fmt);
const exp2 = ['2021-06-01','2021-06-03','2021-06-05'];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

function check(label, actual, exp) {{
  const targetExp = forceWrong ? ['1999-01-01'] : exp;
  const pass = eq(actual, targetExp);
  results.push({{ label, expected: targetExp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: ${{label}} => got ${{JSON.stringify(actual)}}, expected ${{JSON.stringify(targetExp)}}`);
    failed++;
  }}
}}

check('generator step 1', gen, expected);
check('array step 1', arr, expected);
check('methods equivalence step 1', gen, arr);
check('generator step 2', gen2, exp2);
check('array step 2', arr2, exp2);

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

with open("work/R52-T003/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T003/results.json")
