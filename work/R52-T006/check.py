#!/usr/bin/env python3
"""R52-T006 checker: Clarify HTML element class manipulation and boundary cases."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
class MockDOMTokenList {{
  constructor(initial = []) {{
    this.tokens = new Set(initial);
  }}
  contains(cls) {{ return this.tokens.has(cls); }}
  add(cls) {{ this.tokens.add(cls); }}
  remove(cls) {{ this.tokens.delete(cls); }}
  toggle(cls, force) {{
    if (typeof force !== 'undefined') {{
      if (force) this.add(cls); else this.remove(cls);
      return force;
    }}
    if (this.contains(cls)) {{ this.remove(cls); return false; }}
    else {{ this.add(cls); return true; }}
  }}
  toString() {{ return Array.from(this.tokens).join(' '); }}
}}

class MockElement {{
  constructor(initial = []) {{
    this.classList = new MockDOMTokenList(initial);
  }}
}}

const hasClass = (el, className) => el.classList.contains(className);
const addClass = (el, className) => el.classList.add(className);
const removeClass = (el, className) => el.classList.remove(className);
const toggleClass = (el, className, force) => el.classList.toggle(className, force);

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

function check(label, actual, expected) {{
  const exp = forceWrong ? !expected : expected;
  const pass = actual === exp;
  results.push({{ label, expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: ${{label}} => got ${{actual}}, expected ${{exp}}`);
    failed++;
  }}
}}

// 1. Worked example checks
const el1 = new MockElement(['special']);
check('hasClass on p.special', hasClass(el1, 'special'), true);

const el2 = new MockElement([]);
addClass(el2, 'special');
check('addClass to p', hasClass(el2, 'special'), true);

const el3 = new MockElement(['special']);
removeClass(el3, 'special');
check('removeClass from p.special', hasClass(el3, 'special'), false);

const el4 = new MockElement(['special']);
const toggleRes1 = toggleClass(el4, 'special');
check('toggleClass removes existing class', toggleRes1, false);
check('class is gone after toggle', hasClass(el4, 'special'), false);

// 2. Boundary checks
// Idempotent addition
addClass(el2, 'special');
check('idempotent addClass keeps single class', Array.from(el2.classList.tokens).length, 1);

// Safe removal of non-existent class
removeClass(el2, 'not-there');
check('safe removeClass does not alter existing tokens', hasClass(el2, 'special'), true);

// Exact matching check
const el5 = new MockElement(['btn-special']);
check('exact match prevents partial match on substring', hasClass(el5, 'special'), false);

// Force toggle
const el6 = new MockElement([]);
toggleClass(el6, 'active', true);
check('force toggle true adds class', hasClass(el6, 'active'), true);
toggleClass(el6, 'active', false);
check('force toggle false removes class', hasClass(el6, 'active'), false);

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

with open("work/R52-T006/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T006/results.json")
