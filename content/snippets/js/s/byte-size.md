---
title: Calculate the byte size of a JavaScript string
shortTitle: Byte size of string
language: javascript
tags: [string]
cover: mountain-lake-cottage-2
excerpt: Figure out the exact number of bytes in a JavaScript string, including Unicode characters.
listed: true
dateModified: 2024-03-09
---

Calculating the byte size of a string is surprisingly tricky, especially when dealing with Unicode characters. The **length of a string** in JavaScript is the number of 16-bit code units in the string, which is not the same as the **number of bytes**. This is especially important when working with non-ASCII characters, which can be represented by multiple bytes.

In order to correctly handle all cases, we can convert the string into a `Blob` object, and then use the `Blob.size` property to get the byte size of the string.

```js
const byteSize = str => new Blob([str]).size;

const helloWorldString = 'Hello World';
helloWorldString.length; // 11
byteSize(helloWorldString); // 11

const emojisString = '😀';
emojisString.length; // 2
byteSize(emojisString); // 4
```

## Limitations and failure cases

While `byteSize` works well for valid strings, there are important limitations to keep in mind:

### 1. Implicit coercion of non-string inputs
`Blob` silently converts non-string inputs to strings via `toString()`, which can lead to surprising results:

```js
byteSize({}); // 15 — coerced to "[object Object]"
byteSize(null); // 4 — coerced to "null"
byteSize(12345); // 5 — coerced to "12345"
```

To guard against unexpected coercion, check that the input is a string:

```js
const safeByteSize = str =>
  typeof str === 'string' ? new Blob([str]).size : undefined;
```

### 2. Environment availability
The `Blob` API is standard in modern browsers and Node.js (v15.7.0+), but unavailable in legacy Node.js or embedded JS engines without a polyfill. In Node.js server environments, `Buffer.byteLength(str, 'utf8')` is the standard alternative.

## Boundary examples

```js
// Empty string
byteSize(''); // 0

// 1-byte ASCII character
byteSize('a'); // 1

// 2-byte UTF-8 character (Latin extended)
byteSize('é'); // 2

// 3-byte UTF-8 character (CJK / Devanagari)
byteSize('字'); // 3
byteSize('अ'); // 3

// 4-byte UTF-8 character (Emoji surrogate pair)
byteSize('😀'); // 4
```

