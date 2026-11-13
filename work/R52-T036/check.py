import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/ternary-operator.md"
EXPECTED = {True: "10", False: "20"}

# Deliberate wrong result for the proof: run with  FORCE_WRONG=1
import os
if os.environ.get("FORCE_WRONG") == "1":
    EXPECTED = {True: "99", False: "20"}

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)

# Pick the worked example blocks that define someCondition = true/false
found = {}
for b in blocks:
    m = re.search(r"const someCondition = (true|false);", b)
    if m:
        found[m.group(1) == "true"] = b

if set(found) != {True, False}:
    print("FAIL: worked example or boundary example not found in article")
    sys.exit(1)

for cond, code in found.items():
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL: node error:", r.stderr)
        sys.exit(r.returncode)
    actual = r.stdout.strip()
    print(f"someCondition={cond}: expected={EXPECTED[cond]} actual={actual}")
    if actual != EXPECTED[cond]:
        print("FAIL: mismatch")
        sys.exit(1)

print("PASS: article examples produce the expected results")
