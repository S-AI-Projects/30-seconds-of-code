---
title: Check if a JavaScript collection is empty
shortTitle: Value is empty
language: javascript
tags: [type,array,object,string]
cover: mountain-lake
excerpt: Quickly determine if a collection of values is empty in JavaScript.
listed: true
dateModified: 2024-06-10
---

When we say a collection of values is _empty_, we mean that it has no elements with meaningful values. In JavaScript, we can consider an array, object, or string as empty if it has no elements, properties, or characters, respectively.

While arrays and strings share a `length` property, objects don't have a direct way to determine their size. In order to do so, we can use `Object.keys()` to get an **array of the object's keys** and then check its length. Luckily, `Object.keys()` also works on arrays and string, returning their **indices** as strings.

Given this information, we can use `Array.prototype.length` to check if the resulting **keys are empty**. If the value is `null` or `undefined`, we can consider it empty as well.

```js
const isEmpty = val =>
  val === null || val === undefined || !Object.keys(val).length;

isEmpty([]);              // true
isEmpty([1, 2]);          // false
isEmpty({});              // true
isEmpty({ a: 1, b: 2 });  // false
isEmpty('');              // true
isEmpty('text');          // false
isEmpty(null);            // true
isEmpty(undefined);       // true
```

## Regression protection and mutation testing

A resilient test suite guards this function against common single-token mutations:

1. **Inverted length mutant (`!Object.keys(val).length` -> `Object.keys(val).length`)**:
   - Would invert emptiness: `isEmpty([])` would return `0` (falsy) instead of `true`, and `isEmpty([1])` would return `1` (truthy) instead of `false`.
2. **Missing null/undefined guard (`val === null || val === undefined`)**:
   - Omitting this causes `Object.keys(null)` or `Object.keys(undefined)` to throw `TypeError: Cannot convert undefined or null to object`.

## Boundary examples

```js
// Sparse array with holes: empty slots have no keys
isEmpty(new Array(3)); // true (Object.keys(new Array(3)) === [])

// Primitive numbers and booleans have no enumerable own keys
isEmpty(0);     // true
isEmpty(true);  // true

// Objects with non-enumerable properties or symbols
const obj = {};
Object.defineProperty(obj, 'hidden', { value: 42, enumerable: false });
isEmpty(obj); // true (non-enumerable properties are not included in Object.keys)
```

> [!NOTE]
>
> `isEmpty` relies on `Object.keys()`, which only enumerates an object's own enumerable string keys. As a result, data structures like `Map` or `Set` will always report `true` regardless of their `.size`, because entries are stored internally rather than as enumerable own properties.

