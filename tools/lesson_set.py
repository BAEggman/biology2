#!/usr/bin/env python3
# lesson_set.py — 과(lessons/<ID>.json) 정거장의 「글이 아닌 칸」을 고친다: cards(곧장 건 카드) · drop(옛 행에 딸려 왔지만 이 정거장 것이 아닌 카드) · ask(시험 물음) · box(상자) · 새 정거장 끼우기.
#   글 칸(obj · fact · hook · say · title · sub)은 tools/audit/apply_patch.py 가 맡는다.
# 사용: python3 tools/lesson_set.py <patch.json> [--check]
# patch.json:
#   {"set":[ {"lesson":"L17b","sid":"s5","cards_add":["H0-109","H0-110"]},
#            {"lesson":"L19e","sid":"s8","drop_add":["X-SG-23"]},
#            {"lesson":"L17a","sid":"s5","ask":"이 배의 짐은 걸러진 뒤 더 실리나?"},      # ask 를 "" 로 주면 지운다
#            {"lesson":"L19b","sid":"s4","box":[x,y,w,h]} 또는 "box":[[x,y,w,h],[…]] 또는 "box":null,
#            {"lesson":"L17a","new_after":"s5","stop":{"obj":"…","fact":"…","hook":"…","say":"…","box":[…],"cards":[…]}} ]}   # sid 는 자동(최댓값+1 · 재사용 없음)
# 파일 모양(들여쓰기 1 또는 2 · 끝 줄바꿈)은 그대로 지킨다 — 모양을 못 알아보면 멈춘다.
import json, sys, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(lid):
    p = os.path.join(ROOT, 'lessons', lid + '.json')
    txt = open(p, encoding='utf-8').read()
    d = json.loads(txt)
    for ind in (2, 1):
        for nl in ('', '\n'):
            if json.dumps(d, ensure_ascii=False, indent=ind) + nl == txt:
                return p, d, (ind, nl)
    raise SystemExit(f'✕ {lid}: 파일 모양을 못 알아봄(들여쓰기 1 · 2 가 아님)')

def cards_all():
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r'<script[^>]*id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>', s)
    return {c['id'] for c in json.loads(m.group(1))}

def okbox(b, W, H):
    bs = b if isinstance(b[0], list) else [b]
    for x, y, w, h in bs:
        if not (0 <= x and 0 <= y and w > 0 and h > 0 and x + w <= W and y + h <= H): return False
    return True

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; check = '--check' in sys.argv
    patch = json.load(open(args[0], encoding='utf-8'))
    CARDS = cards_all(); files = {}; bad = 0; n = 0
    for op in patch.get('set', []):
        lid = op['lesson']
        if lid not in files: files[lid] = load(lid)
        p, d, style = files[lid]; stops = d['stops']
        if 'new_after' in op:
            at = next((k for k, s in enumerate(stops) if s['sid'] == op['new_after']), None)
            if at is None: print(f"✕ {lid}: sid {op['new_after']} 없음"); bad += 1; continue
            st = op['stop']; mx = max(int(s['sid'][1:]) for s in stops)
            new = {'sid': f's{mx + 1}'}
            for k in ('obj', 'fact', 'hook', 'say', 'box', 'src', 'cards', 'ask'):
                if k in st and st[k] not in (None, ''): new[k] = st[k]
            if len(new.get('fact', '')) > 60 or not new.get('say') or not new.get('obj'):
                print(f"✕ {lid}: 새 정거장 글 검사(사실 60자 · say · obj)"); bad += 1; continue
            if 'box' in new and not okbox(new['box'], d['w'], d['h']): print(f"✕ {lid}: 새 정거장 상자가 그림 밖"); bad += 1; continue
            for c in new.get('cards', []):
                if c not in CARDS: print(f"✕ {lid}: 없는 카드 {c}"); bad += 1
            stops.insert(at + 1, new); n += 1; print(f"  + {lid} {new['sid']} (… {op['new_after']} 뒤)"); continue
        s = next((s for s in stops if s['sid'] == op['sid']), None)
        if s is None: print(f"✕ {lid}: sid {op['sid']} 없음"); bad += 1; continue
        for key, fld in (('cards_add', 'cards'), ('drop_add', 'drop')):
            for c in op.get(key, []):
                if c not in CARDS: print(f"✕ {lid} {op['sid']}: 없는 카드 {c}"); bad += 1; continue
                cur = s.get(fld, [])
                if c not in cur: s[fld] = cur + [c]; n += 1
        if 'ask' in op:
            if op['ask']: s['ask'] = op['ask']
            else: s.pop('ask', None)
            n += 1
        if 'box' in op:
            if op['box'] is None: s.pop('box', None)
            elif not okbox(op['box'], d['w'], d['h']): print(f"✕ {lid} {op['sid']}: 상자가 그림 밖 {op['box']}"); bad += 1; continue
            else: s['box'] = op['box']
            n += 1
    if bad: raise SystemExit(f'✕ {bad} 곳 — 쓰지 않음')
    print(f'과 {len(files)} · 고침 {n}' + (' · 검사만 — 쓰지 않음' if check else ''))
    if check: return
    for lid, (p, d, (ind, nl)) in files.items():
        open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=ind) + nl)

if __name__ == '__main__': main()
