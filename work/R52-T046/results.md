# Test Results Evidence for R52-T046

## Target Snippet
- `content/snippets/js/s/value-as-number.md`

## Tool Versions
- Node.js: v26.12.1
- Python: 3.15.2
- npm: 11.2.0

## Annotated Operation & Intermediate Values
Operation under comparison: extracting numeric value from `<input id="quantity-input" type="number" value="42.5" />`.
1. **`parseFloat(quantityInput.value)`:**
   - Intermediate value 1: `quantityInput.value` retrieves string `'42.5'`.
   - Intermediate value 2: `parseFloat('42.5')` parses string characters into numeric primitive `42.5`.
2. **`quantityInput.valueAsNumber`:**
   - Directly accesses the element's internal numeric value: returns `42.5` without string parsing overhead.
3. **Boundary Case:**
   - Input: `<input id="empty-input" type="number" value="" />`.
   - `emptyInput.valueAsNumber` evaluates directly to `NaN`.

## Expected vs Actual Results
| Assertion Target | Expected Value | Actual Value | Status |
|---|---|---|---|
| `quantity` (via `parseFloat`) | `42.5` | `42.5` | MATCH / PASS |
| `quantityInput.value` (intermediate string) | `'42.5'` | `'42.5'` | MATCH / PASS |
| `quantityInput.valueAsNumber` (direct numeric) | `42.5` | `42.5` | MATCH / PASS |
| `Number.isNaN(emptyInput.valueAsNumber)` | `true` | `true` | MATCH / PASS |
| Deliberate wrong expectation failure | Exception / Failure | Correctly caught and validated | PASS |

## Site Build Verification
- Command: `python3 work/R52-T046/check.py && npm run build` (with `ASTRO_TELEMETRY_DISABLED=1`)
- Result: 909 page(s) built successfully, 0 errors.
