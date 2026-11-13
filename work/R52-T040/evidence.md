# R52-T040 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
node v24.20.0
npm 11.19.0

Inputs/expected/actual:
unwind('b', { a: true, b: [1, 2] }) expected=[{"a":true,"b":1},{"a":true,"b":2}] actual=[{"a":true,"b":1},{"a":true,"b":2}]
Intermediate: removed=[1,2], rest={"a":true}
unwind('b', { a: true, b: [] }) expected=[] actual=[]
Deliberate wrong run (FORCE_WRONG=1): expected=WRONG for first line -> check exits 1
Mutant run (MUTANT=1): [key]: val -> [key]: obj[key] gives "b":[1,2] instead of "b":1 -> check exits 1 (mutant caught)
