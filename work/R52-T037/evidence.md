# R52-T037 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
node v24.20.0
npm 11.19.0

Derivation of distance(1, 1, 2, 3):
dx = x1 - x0 = 1, dy = y1 - y0 = 2
dx**2 = 1, dy**2 = 4
sum of squares = 5
sqrt(5) = 2.2361 (fixed to 4 decimals), equals distance(1, 1, 2, 3)
Array version: Object.keys([1,1]) = ["0","1"] -> differences [1,2] -> Math.hypot(1,2) = 2.2361
Boundary: distance(3, 4, 3, 4) = 0, distance(0, 0, 3, 4) = 5
Deliberate wrong run (FORCE_WRONG=1): expected=WRONG for first line -> check exits 1
