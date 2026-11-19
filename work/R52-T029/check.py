import argparse, json, re, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
MD = R / "content/snippets/js/s/arrow-functions.md"
OUT = Path(__file__).resolve().parent / "results.json"
def blocks():
    bs = re.findall(r"\x60\x60\x60js\n(.*?)\n\x60\x60\x60", MD.read_text(), re.S)
    if len(bs) < 5: raise RuntimeError("Missing blocks")
    return bs[0], bs[4]
def run(b0, b4, tamper=False):
    exp4 = 16 if not tamper else 17
    h = "const assert=require('node:assert/strict');\n"
    h += "const r0=(()=>{\n" + b0 + "\nreturn [square(4),square(0),square(-3)];})();\n"
    h += b4 + "\nconst r4=[square(4),square(0),square(-3)];\n"
    h += f"assert.strictEqual(r4[0],{exp4});assert.deepStrictEqual(r4,[16,0,9]);assert.deepStrictEqual(r0,r4);\n"
    h += "assert.strictEqual(typeof square,'function');assert.strictEqual(typeof regularSquare.prototype,'object');\n"
    h += "assert.strictEqual(square.prototype,undefined);\n"
    h += "process.stdout.write(JSON.stringify({regular:r0,arrow:r4,regularProto:typeof regularSquare.prototype,arrowProto:String(square.prototype)}));"
    p = subprocess.run(["node", "-e", h], cwd=R, capture_output=True, text=True)
    if p.returncode != 0: raise RuntimeError(p.stderr)
    return json.loads(p.stdout)
ap = argparse.ArgumentParser()
ap.add_argument("--negative-test", action="store_true")
if ap.parse_args().negative_test:
    try: run(*blocks(), True)
    except RuntimeError: print("Negative test passed"); sys.exit(0)
    sys.exit(1)
act = run(*blocks(), False)
v = lambda c: subprocess.run([c, "--version"], capture_output=True, text=True).stdout.strip()
vers = {k: v(k) for k in ("python3", "node", "npm")}
data = {"task": "R52-T029", "snippet": str(MD.relative_to(R)), "tool_versions": vers, "status": "PASSED", "actual": act}
OUT.write_text(json.dumps(data, indent=2) + "\n")
print("Check PASSED!")
