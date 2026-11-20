# Test Results Evidence for R52-T045

## Target Snippet
- `content/snippets/js/s/relative-time-formatting.md`

## Tool Versions
- Node.js: v26.12.1
- Python: 3.15.2
- npm: 11.2.0

## Reproducible Fixtures & Inputs
- **Formatter Construction:**
  ```js
  const formatter = new Intl.RelativeTimeFormat('en', {
    numeric: 'auto',
    style: 'long',
  });
  ```
- **Boundary Cases (Value = 0):**
  - `formatter.format(0, 'day')` -> `'today'`
  - `formatter.format(0, 'second')` -> `'now'`
- **Reproducible Date Environment:**
  - Fixed timestamp: `2025-03-31T11:00:00Z`
  - Restored process-global `Date` immediately after evaluation (`global.Date === RealDate`).

## Expected vs Actual Results
| Assertion Target | Expected Value | Actual Value | Status |
|---|---|---|---|
| `formatter.format(0, 'day')` | `'today'` | `'today'` | MATCH / PASS |
| `formatter.format(0, 'second')` | `'now'` | `'now'` | MATCH / PASS |
| `formatter.format(-1, 'day')` | `'yesterday'` | `'yesterday'` | MATCH / PASS |
| `formatter.format(0, 'year')` | `'this year'` | `'this year'` | MATCH / PASS |
| `formatter.format(2, 'week')` | `'in 2 weeks'` | `'in 2 weeks'` | MATCH / PASS |
| Global Date Restored | `true` | `true` | MATCH / PASS |
| Deliberate wrong check | Exception / Failure | Correctly caught and validated | PASS |

## Site Build Verification
- Command: `python3 work/R52-T045/check.py && npm run build` (with `ASTRO_TELEMETRY_DISABLED=1`)
- Result: 909 page(s) built successfully, 0 errors.
