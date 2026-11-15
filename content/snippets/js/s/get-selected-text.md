---
title: How can I get the currently selected text in the browser?
shortTitle: Get selected text
language: javascript
tags: [browser]
cover: white-tablet-2
excerpt: Learn how to get the currently selected text in the browser using JavaScript.
listed: true
dateModified: 2024-07-16
---

When working with text in the browser, you may need to **get the currently selected text** to perform various operations. This can be useful for implementing features like copy-paste functionality, text highlighting, or custom context menus.

As usual, JavaScript provides a way to achieve this using `Window.getSelection()`, which returns a `Selection` object representing the text currently selected in the document. You can then use `Selection.toString()` to get the actual text content.

Suppose the user has selected the text `Lorem ipsum` on the page. `window.getSelection()` returns the current `Selection` object, and `Selection.toString()` converts its selected text into the string `'Lorem ipsum'`. When there is no active text selection, it returns an empty string (`''`).

```js
const getSelectedText = () => window.getSelection().toString();

// With "Lorem ipsum" selected:
const selectedText = getSelectedText();
console.assert(selectedText === 'Lorem ipsum', 'Expected "Lorem ipsum".');
console.log(selectedText); // 'Lorem ipsum'

// With no text selected:
window.getSelection().removeAllRanges();
const emptyText = getSelectedText();
console.assert(emptyText === '', 'Expected an empty string.');
console.log(emptyText); // ''
```

> [!NOTE]
>
> A more **advanced use case** of this functionality can be found in [the copy text to clipboard article](/js/s/copy-text-to-clipboard#using-document-exec-command-copy), used to select and copy text to the clipboard.
