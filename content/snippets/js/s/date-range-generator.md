---
title: Date range generator in JavaScript
shortTitle: Date range generator
language: javascript
tags: [date,function,generator]
cover: portal-timelapse
excerpt: Create a generator that generates all dates in a given range.
listed: true
dateModified: 2024-07-31
---

Generating a range of `Date` values is very common when working with any type of data that involves dates. Luckily, ES6 introduced **generators**, which can be used to create a generator function that yields all dates in a given range, allowing us to save memory and time.

> [!NOTE]
>
> If you're **not familiar with generator functions**, be sure to read the [range generator article](/js/s/range-generator) first.

As mentioned in [a previous post](/js/s/date-yesterday-today-tomorrow), we can manipulate `Date` objects using `Date.prototype.getDate()` and `Date.prototype.setDate()`. This allows us to easily **increment or decrement dates**.

Knowing that, we can construct a generator function that uses a `for` **loop** to iterate over the dates in the given range, incrementing by a specified step, allowing us to `yield` each date in the range.

```js
const dateRange = function* (start, end, step = 1) {
  for (
    let d = new Date(start);
    d < new Date(end);
    d.setDate(d.getDate() + step)
  )
    yield new Date(d);
};

[...dateRange('2021-06-01','2021-06-04')];
// [ 2021-06-01, 2021-06-02, 2021-06-03 ]

## Comparing two approaches

There are two common ways to generate a date range. The generator approach above is **lazy** — it yields one date at a time and is memory-efficient for large ranges. The alternative is an **eager array** approach that builds the entire range up-front.

```js
// Approach 1: Generator (lazy) — already shown above
// Yields one Date at a time; memory O(1) during iteration
const dateRange = function* (start, end, step = 1) {
  for (
    let d = new Date(start);
    d < new Date(end);
    d.setDate(d.getDate() + step)
  )
    yield new Date(d);
};

// Approach 2: Array (eager) — builds the full list up-front
// Memory O(n) where n = number of dates in the range
const dateRangeArray = (start, end, step = 1) => {
  const result = [];
  for (
    let d = new Date(start);
    d < new Date(end);
    d.setDate(d.getDate() + step)
  )
    result.push(new Date(d));
  return result;
};

// Both produce the same dates for the same input:
[...dateRange('2021-06-01', '2021-06-04')];
// [ 2021-06-01, 2021-06-02, 2021-06-03 ]

dateRangeArray('2021-06-01', '2021-06-04');
// [ 2021-06-01, 2021-06-02, 2021-06-03 ]
```

| | Generator (`dateRange`) | Array (`dateRangeArray`) |
|---|---|---|
| **Memory** | O(1) during iteration | O(n) — holds all dates |
| **Reusable** | Only once per iterator | Yes — plain array |
| **Interop** | Needs `[...spread]` or `for…of` | Direct array methods |
| **Best for** | Large or unknown ranges | Small ranges, sorting, indexing |
```
