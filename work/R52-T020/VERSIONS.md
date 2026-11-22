# Tool versions used in R52-T020 checks

| Tool       | Version   |
|------------|-----------|
| Node.js    | v22.14.0  |
| Python3    | 3.9.6     |

## Article
`content/snippets/js/s/browser-os-detection.md`

## Check script
`work/R52-T020/check.py`

## Results
`work/R52-T020/results.json` — saved on each run; `passed: true` means all assertions pass.

## Changes summary
- Added step-by-step breakdown of the isMac logic (concrete intermediate values)
- Added boundary example: Win32 and Linux platform strings → false
- Added ambiguous case callout: iPadOS 13+ reports 'MacIntel' (same as Mac)
- Mutant tested: `.startsWith('mac')` vs correct `.includes('mac')`
  - Distinguishing input: `'something_mac'` → correct=true, mutant=false
