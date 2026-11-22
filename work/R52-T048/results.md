# R52-T048 Results — transpose-matrix

## Task
Item: **transpose matrix**; source anchor: `transpose matrix`; code anchor: `transpose`.

## Worked Example (from article)
```js
const transpose = arr => arr[0].map((col, i) => arr.map(row => row[i]));

transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]);
// [[1, 4, 7, 10], [2, 5, 8, 11], [3, 6, 9, 12]]
```
`arr[0].map` iterates over column indices (0, 1, 2). For each column index `i`, `arr.map(row => row[i])` picks the i-th element from every row, forming a new row of the transposed matrix.

## Boundary Case — Single-row (1 × N)
**Precondition:** `arr` has exactly one row of N elements.  
`arr[0].map` iterates N columns; for each column `i`, `arr.map(row => row[i])` returns a one-element array `[arr[0][i]]`.

```js
transpose([[1, 2, 3]]);
// [[1], [2], [3]]
```

## Misconception — Jagged Array (Unsupported)
`transpose` assumes a **rectangular** matrix. The column count is fixed by `arr[0].length`. For any row shorter than row 0, `row[i]` is `undefined`, silently corrupting the result:

```js
transpose([[1, 2, 3], [4, 5]]);
// [[1, 4], [2, 5], [3, undefined]]  ← third column is broken
```

No error is thrown; callers must validate input shape themselves.

## check.py Results
| Assertion | Result |
|-----------|--------|
| `transpose([[1,2,3],[4,5,6],[7,8,9],[10,11,12]])` == `[[1,4,7,10],[2,5,8,11],[3,6,9,12]]` | ✅ PASS |
| `transpose([[1,2,3]])` == `[[1],[2],[3]]` | ✅ PASS |
| Deliberate wrong assertion raises `AssertionError` | ✅ PASS |

## Build
- Pages built: **909**
- Exit code: **0**
- New content verified in `dist/js/s/transpose-matrix/index.html`
