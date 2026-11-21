# Test Results Evidence for R52-T047

## Target Snippet
- `content/snippets/js/s/construct-url.md`

## Tool Versions
- Node.js: v26.12.1
- Python: 3.15.2
- npm: 11.2.0

## Derivation of the Fixture Result
Connecting each intermediate state to the relevant language operation:
1. **Variable Initializations:**
   - `const query = "Where's Waldø?";` -> string containing whitespace and non-ASCII character `ø`.
   - `const locale = "en-US";` -> standard locale identifier.
   - `const campaign = "promo_email";` -> identifier string.
2. **Template Literal Interpolation:**
   - Operation: Backtick template literal expression evaluation `https://examp.le?q=${query}&lang=${locale}&from=${campaign}`.
   - Step 1: Evaluates expression `${query}` to `"Where's Waldø?"` without performing URL percent-encoding.
   - Step 2: Evaluates expression `${locale}` to `"en-US"`.
   - Step 3: Evaluates expression `${campaign}` to `"promo_email"`.
   - Step 4: Concatenates literal string chunks with evaluated expressions into `"https://examp.le?q=Where's Waldø?&lang=en-US&from=promo_email"`.
3. **Boundary Condition (Empty Query):**
   - Operation: Interpolation with empty string `emptyQuery = ""` -> evaluates to `"https://examp.le?q="`.

## Expected vs Actual Results
| Assertion Target | Expected Value | Actual Value | Status |
|---|---|---|---|
| `query` | `"Where's Waldø?"` | `"Where's Waldø?"` | MATCH / PASS |
| `locale` | `'en-US'` | `'en-US'` | MATCH / PASS |
| `campaign` | `'promo_email'` | `'promo_email'` | MATCH / PASS |
| `url` | `"https://examp.le?q=Where's Waldø?&lang=en-US&from=promo_email"` | `"https://examp.le?q=Where's Waldø?&lang=en-US&from=promo_email"` | MATCH / PASS |
| `emptyUrl` (boundary case) | `"https://examp.le?q="` | `"https://examp.le?q="` | MATCH / PASS |
| Deliberate wrong expectation failure | Exception / Failure | Correctly caught and validated | PASS |

## Site Build Verification
- Command: `python3 work/R52-T047/check.py && npm run build` (with `ASTRO_TELEMETRY_DISABLED=1`)
- Result: 909 page(s) built successfully, 0 errors.
