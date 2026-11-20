import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
R = Path(__file__).resolve().parents[2]
MD = R / "content/snippets/js/s/create-directory-if-not-exists.md"
OUT = Path(__file__).resolve().parent / "results.json"
def extract():
    m = re.search(r"\x60\x60\x60js\n(.*?)\n\x60\x60\x60", MD.read_text(), re.S)
    if not m: raise RuntimeError("Missing js code block")
    return m.group(1)
def run_code(code):
    h = code + "\nimport assert from 'node:assert/strict';\nimport { stat } from 'node:fs/promises';\n"
    h += "const st = await stat('test');\nassert.strictEqual(st.isDirectory(), true);\n"
    h += "const second = await createDirIfNotExists('test');\nassert.strictEqual(second, undefined);\n"
    h += "await assert.rejects(() => createDirIfNotExists('missing-parent/child'), { code: 'ENOENT' });\n"
    h += "process.stdout.write(JSON.stringify({ dirCreated: st.isDirectory(), idempotentResult: String(second), nestedRejectedWith: 'ENOENT' }));\n"
    with tempfile.TemporaryDirectory() as tmp:
        p = subprocess.run(["node", "--input-type=module", "-e", h], cwd=tmp, capture_output=True, text=True)
        if p.returncode != 0: raise RuntimeError(p.stderr)
        return json.loads(p.stdout)
ap = argparse.ArgumentParser()
ap.add_argument("--negative-test", action="store_true")
if ap.parse_args().negative_test:
    src = extract()
    mutants = [
        src.replace("mkdir(dir)", "undefined", 1),
        src.replace("access(dir)", "Promise.reject(new Error('forced'))", 1),
    ]
    for idx, mut in enumerate(mutants, 1):
        assert mut != src, f"Mutant {idx} unchanged"
        try:
            run_code(mut)
            sys.exit(1)
        except RuntimeError:
            pass
    print("Negative test passed (2/2 mutants killed)")
    sys.exit(0)
act = run_code(extract())
v = lambda c: subprocess.run([c, "--version"], capture_output=True, text=True).stdout.strip()
vers = {k: v(k) for k in ("python3", "node", "npm")}
data = {"task": "R52-T030", "snippet": str(MD.relative_to(R)), "tool_versions": vers, "status": "PASSED", "mutants_killed": 2, "actual": act}
OUT.write_text(json.dumps(data, indent=2) + "\n")
print("Check PASSED!")
