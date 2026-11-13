import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/array-filtering-tips.md"

# (expression as written in the article, expected node output)
EXPECTED = [
    ("arr.find(x => x > 3);", "4"),
    ("arr.find(x => x > 10);", "undefined"),
    ("arr.filter(x => x > 3);", "[ 4, 5 ]"),
    ("arr.filter(x => x > 10);", "[]"),
]
if os.environ.get("FORCE_WRONG") == "1":
    EXPECTED[1] = (EXPECTED[1][0], "WRONG")

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)

fail = False
for expr, want in EXPECTED:
    # use the article's own code block that contains this exact expression
    block = next((b for b in blocks if expr in b), None)
    if block is None:
        print(f"FAIL: expression not found in article: {expr}")
        sys.exit(1)
    setup = block.split(expr)[0]
    # keep only declarations before the expression, drop earlier call lines
    setup_lines = [l for l in setup.splitlines() if l.startswith("const ")]
    code = "\n".join(setup_lines) + f"\nconsole.log({expr.rstrip(';')});"
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL: node error:", r.stderr)
        sys.exit(r.returncode)
    actual = r.stdout.strip()
    print(f"{expr} expected={want} actual={actual}")
    if actual != want:
        fail = True

if fail:
    print("FAIL: mismatch")
    sys.exit(1)
print("PASS: article examples produce the expected results")
