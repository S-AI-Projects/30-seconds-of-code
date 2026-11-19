import argparse, json, re, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
MD = R / "content/snippets/js/s/cannot-extend-proxy-object.md"
OUT = Path(__file__).resolve().parent / "results.json"
def code():
    m = re.search(r"\x60\x60\x60js\n(.*?)\n\x60\x60\x60", MD.read_text(), re.S)
    if not m: raise RuntimeError("No code")
    return m.group(1)
def run(js, tamper=False):
    exp_err = "TypeError" if not tamper else "RangeError"
    h = "const assert=require('node:assert/strict'),logs=[];\n"
    h += "console.log=(...a)=>logs.push(a.join(' '));\n" + js + "\n"
    h += "assert.deepStrictEqual(logs,['Called with b = 2','Called with x = 10']);\n"
    h += "assert.deepStrictEqual({...myProxy},{a:1,b:2});assert.strictEqual(myProxy instanceof MyProxy,true);\n"
    h += f"assert.deepStrictEqual({{...emptyProxy}},{{x:10}});assert.strictEqual(subclassError,{json.dumps(exp_err)});\n"
    h += "assert.strictEqual(nullInputError,'TypeError');assert.strictEqual(Proxy.prototype,undefined);\n"
    h += "process.stdout.write(JSON.stringify({logs,myProxy:{...myProxy},emptyProxy:{...emptyProxy},subclassError,nullInputError}));"
    p = subprocess.run(["node", "-e", h], cwd=R, capture_output=True, text=True)
    if p.returncode != 0: raise RuntimeError(p.stderr)
    return json.loads(p.stdout)
ap = argparse.ArgumentParser()
ap.add_argument("--negative-test", action="store_true")
if ap.parse_args().negative_test:
    try: run(code(), True)
    except RuntimeError: print("Negative test passed"); sys.exit(0)
    sys.exit(1)
act = run(code(), False)
v = lambda c: subprocess.run([c, "--version"], capture_output=True, text=True).stdout.strip()
vers = {k: v(k) for k in ("python3", "node", "npm")}
data = {"task": "R52-T028", "snippet": str(MD.relative_to(R)), "tool_versions": vers}
data.update({"status": "PASSED", "actual": act})
OUT.write_text(json.dumps(data, indent=2) + "\n")
print("Check PASSED!")
