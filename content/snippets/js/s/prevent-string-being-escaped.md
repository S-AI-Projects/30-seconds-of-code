---
title: Prevent a string from being escaped in JavaScript
shortTitle: Prevent string escaping
language: javascript
tags: [string]
cover: glass-blowing
excerpt: Strings in JavaScript can be escaped in various ways. But how do you prevent a string from being escaped? Here's a handy trick for that.
listed: true
dateModified: 2021-06-17
---

By default, when JavaScript sees an escape character (`\`), it will escape the character after it. However, there are cases where you might not want this behavior (e.g. when you want to store a Windows path as a string). For these cases, you can use a template literal and the `String.raw()` tag function:

```js
const path = `C:\web\index.html`; // 'C:webindex.html'

const unescapedPath = String.raw`C:\web\index.html`; // 'C:\web\index.html'
```

The behavior depends on one precondition: `String.raw()` works on the source text of a template literal, so it keeps the backslashes exactly as you typed them. In a normal template literal, `\n` is an escape sequence that becomes a single newline character, while with `String.raw()` it stays as two characters, a backslash followed by `n`:

```js
const escaped = `\n`;
const raw = String.raw`\n`;

escaped.length; // 1
raw.length; // 2
raw; // '\\n'
```
