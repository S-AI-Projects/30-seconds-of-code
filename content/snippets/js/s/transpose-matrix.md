---
title: Transpose a matrix in JavaScript
shortTitle: Transpose matrix
language: javascript
tags: [array]
cover: camera-zoom
excerpt: Learn how to transpose a two-dimensional array in JavaScript.
listed: true
dateModified: 2024-07-04
---

A **matrix transpose** is an operation that switches the rows and columns of a two-dimensional array. In other words, it converts the rows of the matrix into columns and vice versa.

In order to perform this operation in JavaScript, we can use `Array.prototype.map()` to create a new array where **each column of the original matrix becomes a row in the transposed matrix**. We can achieve this by mapping over the columns of the original matrix and creating a new row by mapping over the rows and selecting the corresponding element.

```js
const transpose = arr => arr[0].map((col, i) => arr.map(row => row[i]));

transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]);
// [[1, 4, 7, 10], [2, 5, 8, 11], [3, 6, 9, 12]]
```

**Contract:** `transpose` expects a rectangular 2D array — all rows must have the same length. The column count is taken from `arr[0].length`, so every row is indexed up to that length regardless of its actual size.

**Boundary case — single-row (1 × N) matrix:** A matrix with one row transposes into N rows of one element each.

```js
transpose([[1, 2, 3]]);
// [[1], [2], [3]]
```

**Misconception — jagged array:** If rows have unequal lengths, `row[i]` is `undefined` for any row shorter than row 0, silently corrupting the result instead of throwing an error.

```js
// row 1 has only 2 elements, but row 0 drives the column count (3)
transpose([[1, 2, 3], [4, 5]]);
// [[1, 4], [2, 5], [3, undefined]]  ← third column is silently broken
```

@[Further reading](/js/s/matrix-data-structure#transpose)
