---
title: What is the difference between encodeURI() and encodeURIComponent() in JavaScript?
shortTitle: encodeURI() vs encodeURIComponent()
language: javascript
tags: [browser]
cover: laptop-view
excerpt: JavaScript provides two methods for encoding characters to URL-safe strings. Do you know when to use each one?
listed: true
dateModified: 2021-06-12
---

## encodeURIComponent()

The [`encodeURIComponent()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURIComponent) function encodes everything in the given string, except `A-Z a-z 0-9 - _ . ! ~ * ' ( )`. You should use this function if the string you are encoding is only part of a URL.

```js
const partOfURL = 'my-page#with,speci@l&/"characters"?';
const fullURL = 'https://my-website.com/my-page?query="a%b"&user=1';

encodeURIComponent(partOfURL); // Good, escapes special characters
// 'my-page%23with%2Cspeci%40l%26%2F%22characters%22%3F'

encodeURIComponent(fullURL);  // Bad, encoded URL is not valid
// 'https%3A%2F%2Fmy-website.com%2Fmy-page%3Fquery%3D%22a%25b%22%26user%3D1'
```

## encodeURI()

The [`encodeURI()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURI) function encodes everything in the given string, except `A-Z a-z 0-9 ; , / ? : @ & = + $ - _ . ! ~ * ' ( ) #`. You should use this function if the string you are encoding is a full URL.

```js
const partOfURL = 'my-page#with,speci@l&/"characters"?';
const fullURL = 'https://my-website.com/my-page?query="a%b"&user=1';

encodeURI(partOfURL); // Bad, does not escape all special characters
// 'my-page#with,speci@l&/%22characters%22?'

encodeURI(fullURL);  // Good, encoded URL is valid
// 'https://my-website.com/my-page?query=%22a%25b%22&user=1'
```

## Comparison and boundary behavior

Both functions convert disallowed characters into uppercase UTF-8 `%XX` hex byte sequences, but they differ in how they classify the **11 URI structural delimiters** (`; , / ? : @ & = + $ #`):

- `encodeURIComponent()` preserves only the **71 unreserved characters** (`A-Z a-z 0-9 - _ . ! ~ * ' ( )`) and percent-encodes all 11 delimiters so query values cannot break out of a URL parameter.
- `encodeURI()` preserves those 71 characters **plus the 11 structural delimiters** (82 characters total), keeping scheme (`://`), path (`/`), query (`?`, `&`, `=`), and fragment (`#`) separators intact.

```js
const partOfURL = 'my-page#with,speci@l&/"characters"?';
const fullURL = 'https://my-website.com/my-page?query="a%b"&user=1';
const delimiters = ';,/?:@&=+$#';

console.log('component(part):', encodeURIComponent(partOfURL));
console.log('uri(part):      ', encodeURI(partOfURL));
console.log('component(full):', encodeURIComponent(fullURL));
console.log('uri(full):      ', encodeURI(fullURL));
console.log('component(empty):', JSON.stringify(encodeURIComponent('')));
console.log('uri(empty):      ', JSON.stringify(encodeURI('')));
console.log('component(delim):', encodeURIComponent(delimiters));
console.log('uri(delim):      ', encodeURI(delimiters));
// Output:
// component(part): my-page%23with%2Cspeci%40l%26%2F%22characters%22%3F
// uri(part):       my-page#with,speci@l&/%22characters%22?
// component(full): https%3A%2F%2Fmy-website.com%2Fmy-page%3Fquery%3D%22a%25b%22%26user%3D1
// uri(full):       https://my-website.com/my-page?query=%22a%25b%22&user=1
// component(empty): ""
// uri(empty):       ""
// component(delim): %3B%2C%2F%3F%3A%40%26%3D%2B%24%23
// uri(delim):       ;,/?:@&=+$#
```
