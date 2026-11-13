import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/unwind-object.md"

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

# Temporary one-operation mutant (in memory only): run with MUTANT=1
if os.environ.get("MUTANT") == "1":
    mutated = code.replace("[key]: val", "[key]: obj[key]")
    if mutated == code:
        print("FAIL: mutation was not applied")
        sys.exit(2)
    code = mutated
    print("Running with mutant: [key]: val -> [key]: obj[key]")

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

print("PASS: article examples produce the expected results")
