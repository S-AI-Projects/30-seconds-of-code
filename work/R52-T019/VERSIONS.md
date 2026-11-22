# Tool versions used in R52-T019 checks

| Tool       | Version   |
|------------|-----------|
| Node.js    | v22.14.0  |
| Python3    | 3.9.6     |

## Article
`content/snippets/js/s/indexed-object-collections.md`

## Check script
`work/R52-T019/check.py`

## Results
`work/R52-T019/results.json` — saved on each run; `passed: true` means all assertions pass.

## Changes summary
- Fixed `forEach((obj) => ...)` → `forEach((object) => ...)` so the parameter name
  matches all internal references (`object.id`, `this.objects.push(object)`, etc.)
- Added boundary example: `collection.get(999)` → `undefined`
- Added time/space trade-off explanation (O(1) Map vs O(n) Array.find)
