---
title: Implement the Caesar cipher in JavaScript
shortTitle: Caesar cipher
language: javascript
tags: [algorithm,string]
cover: waves-from-above
excerpt: The Caesar cipher is a simple substitution cipher, which can be easily implemented with a few lines of JavaScript code.
listed: true
dateModified: 2023-12-17
---

## Definition

The [Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher) is a simple **substitution cipher**, in which each letter is replaced by another letter a fixed number of positions down the alphabet. For example, with a left shift of `3`, `D` would be replaced by `A`, `E` would become `B`, and so on.

## Implementation

> [!NOTE]
>
> The following implementation only works for **Latin letters** (`A` to `Z` and `a` to `z`), ignoring all other characters.

Depending on the **mode** (decided by the `decrypt` parameter), the cipher either adds or subtracts the `shift` from the character code of each letter, wrapping around the alphabet as needed. This is achieved by using the modulo operator (`%`) and the ternary operator (`?`).

Then, using the spread operator (`...`) and `Array.prototype.map()`, the algorithm **iterates over the letters** of the given string. For each letter, it **converts it to its character code** using `String.prototype.charCodeAt()`, **applies the shift** and **converts it back to a letter** using `String.fromCharCode()`. If the character code is not in the range `65` (`A`) to `90` (`Z`) or `97` (`a`) to `122` (`z`), it is left as is.

Finally, the letters are **combined into a string** using `Array.prototype.join()`.

```js
const caesarCipher = (str, shift, decrypt = false) => {
  const s = decrypt ? (26 - shift) % 26 : shift;
  const n = s > 0 ? s : 26 + (s % 26);
  return [...str]
    .map((l, i) => {
      const c = str.charCodeAt(i);
      if (c >= 65 && c <= 90)
        return String.fromCharCode(((c - 65 + n) % 26) + 65);
      if (c >= 97 && c <= 122)
        return String.fromCharCode(((c - 97 + n) % 26) + 97);
      return l;
    })
    .join('');
};

caesarCipher('Hello World!', 23); // 'Ebiil Tloia!'
caesarCipher('Hello World!', -3); // 'Ebiil Tloia!'
caesarCipher('Ebiil Tloia!', 23, true); // 'Hello World!'
caesarCipher('Ebiil Tloia!', -3, true); // 'Hello World!'
```

> [!CAUTION]
>
> The Caesar cipher is one of the easiest ciphers to break. **Do not use it for sensitive data.**

## Intermediate values

Here is how the letter `H` is processed with a shift of `23`. The method works with character codes:

```js
const c = 'H'.charCodeAt(0);
console.log(c); // 72
console.log(c - 65 + 23); // 30
console.log((c - 65 + 23) % 26); // 4
console.log(String.fromCharCode(((c - 65 + 23) % 26) + 65)); // E
```

## Boundary example

Letters near the end of the alphabet wrap around to the start. With a shift of `3`, `x`, `y` and `z` become `a`, `b` and `c`:

```js
console.log(caesarCipher('xyz', 3)); // abc
console.log(caesarCipher('abc', 3, true)); // xyz
```

## Comparing two methods

The same result can be produced without character codes, by looking letters up in an alphabet string. The difference is the intermediate representation: the source method works with character codes (`72` for `H`), while the alternative works with positions in the alphabet (`7` for `H`).

```js
const caesarCipherAlt = (str, shift) => {
  const upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lower = 'abcdefghijklmnopqrstuvwxyz';
  const n = ((shift % 26) + 26) % 26;
  return [...str]
    .map(l => {
      if (upper.includes(l)) return upper[(upper.indexOf(l) + n) % 26];
      if (lower.includes(l)) return lower[(lower.indexOf(l) + n) % 26];
      return l;
    })
    .join('');
};

console.log(caesarCipher('Hello World!', 23)); // Ebiil Tloia!
console.log(caesarCipherAlt('Hello World!', 23)); // Ebiil Tloia!
console.log('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.indexOf('H')); // 7
console.log(caesarCipherAlt('xyz', 3)); // abc
```
