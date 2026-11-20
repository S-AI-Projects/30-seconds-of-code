#!/usr/bin/env python3
"""
Check script for R52-T041: store-dom-items
Extracts and executes the actual changed JavaScript example from content/snippets/js/s/store-dom-items.md,
asserts published expected output/state, tests boundary conditions, and ensures deliberate wrong results fail.
"""

import os
import re
import subprocess
import sys

def run_snippet(js_code, expected_overrides=None):
    runner_script = f"""
class DOMTokenList {{
  constructor() {{ this._classes = new Set(); }}
  add(...classes) {{ classes.forEach(c => this._classes.add(c)); }}
  remove(...classes) {{ classes.forEach(c => this._classes.delete(c)); }}
  contains(c) {{ return this._classes.has(c); }}
  get value() {{ return Array.from(this._classes).join(' '); }}
  toString() {{ return this.value; }}
}}

class MockElement {{
  constructor(id) {{
    this.id = id;
    this.classList = new DOMTokenList();
    this.textContent = '';
    this.hidden = true;
    this.parentNode = null;
  }}
}}

class MockDocument {{
  constructor() {{
    this.elements = new Map();
  }}
  register(id, el) {{
    this.elements.set(id, el);
  }}
  querySelector(sel) {{
    if (sel.startsWith('#')) {{
      return this.elements.get(sel.slice(1)) || null;
    }}
    return null;
  }}
}}

const doc = new MockDocument();
const el = new MockElement('my-element');
doc.register('my-element', el);
global.document = doc;

// Run snippet code
{js_code}

const results = {{
  classListContainsMyClass: el.classList.contains('my-class'),
  textContent: el.textContent,
  hidden: el.hidden,
  missingElementIsNull: missingElement === null
}};

console.log(JSON.stringify(results));
"""

    proc = subprocess.run(
        ["node", "-e", runner_script],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node execution failed with exit code {proc.returncode}:\n{proc.stderr}")

    import json
    results = json.loads(proc.stdout.strip())

    # Assert results against expectations
    exp_class = expected_overrides.get("classListContainsMyClass", True) if expected_overrides else True
    exp_text = expected_overrides.get("textContent", "hello") if expected_overrides else "hello"
    exp_hidden = expected_overrides.get("hidden", False) if expected_overrides else False
    exp_missing = expected_overrides.get("missingElementIsNull", True) if expected_overrides else True

    assert results["classListContainsMyClass"] == exp_class, f"Expected class {exp_class}, got {results['classListContainsMyClass']}"
    assert results["textContent"] == exp_text, f"Expected text {exp_text!r}, got {results['textContent']!r}"
    assert results["hidden"] == exp_hidden, f"Expected hidden {exp_hidden}, got {results['hidden']}"
    assert results["missingElementIsNull"] == exp_missing, f"Expected missingElementIsNull {exp_missing}, got {results['missingElementIsNull']}"

    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(os.path.join(base_dir, "S-AI-Project")):
        proj_dir = os.path.join(base_dir, "S-AI-Project")
    else:
        proj_dir = base_dir

    snippet_path = os.path.join(proj_dir, "content", "snippets", "js", "s", "store-dom-items.md")
    if not os.path.isfile(snippet_path):
        print(f"ERROR: Snippet file not found: {snippet_path}", file=sys.stderr)
        sys.exit(1)

    with open(snippet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract code blocks
    code_blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
    if not code_blocks:
        print("ERROR: No JavaScript code block found in snippet", file=sys.stderr)
        sys.exit(1)

    js_code = code_blocks[0]

    # Check key contracts are in the published code
    required_lines = [
        "document.querySelector('#my-element').classList.add('my-class');",
        "const myElement = document.querySelector('#my-element');",
        "myElement.classList.add('my-class');",
        "myElement.textContent = 'hello';",
        "myElement.hidden = false;",
        "const missingElement = document.querySelector('#non-existent');",
    ]
    for line in required_lines:
        if line not in js_code:
            print(f"ERROR: Expected code line missing from snippet: {line}", file=sys.stderr)
            sys.exit(1)

    # 1. Run actual snippet and verify expected output
    actual_results = run_snippet(js_code)
    print(f"PASS: Actual snippet execution results verified: {actual_results}")

    # 2. Test deliberate wrong expectation fails
    failed_on_wrong = False
    try:
        run_snippet(js_code, expected_overrides={"textContent": "wrong-value"})
    except AssertionError:
        failed_on_wrong = True

    if not failed_on_wrong:
        print("ERROR: Check did not fail on deliberate wrong textContent expectation!", file=sys.stderr)
        sys.exit(1)

    failed_on_wrong_boundary = False
    try:
        run_snippet(js_code, expected_overrides={"missingElementIsNull": False})
    except AssertionError:
        failed_on_wrong_boundary = True

    if not failed_on_wrong_boundary:
        print("ERROR: Check did not fail on deliberate wrong boundary expectation!", file=sys.stderr)
        sys.exit(1)

    print("PASS: Deliberate wrong assertions correctly triggered non-zero failures.")
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    main()
