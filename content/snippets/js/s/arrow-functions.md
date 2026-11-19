---
title: Introduction to arrow functions in JavaScript
shortTitle: Arrow functions introduction
language: javascript
tags: [function]
cover: arrow-functions
excerpt: JavaScript arrow functions are a very useful tool to learn and master. Here's a complete introduction to everything you need to know.
listed: true
dateModified: 2021-06-12
---

## Syntax

In order to understand arrow function syntax, we should start by refactoring a regular function step by step:

```js
function square(a) {
  return a * a;
}
```

We can start by refactoring the function declaration to use a variable assignment:

```js
const square = function (a) {
  return a * a;
}
```

Then, we can refactor the regular `function` to an arrow function:

```js
const square = (a) => {
  return a * a;
}
```

If there's only one argument, we can omit the parentheses around it:

```js
const square = a => {
  return a * a;
}
```

If the function is a single expression, you can omit the curly braces and `return` statement and use an implicit return:

```js
const square = a => a * a;

// Worked example and boundary cases
square(4); // 16
square(0); // 0
square(-3); // 9

// Resource inspection: regular function vs. arrow function
function regularSquare(a) {
  return a * a;
}

typeof square; // 'function'
typeof regularSquare.prototype; // 'object' (allocates a prototype object)
square.prototype; // undefined (no prototype object allocated)
```

### Operation and resource behavior

- **Fixed-cost execution (`O(1)` time and space):** Evaluating `square(4)` (`16`) or boundary inputs like `square(0)` (`0`) and `square(-3)` (`9`)
  passes a primitive IEEE 754 `number` by value and performs a single multiplication with no heap allocation or data copying.
- **Reduced per-function overhead (`O(1)`):** Unlike `function regularSquare(a)`, an arrow function has no `prototype` object (`square.prototype === undefined`),
  cannot be called with `new`, and omits per-call `arguments` and dynamic `this` bindings.
- **Closure allocation trade-off (`O(n)`):** Defining an arrow function inside a class field or repeated factory allocates one closure object per instance (`O(n)` for `n` instances),
  whereas a shared prototype method allocates a single function object (`O(1)`).

## Execution context

The main difference between arrow functions and regular functions is execution context (i.e. the value of `this`). Technically speaking, most other differences often mentioned either stem from this one or are side effects of it.

In a regular function, `this` is dynamic and depends on how the function was invoked:

```js
function simple() { return this; }
const object = {
  method() { return this; }
};
class Class {
  classMethod() { console.log(this); }
}
const instance = new Class();

simple();                   // `this` refers to the global object
new simple();               // `this` refers to the newly created instance

object.method();            // `this` refers to `object`
simple.call(object);        // `this` refers to `object`

instance.classMethod();     // `this` refers to `instance`
setTimeout(
  instance.classMethod, 0   // `this` refers to the global object
);
```

Arrow functions, unlike regular ones, don't define their own execution context therefore `this` inside an arrow function always refers to the lexical `this` (i.e. the scope in which the arrow function was defined).

```js
const simple = () => this;
const object = {
  method: () => this
};
class Class {
  classMethod = () => { console.log(this); }
}
const instance = new Class();

simple();                   // `this` refers to the global object
new simple();               // Uncaught TypeError: simple is not a constructor

object.method();            // `this` refers to the global object
simple.call(object);        // `this` refers to the global object

instance.classMethod();     // `this` refers to `instance`
setTimeout(
  instance.classMethod, 0   // `this` refers to `instance`
);
```

As you can see from these examples, there's a difference in how constructors work due to the execution context and how it's resolved. Regular functions can be used as constructors in contrast to arrow functions which will throw a `TypeError` instead.

Moreover, arrow functions and regular functions present some differences when used to define class methods. A regular function method will end up with a different execution context when passed as a callback. This can be handled using `Function.prototype.bind()` or by using an arrow function which doesn't have this issue.

If you want to read more about the `this` keyword, you should check out our [previous article on the subject](/js/s/this).
