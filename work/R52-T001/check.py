#!/usr/bin/env python3
"""
Repeatable assertion-based check for R52-T001 (isValidJSON).
Extracts the code block directly from content/snippets/js/s/string-is-valid-json.md,
runs the assertions against Node.js, and validates expected outputs.
"""
import os
import re
import subprocess
import sys

SNIPPET_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../content/snippets/js/s/string-is-valid-json.md")
)

def main():
    if not os.path.exists(SNIPPET_FILE):
        print(f"FAIL: File not found: {SNIPPET_FILE}")
        sys.exit(1)

    with open(SNIPPET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract the js code block
    match = re.search(r"```js\s*\n(.*?)\n```", content, re.DOTALL)
    if not match:
        print("FAIL: No ```js code block found in markdown file")
        sys.exit(1)

    js_code = match.group(1)

    # Deliberate failure test support via FORCE_WRONG env var
    force_wrong = os.environ.get("FORCE_WRONG") == "1"

    # Node test script executing the extracted code and verifying assertions
    test_script = f"""
{js_code}

const tests = [
  {{ call: 'isValidJSON(\\'{{\\"name\\":\\"Adam\\",\\"age\\":20}}\\')', actual: isValidJSON('{{"name":"Adam","age":20}}'), expected: {'false' if force_wrong else 'true'} }},
  {{ call: 'isValidJSON(\\'{{\\"name\\":\\"Adam\\",age:\\"20\\"}}\\')', actual: isValidJSON('{{"name":"Adam",age:"20"}}'), expected: false }},
  {{ call: 'isValidJSON(null)', actual: isValidJSON(null), expected: true }},
  {{ call: 'isValidJSON(\\'\\')', actual: isValidJSON(''), expected: false }}
];

let failed = false;
for (const t of tests) {{
  if (t.actual !== t.expected) {{
    console.error(`FAIL: ${{t.call}} => expected ${{t.expected}}, got ${{t.actual}}`);
    failed = true;
  }} else {{
    console.log(`PASS: ${{t.call}} === ${{t.expected}}`);
  }}
}}

if (failed) {{
  process.exit(1);
}}
"""

    res = subprocess.run(["node", "-e", test_script], capture_output=True, text=True)
    sys.stdout.write(res.stdout)
    if res.stderr:
        sys.stderr.write(res.stderr)

    if res.returncode != 0:
        print(f"Check failed with exit code {res.returncode}")
        sys.exit(res.returncode)

    print("All checks passed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
