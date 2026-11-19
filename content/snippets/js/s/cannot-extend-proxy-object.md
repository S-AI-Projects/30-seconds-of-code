---
title: You can't extend JavaScript's Proxy object
shortTitle: Extending the Proxy object
language: javascript
tags: [proxy]
cover: icebreaker
excerpt: Turns out the Proxy object is not extensible, but there's a way around its limitations.
listed: true
dateModified: 2023-04-17
---

While the [`Proxy`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy) object seems like it can be extended by any other class in JavaScript, that's not the case. This is due to proxy objects having very atypical semantics and being considered **exotic objects**. Simply put, this means they do not have a prototype and are not extensible.

@[Quick refresher](/js/s/proxy-introduction)

So how do you extend a proxy object? You don't. You can, however, create a class that returns a proxy by returning it from the constructor. After all, this is probably the sort of behavior you're after.

```js
class MyProxy {
  constructor(value) {
    Object.keys(value).forEach(key => (this[key] = value[key]));
    return new Proxy(this, {
      set(object, key, value) {
        console.log(`Called with ${key} = ${value}`);
        object[key] = value;
        return true;
      }
    });
  }
}

const myProxy = new MyProxy({ a: 1 });
myProxy.b = 2; // LOGS: 'Called with b = 2'

// Boundary case: empty initial object
const emptyProxy = new MyProxy({});
emptyProxy.x = 10; // LOGS: 'Called with x = 10'

// Failure cases: extending Proxy directly or passing null
let subclassError;
try {
  class BrokenProxy extends Proxy {}
} catch (err) {
  subclassError = err.name; // 'TypeError'
}
let nullInputError;
try {
  new MyProxy(null);
} catch (err) {
  nullInputError = err.name; // 'TypeError'
}
```

### Limitations and contract

- **Direct subclassing (`extends Proxy`) fails:** Because `Proxy.prototype` is `undefined`,
  evaluating `class BrokenProxy extends Proxy {}` immediately throws a `TypeError`.
- **Constructor contract:** `Object.keys(value)` initializes properties without triggering `set`,
  so `value` must be a non-null object (`new MyProxy(null)` throws a `TypeError`),
  and private class `#fields` cannot be accessed directly through the returned proxy.
