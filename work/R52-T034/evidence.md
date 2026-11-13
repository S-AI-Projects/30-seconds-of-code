# R52-T034 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
node v24.20.0
npm 11.19.0

Invariant: Math.round(nthRoot(x, n) ** n) === x for perfect powers x.
Fixture and bounded variations (x, n -> root -> rounded root**n):
32, 5 -> 2 -> 32 (fixture)
8, 3 -> 2 -> 8
81, 4 -> 3 -> 81
243, 5 -> 3 -> 243
1024, 10 -> 2 -> 1024
1, 7 -> 1 -> 1 (boundary)
Invariant checked directly by check.py on 6 cases: holds
Deliberate wrong run (FORCE_WRONG=1): expected=WRONG for first line -> check exits 1
