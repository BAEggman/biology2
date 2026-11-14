#!/usr/bin/env python3
# card_edit_note.py <id> "<까닭>" [<id> "<까닭>" …] — 카드 글을 일부러 고쳤다고 test/baseline.json 의 cardEdits 에 적는다.
#   (test/verify_*.js 는 「기존 카드가 변형되지 않는다」를 지킨다 — 여기에 id 와 까닭이 있는 카드만 변형을 허용한다. 자식 카드(#n)도 바뀌면 그 id 도 적는다.)
import sys, json, os, datetime
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'test', 'baseline.json')
L = open(P, encoding='utf-8').read().split('\n')
i = next(k for k, ln in enumerate(L) if ln.startswith(' "cardEdits": '))
d = json.loads(L[i].strip()[len('"cardEdits": '):].rstrip(','))
assert ' "cardEdits": ' + json.dumps(d, ensure_ascii=False) + ',' == L[i], '줄 꼴이 예상과 다르다 — 손으로 확인'
args = sys.argv[1:]; assert args and len(args) % 2 == 0, '쓰기: card_edit_note.py <id> "<까닭>" …'
today = datetime.date.today().isoformat()
for cid, why in zip(args[0::2], args[1::2]):
    d[cid] = (d[cid] + ' / ' if cid in d else '') + f'{today} {why}'
L[i] = ' "cardEdits": ' + json.dumps(d, ensure_ascii=False) + ','
open(P, 'w', encoding='utf-8').write('\n'.join(L))
print('cardEdits', len(d), '·', ' '.join(args[0::2]))
