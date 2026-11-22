---
title: Check if a string contains a substring in JavaScript
shortTitle: String contains substring
language: javascript
tags: [string]
cover: cave-explorer
excerpt: Let's have a look at how to check if a string contains a substring in JavaScript.
listed: true
dateModified: 2022-07-27
---

## String.prototype.includes()

The most straightforward substring search option is `String.prototype.includes()`, introduced in ES6. It's a simple method that returns a boolean value depending on whether the string contains the substring or not.

```js
const str = 'Hello world';
str.includes('world'); // true
str.includes('foo'); // false
```

**Derivation:** `str` holds the character sequence `'Hello world'` (11 characters). `includes('world')` scans the string from index 0, finds the exact byte sequence `w-o-r-l-d` starting at index 6, and returns `true`. `includes('foo')` performs the same scan, finds no matching position, and returns `false`.

**Boundary example — position argument:** `String.prototype.includes()` accepts an optional second argument `position` (default `0`) that sets the index at which to begin searching. Passing an offset past the substring's location causes it to be missed:

```js
const str = 'Hello world';
str.includes('Hello', 0);  // true  — search starts at index 0, 'Hello' found at 0
str.includes('Hello', 1);  // false — search starts at index 1, skips the 'H', substring not found
str.includes('', 100);     // true  — empty string is always found (even beyond string length)
```

## String.prototype.indexOf()

Another option is `String.prototype.indexOf()`, which can be preferable if you need to support legacy browsers. As this methods returns the index of the first occurrence of the substring, you need to compare it to `-1` to know if the substring was found or not.

```js
const str = 'Hello world';
str.indexOf('world') !== -1; // true
str.indexOf('foo') !== -1; // false
```

## Case-insensitive substring search

Both methods presented so far are case-sensitive. If you need to search for a substring that is case-insensitive, you can use `String.prototype.toLowerCase()` to convert both strings to lowercase. Then you can compare them, using any of the previous methods.

```js
const str = 'Hello world';
const token = 'WORLD';
str.toLowerCase().includes(token.toLowerCase()); // true
```
