import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/prevent-string-being-escaped.md"

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)
if len(blocks) < 2:
    print("FAIL: expected at least 2 js blocks in article")
    sys.exit(1)

# (block index, expression to print, expected node output)
CASES = [
    (0, "path", "C:webindex.html"),
    (0, "unescapedPath", "C:\\web\\index.html"),
    (1, "escaped.length", "1"),
    (1, "raw.length", "2"),
    (1, "raw.charCodeAt(0)", "92"),
]
if os.environ.get("FORCE_WRONG") == "1":
    CASES[1] = (0, "unescapedPath", "WRONG")

fail = False
for idx, expr, want in CASES:
    # strip trailing comments so only the article's own code runs
    code = "\n".join(l.split(" //")[0] for l in blocks[idx].splitlines())
    code += f"\nconsole.log({expr});"
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL: node error:", r.stderr)
        sys.exit(r.returncode)
    actual = r.stdout.strip()
    print(f"block{idx} {expr}: expected={want} actual={actual}")
    if actual != want:
        fail = True

if fail:
    print("FAIL: mismatch")
    sys.exit(1)
print("PASS: article examples produce the expected results")
