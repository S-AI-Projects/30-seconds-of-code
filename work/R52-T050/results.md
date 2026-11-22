# R52-T050 Results — check-array-values-are-truthy

## Task
Item: **check array values are truthy**; source anchor: `Check if all values in an array are truthy`; code anchor: `all`.

## Worked Examples (from article)
```js
const all = (arr, fn = Boolean) => arr.every(fn);

all([4, 2, 3], x => x > 1); // true
all([1, 2, 3]); // true
```

## Boundary Example — Empty Array
Under ECMAScript rules for `Array.prototype.every()`, iterating an empty array vacuously yields `true` regardless of the predicate function passed:
```js
all([]); // true
all([], () => false); // true
```

## Mutation Analysis & Regression Protection
### Mutant Under Test
A single-operation operator replacement mutant replaces `every` with `some`:
```js
const mutantSome = (arr, fn = Boolean) => arr.some(fn);
```

### Distinguishing Test Cases
1. **Mixed truthy and falsy values (`[1, 0, 3]`):**
   - Correct implementation (`all` / `arr.every`): evaluates to `false` because `0` is falsy.
   - Mutant implementation (`mutantSome` / `arr.some`): evaluates to `true` because at least one element is truthy (`1`).
   - Result: Mutant killed.

2. **Empty array (`[]`):**
   - Correct implementation: evaluates to `true` (vacuous truth).
   - Mutant implementation: evaluates to `false` (no element satisfies predicate).
   - Result: Mutant killed.

## check.py Results
| Assertion | Expected | Actual | Result |
|-----------|----------|--------|--------|
| `all([4, 2, 3], x => x > 1)` | `true` | `true` | ✅ PASS |
| `all([1, 2, 3])` | `true` | `true` | ✅ PASS |
| `all([])` | `true` | `true` | ✅ PASS |
| `all([], () => false)` | `true` | `true` | ✅ PASS |
| `all([1, 0, 3])` | `false` | `false` | ✅ PASS |
| Mutant `arr.some` on `[1, 0, 3]` | `true` (distinguished) | `true` | ✅ KILLED |
| Mutant `arr.some` on `[]` | `false` (distinguished) | `false` | ✅ KILLED |
| Deliberate wrong assertion raises `AssertionError` | `AssertionError` | `AssertionError` | ✅ PASS |

## Build
- Verified with `npm run build` (909 pages built successfully).
