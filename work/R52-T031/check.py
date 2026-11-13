import os
import re
import subprocess
import sys

ARTICLE = "content/snippets/js/s/data-structures-tree.md"

text = open(ARTICLE, encoding="utf-8").read()
blocks = re.findall(r"```js\n(.*?)```", text, re.S)
if len(blocks) < 3:
    print("FAIL: js examples not found in article")
    sys.exit(1)


def wrap(expr):
    # print the value the way a REPL would, so the article's own comment can be compared
    return "console.log(require('util').inspect(" + expr.strip() + ", {breakLength: Infinity}));"


code_lines = []
expected = []
for block in blocks:
    lines = block.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        nxt = re.match(r"^//\s*(.*)$", lines[i + 1]) if i + 1 < len(lines) else None
        m_log = re.match(r"^console\.log\(.*\);\s*//\s*(.*)$", line)
        m_same = re.match(r"^([^\s/][^/]*?);\s*//\s*(.*)$", line)
        m_stmt = re.match(r"^([^\s/][^/]*);\s*$", line)
        if m_log:
            expected.append(m_log.group(1))
            code_lines.append(line)
        elif m_same:
            expected.append(m_same.group(2))
            code_lines.append(wrap(m_same.group(1)))
        elif m_stmt and nxt:
            expected.append(nxt.group(1))
            code_lines.append(wrap(m_stmt.group(1)))
            i += 1
        else:
            code_lines.append(line)
        i += 1

code = "\n".join(code_lines)

if not expected:
    print("FAIL: no examples with expected results found in article")
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


def norm(s):
    return re.sub(r"\s+", "", s)


for i, (e, a) in enumerate(zip(expected, actual), 1):
    print(f"{i}: expected={e} actual={a}")
    if norm(e) != norm(a):
        print("FAIL: mismatch")
        sys.exit(1)

print("PASS: article examples produce the expected results")
