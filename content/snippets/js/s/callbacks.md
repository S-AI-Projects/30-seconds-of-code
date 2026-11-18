---
title: What is a callback function?
shortTitle: Callback functions
language: javascript
tags: [function]
cover: rabbit-call
excerpt: JavaScript uses callback functions quite a lot. From event listeners to asynchronous code, they're an invaluable tool you need to master.
listed: true
dateModified: 2021-10-03
---

A callback function is a function passed as an argument to another function, which is then invoked inside the outer function. Callback functions are often executed once an event has occurred or a task has completed.

## Synchronous callbacks

A synchronous callback is a callback function that is executed immediately. The function passed as the first argument to `Array.prototype.map()` is a great example of a synchronous callback:

```js
const nums = [1, 2, 3];
const printDoublePlusOne = n => console.log(2 * n + 1);

const mapped = nums.map(printDoublePlusOne);
// LOGS: 3, 5, 7
// mapped: [undefined, undefined, undefined]

// Pure callback without external console state, plus boundary inputs
const doublePlusOne = n => 2 * n + 1;
const doubled = nums.map(doublePlusOne); // [3, 5, 7]
const emptyMapped = [].map(doublePlusOne); // []
const zeroMapped = [0].map(doublePlusOne); // [1]
```

In the first example, `Array.prototype.map()` invokes `printDoublePlusOne(n, index, array)` synchronously for each element of `[1, 2, 3]`, writing `3`, `5`, and `7` to external `console` state as a side effect while returning `undefined` per element (`[undefined, undefined, undefined]`). Using a stateless callback (`doublePlusOne`) removes reliance on external `console` state so results depend solely on the input array: `[1, 2, 3]` produces `[3, 5, 7]`, the empty boundary array `[]` invokes the callback zero times to return `[]`, and `[0]` returns `[1]`.

## Asynchronous callbacks

An asynchronous callback is a callback function that is used to execute code after an asynchronous operation has completed. The function executed inside `Promise.prototype.then()` is a great example of an asynchronous callback:

```js
const nums = fetch('https://api.nums.org'); // Suppose the response is [1, 2, 3]
const printDoublePlusOne = n => console.log(2 * n + 1);

nums.then(printDoublePlusOne); // LOGS: 3, 5, 7
```
