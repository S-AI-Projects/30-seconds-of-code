#!/usr/bin/env python3
"""R52-T001 checker: Make the example executable — string is valid json."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const isValidJSON = str => {{
  try {{
    JSON.parse(str);
    return true;
  }} catch (e) {{
    return false;
  }}
}};

const cases = [
  ['{{"name":"Adam","age":20}}', true],
  ['[1, 2, 3]',                true],
  ['"hello"',                  true],
  ['42',                       true],
  ['{{"name":"Adam",age:"20"}}', false],
  ['{{name: "Adam"}}',           false],
  ['undefined',                false],
  [null,                       true],
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const [input, expected] of cases) {{
  const actual = isValidJSON(input);
  const exp = forceWrong ? !expected : expected;
  const pass = actual === exp;
  results.push({{ input, expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL isValidJSON(${{JSON.stringify(input)}}) => ${{actual}}, expected ${{exp}}`);
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

with open("work/R52-T001/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T001/results.json")
