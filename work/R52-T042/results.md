# Test Results Evidence for R52-T042

## Target Snippet
- `content/snippets/js/s/prefix-css-property.md`

## Tool Versions
- Node.js: v26.12.1
- Python: 3.15.2
- npm: 11.2.0

## Inputs
- Supported property input: `'appearance'`
  - Supported attributes in `document.body.style`: `appearance: 'auto'`, `webkitAppearance: 'auto'`.
- Boundary input (unsupported property): `'nonExistentProperty'`
  - Supported attributes in `document.body.style`: none matching `nonExistentProperty`, `webkitNonExistentProperty`, `mozNonExistentProperty`, `msNonExistentProperty`, or `oNonExistentProperty`.

## Executed Code
Extracted directly from `content/snippets/js/s/prefix-css-property.md`:
```js
const prefix = prop => {
  const capitalizedProp = prop.charAt(0).toUpperCase() + prop.slice(1);
  const prefixes = ['', 'webkit', 'moz', 'ms', 'o'];
  const i = prefixes.findIndex(
    prefix =>
      typeof document.body.style[prefix ? prefix + capitalizedProp : prop] !==
      'undefined'
  );
  return i !== -1 ? (i === 0 ? prop : prefixes[i] + capitalizedProp) : null;
};

prefix('appearance');
// 'appearance' on a supported browser, otherwise 'webkitAppearance',
//   'mozAppearance', 'msAppearance' or 'oAppearance'

// Boundary case: if neither the standard property nor any prefixed variant is supported
prefix('nonExistentProperty'); // null
```

## Expected vs Actual Results
| Assertion Target | Expected Value | Actual Value | Status |
|---|---|---|---|
| `prefix('appearance')` | `'appearance'` | `'appearance'` | MATCH / PASS |
| `prefix('nonExistentProperty')` | `null` | `null` | MATCH / PASS |
| Deliberate wrong appearance check | Exception / Failure | Correctly caught and validated | PASS |
| Deliberate wrong boundary check | Exception / Failure | Correctly caught and validated | PASS |

## Site Build Verification
- Command: `python3 work/R52-T042/check.py && npm run build` (with `ASTRO_TELEMETRY_DISABLED=1`)
- Result: 909 page(s) built successfully, 0 errors.
