---
title: Detect the user's OS in the browser with JavaScript
shortTitle: Browser OS detection
language: javascript
tags: [browser]
cover: dark-leaves-2
excerpt: Learn how to easily detect the user's operating system in the browser using JavaScript.
listed: true
dateModified: 2025-04-19
---

I was recently implementing a hotkeys feature for this website (hint use `⌘` or `Ctrl` to see what I'm talking about), and I needed to **detect the user's operating system in the browser**. Seems simple, right? Yet, as with many things in the browser, it's more nuanced than you may think.

## `Navigator.platform`

The most common answer online, and the one I was vaguely aware of, is based on the use of the `Navigator.platform` property. It's straightforward, too:

```js
const isMac = navigator.platform.toLowerCase().includes('mac');

isMac; // true if the user is on a Mac, false otherwise
```

All we do here is take the value, use `String.prototype.toLowerCase()`, and check if it contains the string `mac`. If it does, we know the user is on a Mac.

**How it works — step by step:** `navigator.platform` returns a vendor string such as `'MacIntel'` or `'Win32'`. `.toLowerCase()` normalises the case (`'macintel'`), and `.includes('mac')` checks whether the substring `'mac'` appears **anywhere** in that string.

```js
// Concrete intermediate values for 'MacIntel':
// navigator.platform           → 'MacIntel'
// .toLowerCase()               → 'macintel'
// .includes('mac')             → true  ✔ user is on a Mac

// Boundary — Windows platform string:
// navigator.platform           → 'Win32'
// .toLowerCase()               → 'win32'
// .includes('mac')             → false ✔ not a Mac
```

> **Ambiguous case — iPad on iPadOS 13+:** Since iPadOS 13, `navigator.platform` reports `'MacIntel'` on iPad devices to match Safari's desktop-site default. This means `.includes('mac')` returns `true` for iPads too, making it **impossible to distinguish a real Mac from an iPad** using `Navigator.platform` alone. This is one of the reasons MDN marks the property as **deprecated and no longer recommended** for use.

Cool. Except, MDN says it's **deprecated and no longer recommended** for use. <br/> So much for that solution!

## `Navigator.userAgentData`

<baseline-support featureId="ua-client-hints">
</baseline-support>

The consensus about the **bleeding edge solution** seems to revolve around `Navigator.userAgentData`, with some debate surrounding the need to use `NavigatorUAData.getHighEntropyValues()`. While the latter doesn't seem strictly necessary in most cases, the former seems relatively promising.

```js
const isMac = navigator.userAgentData?.platform === 'macOS';

isMac; // true if the user is on a Mac, false otherwise
```

The problem in this case is the exact opposite of the previous one: **support for this is pretty limited** (at the time of writing only Chrome and Edge support it). So, while it may be a future solution, it's not at this time.

## `Navigator.userAgent`

We've once more arrived at the trusty `Navigator.userAgent` property. We've previously seen how to use it to [detect device type](/js/s/detect-device-type). It's not as elegant, yet it works everywhere.

```js
const isMac = /mac/i.test(navigator.userAgent);

isMac; // true if the user is on a Mac, false otherwise
```

You can use either `RegExp.prototype.test()` or the lowercase and `String.prototype.includes()` method, as shown in the first example. Performance shouldn't be a concern here, as you're probably only checking this once per page load.

## Conclusion

A simple task to detect the user's operating system in the browser can quickly spiral into a rabbit hole of figuring out what to use and how reliable it is. I guess the lesson here is that, even though JavaScript has come a very long way in recent years, we're still left grappling with answers that rely on **legacy solutions** or are far too optimistic about **browser support**. Researching the right solution is very much a necessity still and it doesn't seem like our AI assistants can be trusted 100% of the time.
