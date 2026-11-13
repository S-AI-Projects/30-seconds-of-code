---
title: Run a callback on each animation frame with JavaScript
shortTitle: Record animation frames
language: javascript
tags: [browser,recursion]
cover: mac-and-coffee
excerpt: Ever wanted to run a function on each animation frame? This article shows you how to do it using `Window.requestAnimationFrame()`.
listed: true
dateModified: 2024-07-21
---

Using **animation frames** is a common technique in web development to create smooth animations. The `Window.requestAnimationFrame()` method is used to **invoke a callback** before the next repaint of the browser window.

We can leverage this knowledge to create a function that **runs a callback on each animation frame**. This can be useful for creating custom animations or for running a function at a high frequency.

In order to achieve this, we can use **recursion** to keep invoking `Window.requestAnimationFrame()` as long as a flag is set to `true`. We can also provide methods to **start** and **stop** the recording of animation frames. Additionally, we can **control the start** of the recording by passing an optional argument.

In order to **track** the state of the recording, we can use a variable, `running`, and a reference to the `requestAnimationFrame` function, `raf`. We can then use the `start` and `stop` methods to **control the recording**.

Starting with out `run` function, we use recursion to keep invoking `Window.requestAnimationFrame()` as long as `running` is `true`. We call the provided callback and, if `running` is still `true`, we call `run` again.

Our `start` function will check if the recording is already running and return if it is. If it isn't, we set `running` to `true` and call the `run` function.

Our `stop` function will simply check if the recording is already stopped and return if it is. If it is running, we set `running` to `false` and cancel the animation frame using `cancelAnimationFrame()`.

Finally, if the `autoStart` argument is `true`, we call `start` when the function is invoked. If it is set to `false`, we require the user to call `start` manually.

```js
const recordAnimationFrames = (callback, autoStart = true) => {
  let running = false, raf;

  const stop = () => {
    if (!running) return;
    running = false;
    cancelAnimationFrame(raf);
  };

  const start = () => {
    if (running) return;
    running = true;
    run();
  };

  const run = () => {
    raf = requestAnimationFrame(() => {
      callback();
      if (running) run();
    });
  };

  if (autoStart) start();

  return { start, stop };
};

const cb = () => console.log('Animation frame fired');

const recorder = recordAnimationFrames(cb);
// Logs 'Animation frame fired' on each animation frame
recorder.stop();
// Stops logging
recorder.start();
// Starts again

const recorder2 = recordAnimationFrames(cb, false);
// `start` needs to be explicitly called to begin recording frames
```

## Observing the behavior

Node.js has no `requestAnimationFrame()`, so this experiment replaces it with a small manual queue. Calling `step()` fires the oldest pending frame, which makes it easy to count frames and see how many are still scheduled:

```js
let frameQueue = [], frameId = 0;
globalThis.requestAnimationFrame = fn => { frameQueue.push({ id: ++frameId, fn }); return frameId; };
globalThis.cancelAnimationFrame = id => { frameQueue = frameQueue.filter(f => f.id !== id); };
const step = () => { const f = frameQueue.shift(); if (f) f.fn(); };
```

With `autoStart` left as `true`, `running` becomes `true` and exactly one frame is scheduled (`raf` points to it). Every time that frame fires, `run` schedules the next one, so there is always one pending frame while recording:

```js
let fired = 0;
const rec = recordAnimationFrames(() => fired++);
console.log(fired, frameQueue.length); // 0 1
step(); step(); step();
console.log(fired, frameQueue.length); // 3 1
```

Calling `stop()` sets `running` to `false` and cancels the pending frame, so nothing is scheduled and no more callbacks fire, even if frames are stepped:

```js
rec.stop();
console.log(fired, frameQueue.length); // 3 0
step();
console.log(fired, frameQueue.length); // 3 0
```

## Boundary example

Calling `start()` twice does not schedule two frames, because the second call returns early while `running` is `true`. With `autoStart` set to `false`, no frame is scheduled until `start()` is called:

```js
rec.start(); rec.start();
console.log(frameQueue.length); // 1
const rec2 = recordAnimationFrames(() => fired++, false);
console.log(frameQueue.length); // 1
rec2.start();
console.log(frameQueue.length); // 2
```
