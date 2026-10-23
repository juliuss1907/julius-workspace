# CJK Leak Patterns -- Session 2026-09-18

Additional Chinese character leaks observed during batch blog writing.
Merge into `references/cjk-and-build-pitfalls.md` table when next foreground
edit is possible.

## New patterns (add to leak table)

| Chinese (leaked) | Vietnamese (intended) | Context |
|---|---|---|
| 未经授权 | khong duoc phep | "tao bang tin noi bo未经授权" |
| 方向 | huong di | "Nhung方向 da ro" |
| dong co | dong co | "nhung动机 dang sau" |

## Detection helper

```python
import re
with open('path/to/file.md') as f:
    for i, line in enumerate(f, 1):
        m = re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', line)
        if m:
            print(f'Line {i}: char={m.group()} pos={m.start()} context=...{line[max(0,m.start()-10):m.start()+10]}...')
```

Run this AFTER the validation script flags CJK to find the exact character
and surrounding context before patching.
