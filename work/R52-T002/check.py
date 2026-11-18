#!/usr/bin/env python3
"""R52-T002 checker: Explain the boundary — string starts or ends with substring."""
import subprocess, sys, os, json

force_wrong = os.environ.get("FORCE_WRONG") == "1" or "--negative-test" in sys.argv

code = f"""
const startsWithSubstring = (text, word) => {{
  for (let i = word.length; i > 0; i--) {{
    const substr = word.slice(-i);
    if (text.startsWith(substr)) return substr;
  }}
  return undefined;
}};
const endsWithSubstring = (text, word) => {{
  for (let i = word.length; i > 0; i--) {{
    const substr = word.slice(0, i);
    if (text.endsWith(substr)) return substr;
  }}
  return undefined;
}};

const tests = [
  // Published examples
  {{ fn: 'starts', text: '/>Lorem ipsum dolor sit amet', word: '<br />', expected: '/>' }},
  {{ fn: 'ends',   text: 'Lorem ipsum dolor sit amet<br /', word: '<br />', expected: '<br /' }},
  // Boundary: empty word
  {{ fn: 'starts', text: '/>Lorem', word: '', expected: undefined }},
  {{ fn: 'ends',   text: 'Lorem<br /', word: '', expected: undefined }},
  // Boundary: exact match
  {{ fn: 'starts', text: '<br />Hello', word: '<br />', expected: '<br />' }},
  {{ fn: 'ends',   text: 'Hello<br />',  word: '<br />', expected: '<br />' }},
  // Boundary: no match / case sensitive
  {{ fn: 'starts', text: 'Hello world', word: '<BR />', expected: undefined }},
  {{ fn: 'ends',   text: 'Hello world',  word: '<br />', expected: undefined }}
];

const forceWrong = {str(force_wrong).lower()};
let failed = 0;
const results = [];

for (const t of tests) {{
  const actual = t.fn === 'starts' ? startsWithSubstring(t.text, t.word) : endsWithSubstring(t.text, t.word);
  const exp = forceWrong ? 'WRONG' : t.expected;
  const pass = actual === exp;
  results.push({{ fn: t.fn, text: t.text, word: t.word, expected: exp, actual, pass }});
  if (!pass) {{
    console.error(`FAIL: ${{t.fn}}Substr(${{t.text}}, ${{t.word}}) => ${{actual}}, expected ${{exp}}`);
    failed++;
  }}
}}

console.log(JSON.stringify(results, null, 2));
process.exit(failed > 0 ? 1 : 0);
"""

res = subprocess.run(["node", "-e", code], capture_output=True, text=True)
if force_wrong:
    if res.returncode != 0:
        print("Negative test correctly failed with non-zero exit code.")
        sys.exit(0)
    else:
        print("ERROR: Negative test unexpectedly passed!", file=sys.stderr)
        sys.exit(1)

if res.returncode != 0:
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)

with open("work/R52-T002/results.json", "w") as f:
    f.write(res.stdout)
print("All checks passed cleanly. Evidence saved to work/R52-T002/results.json")
