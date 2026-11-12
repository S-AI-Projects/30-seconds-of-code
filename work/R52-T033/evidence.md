# R52-T033 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
node v24.20.0
npm 11.19.0

Inputs/expected/actual:
caesarCipher('xyz', 3) expected=abc actual=abc
caesarCipher('abc', 3, true) expected=xyz actual=xyz
caesarCipher('Hello World!', 23) expected=Ebiil Tloia! actual=Ebiil Tloia!
caesarCipherAlt('Hello World!', 23) expected=Ebiil Tloia! actual=Ebiil Tloia!
Intermediate: 'H' -> char code 72 -> 72-65+23=30 -> 30%26=4 -> 'E'
Alphabet index of 'H' (alternative method) = 7
Deliberate wrong run (FORCE_WRONG=1): expected=WRONG for first line -> check exits 1
