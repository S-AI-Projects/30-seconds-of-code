# R52-T039 evidence
Student: ANIKETBHAI PANARA (E26B07F0533)
Tool versions:
Python 3.15.2
node v24.20.0
npm 11.19.0

Experiment (manual requestAnimationFrame queue, step() fires one frame):
after recordAnimationFrames(cb): fired=0, pending frames=1 (running=true, raf set)
after step() x3: fired=3, pending frames=1 (run re-schedules itself)
after stop(): fired=3, pending frames=0 (cancelAnimationFrame removed raf)
step() after stop: fired=3, pending frames=0 (no callback fires)
Boundary: start() twice -> pending frames=1 (second call returns early)
Boundary: autoStart=false -> no frame until start(): 1 -> 2 after rec2.start()
Deliberate wrong run (FORCE_WRONG=1): expected=WRONG for first line -> check exits 1
