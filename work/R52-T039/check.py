import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/record-animation-frames.md"

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)
# Stub only so the article's first (browser) example can be evaluated in node.
# The experiment itself uses the manual frame queue written in the article.
stub = "globalThis.requestAnimationFrame = () => 0; globalThis.cancelAnimationFrame = () => {};\n"
code = stub + "\n".join(blocks)
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
