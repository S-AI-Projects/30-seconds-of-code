import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/nth-number-root.md"

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)
code = "\n".join(blocks)
expected = [e.strip() for e in re.findall(r"console\.log\(.*\);\s*//\s*(.*)$", code, re.M)]

if not expected:
    print("FAIL: no console.log examples found in article")
    sys.exit(1)

# Deliberate wrong result for the proof: run with FORCE_WRONG=1
if os.environ.get("FORCE_WRONG") == "1":
    expected[0] = "WRONG"

r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
if r.returncode != 0:
    print("FAIL: node error:", r.stderr)
    sys.exit(r.returncode)

actual = r.stdout.strip().split("\n")
if len(actual) != len(expected):
    print(f"FAIL: expected {len(expected)} lines, got {len(actual)}")
    sys.exit(1)

for i, (e, a) in enumerate(zip(expected, actual), 1):
    print(f"{i}: expected={e} actual={a}")
    if e != a:
        print("FAIL: mismatch")
        sys.exit(1)

# Invariant checked directly on the article's own nthRoot: round(nthRoot(x, n) ** n) == x
inv = code.split("\n", 1)[0] if "const nthRoot" in code.split("\n", 1)[0] else None
m = re.search(r"const nthRoot = .*?;", code)
if not m:
    print("FAIL: nthRoot definition not found in article")
    sys.exit(1)
cases = [(32, 5), (8, 3), (81, 4), (243, 5), (1024, 10), (1, 7)]
js = m.group(0) + "\n" + "\n".join(
    f"if (Math.round(nthRoot({x}, {n}) ** {n}) !== {x}) {{ console.log('INVARIANT BROKEN {x} {n}'); process.exit(1); }}"
    for x, n in cases
) + "\nconsole.log('invariant holds');"
r2 = subprocess.run(["node", "-e", js], capture_output=True, text=True)
print("invariant on", len(cases), "cases:", r2.stdout.strip())
if r2.returncode != 0:
    print("FAIL: invariant broken")
    sys.exit(1)

print("PASS: article examples produce the expected results")
