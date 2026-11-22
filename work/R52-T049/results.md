# R52-T049 Results — reorder-function-arguments

## Task
Item: **reorder function arguments**; source anchor: `Flip function arguments`; code anchor: `flip`.

## Worked Example (from article)
```js
const flip = fn => (first, ...rest) => fn(...rest, first);

const parseInteger = flip(Number.parseInt);
parseInteger(8, '10'); // 8 (10 in base 8)

const parseIntegerBase16 = parseInteger.bind(null, 16);
parseIntegerBase16('10'); // 16 (10 in base 16)
```

`flip(fn)` creates a higher-order wrapper closure over `fn`. When called with arguments `(first, ...rest)`, it unpacks `rest` followed by `first` when invoking `fn`. In `parseInteger(8, '10')`, `first = 8` and `rest = ['10']`, resulting in `Number.parseInt('10', 8) === 8`.

## Resource Behavior: Time, Space, and Copy/View Behavior
- **Time complexity:** $O(k)$ per invocation where $k$ is the total argument count. Collecting `...rest` into an array and spreading `...rest` into the call site both scale linearly with the number of rest parameters.
- **Space complexity:** $O(k)$ transient memory allocation per invocation to hold the `rest` arguments array. The closure itself maintains an $O(1)$ persistent reference to `fn`.
- **Copy vs. view behavior:** Rest parameter gathering and spread syntax perform shallow copies of references and primitives. Object references are passed without cloning underlying state.

## Boundary Example — Single Argument
When invoked with a single argument, `first` captures that argument, `rest` is empty (`[]`), and spreading `...rest` introduces zero arguments before `first`. The target function receives `first` as its initial and only argument.

```js
const identity = flip(x => x);
identity('hello'); // 'hello'
```

## check.py Results
| Assertion | Result |
|-----------|--------|
| `parseInteger(8, '10')` == `8` | ✅ PASS |
| `parseIntegerBase16('10')` == `16` | ✅ PASS |
| `identity('hello')` == `'hello'` | ✅ PASS |
| Deliberate wrong assertion raises `AssertionError` | ✅ PASS |

## Build
- Verified with `npm run build`
