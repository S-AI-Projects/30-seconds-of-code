# R52-T038 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
v24.20.0
11.19.0

Inputs/expected/actual (from content/snippets/js/s/array-filtering-tips.md):
arr.find(x => x > 3)  expected=4          actual=4
arr.find(x => x > 10) expected=undefined  actual=undefined
arr.filter(x => x > 3)  expected=[ 4, 5 ] actual=[ 4, 5 ]
arr.filter(x => x > 10) expected=[]       actual=[]
Deliberate wrong run (FORCE_WRONG=1): find no-match expected=WRONG -> FAIL, exit code 1
