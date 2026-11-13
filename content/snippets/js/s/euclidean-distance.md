---
title: Calculate the Euclidean distance in JavaScript
language: javascript
tags: [math,algorithm]
cover: ancient-greek-building
excerpt: Use JavaScript's `Math.hypot()` to calculate the Euclidean distance between two points.
listed: true
dateModified: 2023-12-18
---

## Definition

The [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) between two points is the **length of the line segment connecting them**. The formula for calculating it in 2D is equal to the **hypotenuse** of a right triangle, given by the [Pythagorean theorem](https://en.wikipedia.org/wiki/Pythagorean_theorem).

<latex-expression>

```math
d^2 = x^2 + y^2 \\
x = x_2 - x_1\\
y = y_2 - y_1\\
d^2 = (x_2 - x_1)^2 + (y_2 - y_1)^2 \\
d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
```

</latex-expression>

## Implementation

JavaScript's `Math.hypot()` method can be used to calculate the Euclidean distance between two points in **2 dimensions**.

```js
const distance = (x0, y0, x1, y1) => Math.hypot(x1 - x0, y1 - y0);

distance(1, 1, 2, 3); // ~2.2361
```

In **3 dimensions**, the formula is the same, but with an additional dimension. For readability's sake, we should also use represent **each point as an array**.

```js
const distance = ([x0, y0, z0], [x1, y1, z1]) =>
  Math.hypot(x1 - x0, y1 - y0, z1 - z0);

distance([1, 1, 1], [2, 3, 2]); // ~2.4495
```

In fact, for **any number of dimensions**, we can use the same formula. Using `Object.keys()` and `Array.prototype.map()`, we can map each coordinate to its difference between the two points. Then, using the spread operator (`...`), we can pass the resulting values to `Math.hypot()`.

```js
const euclideanDistance = (a, b) =>
  Math.hypot(...Object.keys(a).map(k => b[k] - a[k]));

euclideanDistance([1, 1], [2, 3]); // ~2.2361
euclideanDistance([1, 1, 1], [2, 3, 2]); // ~2.4495
euclideanDistance([1, 1, 1, 1], [2, 3, 2, 3]); // ~3.1623
```

## Complexity

The **time complexity** of the algorithmic implementation is `O(n)`, where `n` is the number of dimensions, due to the complexity of `Array.prototype.map()`.

## Derivation of the result

Here is how `distance(1, 1, 2, 3)` becomes `~2.2361`. First, the differences between the coordinates are computed (`x1 - x0` and `y1 - y0`). Then each difference is squared, the squares are added, and the square root of the sum is taken, which is what `Math.hypot()` does in one call:

```js
const [x0, y0, x1, y1] = [1, 1, 2, 3];
const dx = x1 - x0;
const dy = y1 - y0;
console.log(dx, dy); // 1 2
console.log(dx ** 2, dy ** 2); // 1 4
console.log(dx ** 2 + dy ** 2); // 5
console.log(Math.sqrt(dx ** 2 + dy ** 2).toFixed(4)); // 2.2361
console.log(distance(x0, y0, x1, y1).toFixed(4)); // 2.2361
```

## Derivation with arrays

In the any-dimension version, each point is an array. `Object.keys()` gives the indexes, `Array.prototype.map()` turns every index into a coordinate difference, and the spread operator passes those differences to `Math.hypot()`:

```js
const a = [1, 1], b = [2, 3];
console.log(JSON.stringify(Object.keys(a))); // ["0","1"]
console.log(JSON.stringify(Object.keys(a).map(k => b[k] - a[k]))); // [1,2]
console.log(Math.hypot(...Object.keys(a).map(k => b[k] - a[k])).toFixed(4)); // 2.2361
```

## Boundary example

If both points are the same, every difference is `0`, so the distance is `0`. If the points lie on one axis-aligned right triangle with sides `3` and `4`, the distance is exactly `5`:

```js
console.log(distance(3, 4, 3, 4)); // 0
console.log(distance(0, 0, 3, 4)); // 5
```
