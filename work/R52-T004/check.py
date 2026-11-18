#!/usr/bin/env python3
"""R52-T004 checker: Explain an invariant — listener reference symmetry."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const {{ EventEmitter }} = require('events');

class FakeEl extends EventEmitter {{
  addEventListener(type, fn) {{ this.on(type, fn); }}
  removeEventListener(type, fn) {{ this.off(type, fn); }}
}}

const addMultipleListeners = (el, types, listener) =>
  types.forEach(type => el.addEventListener(type, listener));
const removeMultipleListeners = (el, types, listener) =>
  types.forEach(type => el.removeEventListener(type, listener));

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

function check(label, actual, exp) {{
  const targetExp = forceWrong ? !exp : exp;
  const pass = actual === targetExp;
  results.push({{ label, expected: targetExp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: ${{label}} => got ${{actual}}, expected ${{targetExp}}`);
    failed++;
  }}
}}

// 1. Invariant: same reference => symmetric add/remove
const el = new FakeEl();
const listener = () => {{}};
addMultipleListeners(el, ['click', 'mousedown'], listener);
check('listeners added', el.listenerCount('click') === 1 && el.listenerCount('mousedown') === 1, true);

removeMultipleListeners(el, ['click', 'mousedown'], listener);
check('listeners removed (same ref)', el.listenerCount('click') === 0 && el.listenerCount('mousedown') === 0, true);

// 2. Invariant broken: different function references
const el2 = new FakeEl();
addMultipleListeners(el2, ['click'], () => {{}});
removeMultipleListeners(el2, ['click'], () => {{}});
check('inline arrow NOT removed', el2.listenerCount('click') === 1, true);

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

with open("work/R52-T004/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T004/results.json")
