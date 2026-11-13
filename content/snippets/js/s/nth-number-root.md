---
title: Calculate the nth root of a number in JavaScript
shortTitle: Nth root of number
language: javascript
tags: [math]
cover: tree-roots
excerpt: Use `Math.pow()` to calculate the nth root of a given number in JavaScript.
listed: true
dateModified: 2024-02-17
---

The **nth root** of a number `x` is a value that, when multiplied by itself `n` times, gives `x`. The nth root can also be expressed as a **power** of `x`, where `x ^ (1/n)` is equal to the nth root of `x`.

Given this, we can use `Math.pow()` to calculate the nth root of a given number. Simply pass it the number `x` and a power of `1 / n`, and you'll get the nth root of `x`.

```js
const nthRoot = (x, n) => Math.pow(x, 1 / n);

nthRoot(32, 5); // 2
```

## Invariant

For a number `x` that is a perfect power, raising the nth root back to the power `n` gives `x` again: `nthRoot(x, n) ** n` equals `x`. Floating point arithmetic can leave a tiny error, so the comparison rounds the result first. Here is the worked example from above checked with this invariant:

```js
const root = nthRoot(32, 5);
console.log(root); // 2
console.log(Math.round(root ** 5)); // 32
```

## Bounded variations

The same invariant holds for other perfect powers. Each line prints the root, then the rounded result of raising it to the power `n`:

```js
console.log(nthRoot(8, 3)); // 2
console.log(Math.round(nthRoot(8, 3) ** 3)); // 8
console.log(nthRoot(81, 4)); // 3
console.log(Math.round(nthRoot(81, 4) ** 4)); // 81
console.log(nthRoot(243, 5)); // 3
console.log(Math.round(nthRoot(243, 5) ** 5)); // 243
console.log(nthRoot(1024, 10)); // 2
console.log(Math.round(nthRoot(1024, 10) ** 10)); // 1024
```

## Boundary example

The root of `1` is always `1`, whatever `n` is, and the invariant still holds:

```js
console.log(nthRoot(1, 7)); // 1
console.log(Math.round(nthRoot(1, 7) ** 7)); // 1
```
