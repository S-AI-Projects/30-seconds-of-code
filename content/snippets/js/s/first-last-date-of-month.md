---
title: Get the first or last date of a month using JavaScript
shortTitle: First or last date of a month
language: javascript
tags: [date]
cover: polar-bear
excerpt: Use the `Date` object and some clever tricks to get the first or last date of a month in JavaScript.
listed: true
dateModified: 2024-02-17
---

Getting the first date of a month is usually pretty simple. But how about getting the last date of a month? Here's how you can do both using JavaScript.

## Get the first date of a month

Given any `Date` object, you can use `Date.prototype.getFullYear()` and `Date.prototype.getMonth()` to get the **current year and month** from the given date. In order to get the first date of a month, you just need to create a new `Date` object, using these methods, and **set the day** to `1`.

```js
const firstDateOfMonth = (date = new Date()) =>
  new Date(date.getFullYear(), date.getMonth(), 1);

firstDateOfMonth(new Date('2015-08-11')); // '2015-08-01'
```

## Get the last date of a month

In order to get the last date of a month, we can use a clever trick on top of the previous code snippet. Instead of setting the day to `1`, we can set it to `0`. This will give us the **last day of the previous month**. In order for this to work, we'll need to **advance the month** by `1` as well.

```js
const lastDateOfMonth = (date = new Date()) =>
  new Date(date.getFullYear(), date.getMonth() + 1, 0);

lastDateOfMonth(new Date('2015-08-11')); // '2015-08-31'
```

## Step-by-step derivation

Taking `const inputDate = new Date('2015-08-11')` as an example:

1. **Extract components**:
   - `inputDate.getFullYear()` evaluates to `2015`.
   - `inputDate.getMonth()` evaluates to `7` (months are 0-indexed in JavaScript: 0 is January, 7 is August).
2. **First date computation**:
   - `new Date(2015, 7, 1)` sets day to `1`, producing `2015-08-01`.
3. **Last date computation**:
   - `inputDate.getMonth() + 1` evaluates to `8` (the index for September).
   - `new Date(2015, 8, 0)` invokes JavaScript's date normalization: day `0` resolves to the day preceding September 1st, which is the final day of August (`2015-08-31`).

## Boundary examples

```js
// Leap year February (2024 is a leap year)
lastDateOfMonth(new Date('2024-02-10')); // 2024-02-29

// Common year February (2023 is not a leap year)
lastDateOfMonth(new Date('2023-02-10')); // 2023-02-28

// Year-end boundary (December): month + 1 wraps cleanly without corrupting the year
firstDateOfMonth(new Date('2023-12-25')); // 2023-12-01
lastDateOfMonth(new Date('2023-12-25'));  // 2023-12-31
```

