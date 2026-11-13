# R52-T032 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
v24.20.0
11.19.0

Inputs/expected/actual (from content/snippets/js/s/prevent-string-being-escaped.md):
template literal path expected=C:webindex.html actual=C:webindex.html
String.raw unescapedPath expected=C:\web\index.html actual=C:\web\index.html
escaped.length expected=1 actual=1
raw.length expected=2 actual=2
raw.charCodeAt(0) expected=92 actual=92
Deliberate wrong run (FORCE_WRONG=1): unescapedPath expected=WRONG -> FAIL, exit code 1
