# Oxford Comma False Positive in Vietnamese (2026-09-20)

## The pattern

Vietnamese compound sentences routinely use comma before "và" to join two clauses:
"Jev không sinh chuỗi ký tự, và đó là lý do nó nhanh hơn."

This is standard Vietnamese punctuation, NOT an Oxford comma (English serial-list pattern:
"X, Y, và Z" where the comma before "và" is optional/debated).

## Why the script flags it

The content-validation script counts lines matching `,\s*(và|and)\s` and warns when count > 2.
In Vietnamese articles with 5+ compound sentences, this threshold triggers false positives.

## Agent action

When the validation script reports `[Oxford comma?] N dòng`:
1. Read each flagged line
2. Check if it's a compound sentence (clause + comma + "và" + clause) or a serial list (A, B, và C)
3. If ALL are compound sentences → false positive, proceed with build
4. If any are serial lists → fix the Oxford comma

## Observed instances (2026-09-20)

- "Model đã vượt con người ở chat từ nhiều năm rồi, vậy tự động hóa ở đâu?" — compound, OK
- "Jev nhận trạng thái đầu vào và trả về quyết định trực tiếp" — compound, OK
- "chatbot, viết bài, mã nguồn dài, hay bất kỳ..." — serial list with "hay", OK
