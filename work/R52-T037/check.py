import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/euclidean-distance.md"

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)
if len(blocks) < 2:
    print("FAIL: js examples not found in article")
    sys.exit(1)

# The article defines `distance` more than once. The first block runs at top level,
# every other block runs in its own { } scope so redefinitions do not clash.
code = blocks[0] + "\n" + "\n".join("{\n" + b + "\n}" for b in blocks[1:])
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

print("PASS: article examples produce the expected results")
