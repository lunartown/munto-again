import json
KEEP={0,2,5,12,14,15,16,17,18,19,20,21,22,24,29,32,34,36,39,41,43,44,50,56,
70,72,73,75,79,80,88,91,94,101,103,129,138,141,157,158,165,174,202,213,252,
297,314,319,320,322,327,333}
rows=[json.loads(l) for l in open('data/records.jsonl',encoding='utf-8')]
kept, rejected, seen_body = [], [], set()
for i,r in enumerate(rows):
    if i in KEEP:
        key=' '.join(r['body'].split())[:120]
        if key in seen_body:      # 혹시 남은 완전중복 본문 제거
            rejected.append(r); continue
        seen_body.add(key); kept.append(r)
    else:
        rejected.append(r)
with open('data/records.clean.jsonl','w',encoding='utf-8') as f:
    for r in kept: f.write(json.dumps(r,ensure_ascii=False)+'\n')
with open('data/records.rejected.jsonl','w',encoding='utf-8') as f:
    for r in rejected: f.write(json.dumps(r,ensure_ascii=False)+'\n')
from collections import Counter
print(f'원본 {len(rows)} → 정제 {len(kept)} / 버림 {len(rejected)}')
print('정제본 사이트별:', dict(Counter(r['site'] for r in kept)))
print('정제본 댓글 있는 글:', sum(1 for r in kept if r['comments']))
print('\n--- 정제본 제목 목록 ---')
for r in kept: print(f"  [{r['site']} s{r['score']}] {r['title'][:48]}")
