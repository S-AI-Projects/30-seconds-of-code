import argparse, json, re, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
MD = R / "content/snippets/js/s/common-regexp-cheatsheet.md"
OUT = Path(__file__).resolve().parent / "results.json"
def code():
    m = re.search(r"## Exact string match\s+.*?\x60\x60\x60js\n(.*?)\n\x60\x60\x60", MD.read_text(), re.S)
    if not m: raise RuntimeError("No code")
    return m.group(1)
def run(js, tamper=False):
    exp = not tamper
    h = f"const assert=require('node:assert/strict');\n{js}\nassert.strictEqual(exactMatch,{json.dumps(exp)});\n"
    h += "assert.deepStrictEqual(Array.from(matchResult),['abc']);assert.strictEqual(extraSuffix,false);\n"
    h += "assert.strictEqual(leadingSpace,false);assert.strictEqual(trailingNewline,false);assert.strictEqual(emptyInput,false);\n"
    h += "console.log(JSON.stringify({exactMatch,matchResult:Array.from(matchResult),extraSuffix,leadingSpace,trailingNewline,emptyInput}));"
    p = subprocess.run(["node", "-e", h], cwd=R, capture_output=True, text=True)
    if p.returncode != 0: raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)
ap = argparse.ArgumentParser()
ap.add_argument("--negative-test", action="store_true")
if ap.parse_args().negative_test:
    try: run(code(), True)
    except RuntimeError: print("Negative test passed"); sys.exit(0)
    sys.exit(1)
act = run(code(), False)
vers = {k: subprocess.run([k, "--version"], capture_output=True, text=True).stdout.strip() for k in ("python3", "node", "npm")}
cases = [
    {"name": "exact_test", "input": "abc", "expected": True, "actual": act["exactMatch"]},
    {"name": "exact_exec", "input": "abc", "expected": ["abc"], "actual": act["matchResult"]},
]
cases += [
    {"name": "suffix", "input": "abcd", "expected": False, "actual": act["extraSuffix"]},
    {"name": "space", "input": " abc", "expected": False, "actual": act["leadingSpace"]},
]
cases += [
    {"name": "newline", "input": "abc\\n", "expected": False, "actual": act["trailingNewline"]},
    {"name": "empty", "input": "", "expected": False, "actual": act["emptyInput"]},
]
OUT.write_text(json.dumps({"task":"R52-T027","snippet":str(MD.relative_to(R)),"tool_versions":vers,"status":"PASSED","cases":cases}, indent=2)+"\n")
print("Check PASSED!")
