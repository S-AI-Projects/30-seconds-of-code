#!/usr/bin/env python3
"""
Check script for R52-T047: construct-url
Extracts and executes the actual changed JavaScript examples from content/snippets/js/s/construct-url.md.
Asserts published expected output, verifies intermediate derivation states, tests boundary conditions,
and validates that deliberate wrong results fail.
"""

import json
import os
import re
import subprocess
import sys

def run_snippet(js_code, expected_overrides=None):
    runner_script = f"""
{js_code}

const results = {{
  query: query,
  locale: locale,
  campaign: campaign,
  url: url,
  emptyQuery: emptyQuery,
  emptyUrl: emptyUrl
}};

console.error('__JSON_START__' + JSON.stringify(results) + '__JSON_END__');
"""

    proc = subprocess.run(
        ["node", "-e", runner_script],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node execution failed with exit code {proc.returncode}:\n{proc.stderr}")

    match = re.search(r"__JSON_START__(.*?)__JSON_END__", proc.stderr)
    if not match:
        raise RuntimeError(f"JSON output delimiter not found in node output:\nstdout: {proc.stdout}\nstderr: {proc.stderr}")

    results = json.loads(match.group(1))

    exp_url = expected_overrides.get("url", "https://examp.le?q=Where's Waldø?&lang=en-US&from=promo_email") if expected_overrides else "https://examp.le?q=Where's Waldø?&lang=en-US&from=promo_email"
    exp_empty_url = expected_overrides.get("emptyUrl", "https://examp.le?q=") if expected_overrides else "https://examp.le?q="

    assert results["query"] == "Where's Waldø?", f"Expected query to match, got {results['query']!r}"
    assert results["locale"] == "en-US", f"Expected locale to match, got {results['locale']!r}"
    assert results["campaign"] == "promo_email", f"Expected campaign to match, got {results['campaign']!r}"
    assert results["url"] == exp_url, f"Expected url={exp_url!r}, got {results['url']!r}"
    assert results["emptyQuery"] == "", "Expected emptyQuery to be empty string"
    assert results["emptyUrl"] == exp_empty_url, f"Expected emptyUrl={exp_empty_url!r}, got {results['emptyUrl']!r}"

    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.exists(os.path.join(base_dir, "S-AI-Project")):
        proj_dir = os.path.join(base_dir, "S-AI-Project")
    else:
        proj_dir = base_dir

    snippet_path = os.path.join(proj_dir, "content", "snippets", "js", "s", "construct-url.md")
    if not os.path.isfile(snippet_path):
        print(f"ERROR: Snippet file not found: {snippet_path}", file=sys.stderr)
        sys.exit(1)

    with open(snippet_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract JavaScript blocks
    code_blocks = re.findall(r"```js\n(.*?)```", content, re.DOTALL)
    if not code_blocks:
        print("ERROR: No JavaScript code blocks found in snippet", file=sys.stderr)
        sys.exit(1)

    js_code = code_blocks[0]

    # Verify critical anchor strings
    required_lines = [
        'const query = "Where\'s Waldø?";',
        'const locale = "en-US";',
        'const campaign = "promo_email";',
        'const url = `https://examp.le?q=${query}&lang=${locale}&from=${campaign}`;',
        'const emptyUrl = `https://examp.le?q=${emptyQuery}`;',
    ]
    for line in required_lines:
        if line not in js_code:
            print(f"ERROR: Required line missing from snippet: {line}", file=sys.stderr)
            sys.exit(1)

    # 1. Run actual extracted snippet
    actual_results = run_snippet(js_code)
    print(f"PASS: Actual snippet execution results verified: {actual_results}")

    # 2. Test deliberate wrong expectation fails
    failed_on_wrong = False
    try:
        run_snippet(js_code, expected_overrides={"url": "https://wrong.url"})
    except AssertionError:
        failed_on_wrong = True

    if not failed_on_wrong:
        print("ERROR: Check did not fail on deliberate wrong expectation!", file=sys.stderr)
        sys.exit(1)

    print("PASS: Deliberate wrong assertions correctly triggered non-zero failures.")
    print("ALL CHECKS PASSED.")

if __name__ == "__main__":
    main()
