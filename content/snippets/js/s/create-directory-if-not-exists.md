---
title: Create a directory if it doesn't exist using Node.js
shortTitle: Create directory if not exists
language: javascript
tags: [node]
cover: misty-mountains
excerpt: Learn how to create a directory using Node.js, if it doesn't exist.
listed: true
dateModified: 2024-03-08
---

When working with files and directories in Node.js, you might want to create a directory, if it doesn't exist yet. The default behavior of the filesystem methods in Node.js is to throw an error if the directory already exists, so you need to roll up your own solution for this task.

## Asynchronous approach

Most commonly, you'll want to create a directory asynchronously, using `fs.mkdir()`. This method returns a `Promise`, that will reject if the directory already exists. In order to remedy that, we can use `fs.access()` to check if the directory exists, and then create it if it doesn't.

```js
import { access, mkdir } from 'fs/promises';

const createDirIfNotExists = dir =>
  access(dir)
    .then(() => undefined)
    .catch(() => mkdir(dir));

await createDirIfNotExists('test');
// Resolves to `undefined` and creates the directory 'test' when it does not exist

await createDirIfNotExists('test');
// Boundary case: resolves to `undefined` without throwing `EEXIST` when 'test' already exists
```

### Behavior and regression contract

- **Missing directory (`'test'` absent):** `access('test')` rejects with `ENOENT`, routing execution into `.catch(() => mkdir('test'))`, which creates `'test'` and resolves to `undefined`.
- **Existing directory boundary (`'test'` present):** `access('test')` resolves, so `.then(() => undefined)` short-circuits and prevents `mkdir('test')` from rejecting with `EEXIST`.
- **Single-level path contract:** Without `{ recursive: true }`, passing a nested path whose parent directory does not exist (such as `'parent/child'`) rejects with `ENOENT`.

## Synchronous approach

While the asynchronous approach is generally preferred, you might want to create a directory synchronously in some cases. You can use `fs.existsSync()` to check if the directory exists, and `fs.mkdirSync()` to create it.

```js
import { existsSync, mkdirSync } from 'fs';

const createDirIfNotExists = dir =>
  !existsSync(dir) ? mkdirSync(dir) : undefined;

createDirIfNotExists('test');
// Synchronously creates the directory 'test', if it doesn't exist
```
