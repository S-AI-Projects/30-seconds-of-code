# R52-T045 — Test Results

## Example tested

The checker extracts the JavaScript code directly from the
`Constructing a formatter` section of
`content/snippets/js/s/relative-time-formatting.md` and executes it with Node.js.

**Inputs**
- Locale: `en`
- Options: `{ numeric: 'auto', style: 'long' }`
- Main example: `formatter.format(-1, 'day')`
- Boundary example: `formatter.format(0, 'day')`

| Input | Expected output | Actual output |
|---|---|---|
| `format(-1, 'day')` | `yesterday` | `yesterday` |
| `format(0, 'day')` | `today` | `today` |

## Checker verification

Command:

```bash
python3 work/R52-T045/check.py