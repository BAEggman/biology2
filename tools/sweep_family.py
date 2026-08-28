#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""형제는 걸렸는데 나만 빠진 카드 훑기.

★ 무엇을 세는가
  한 주제를 묻는 카드 무리 가운데 **걸린 형제가 전부 같은 한 판**에 있고,
  **그 판에 못 간 형제가 아무 데도 안 걸린** 자리.
  형제가 여러 판에 흩어져 있으면 세지 않는다 — 그건 제자리를 찾은 것이다.

⚠ 이것은 빚 목록이 아니다. 사용자 방침이 「모든 카드를 연결할 필요는 없어」이므로,
  여기 오른 것 중 **그 판이 이미 그 사실을 그리고 있는데 안 걸린 것**만 진짜 빚이다.
  나머지는 그림이 없어서 안 걸린 것이고 그건 「★ 그린 것만 건다」를 지킨 결과다.

⚠⚠ 2026-08-28 · 이 파일이 생긴 까닭
  처음 판에서 카드 ID 정규식을 `[A-Za-z0-9]+-[A-Za-z0-9]+` 로 썼다.
  그런데 이 덱에는 **하이픈이 둘인 ID** 가 있다 — S-SG-6 · X-BT-13 · S-PL-6 …
  그 패턴은 「S-SG」 까지만 먹고 닫는 따옴표를 못 만나 **통째로 안 잡힌다**.
  그래서 걸려 있는 카드 155장이 「안 걸림」으로 잘못 보고됐다.
  ★ 교훈: 한 번 쓰고 버리는 훑기라도 **ID 패턴은 파일에 박아 둔다**.
  그래야 같은 구멍이 조용히 돌아오지 않는다.
"""
import re, json, collections, sys, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ★ 카드 ID — 하이픈이 하나든 둘이든 잡는다
CID = r'"([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+(?:#\d+)?)"'
PID = r"\{id:'([a-z]\d+p\d+[a-z]?)'"
strip = lambda x: re.sub('<[^>]+>', '', x or '')

def load():
    s = open(os.path.join(R, 'sketchy.html'), encoding='utf-8').read()
    cards = json.loads(re.search(r'id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>',
                                 open(os.path.join(R, 'index.html'), encoding='utf-8').read()).group(1))
    ms = list(re.finditer(PID, s))
    c2p = collections.defaultdict(set)
    for k, m in enumerate(ms):
        end = ms[k + 1].start() if k + 1 < len(ms) else len(s)
        for c in re.findall(CID, s[m.start():end]):
            c2p[c].add(m.group(1))
    return cards, c2p

def subj(q):
    """물음의 맨 앞 토막 = 주제. 「비타민 B12의 …」 → 「비타민 B12」"""
    q = strip(q).strip()
    m = re.match(r'^(.{2,14}?)\s*(?:의|가|는|은|이)\s', q)
    return re.sub(r'\s+', ' ', (m.group(1) if m else q[:10])).strip()

def sweep():
    cards, c2p = load()
    grp = collections.defaultdict(list)
    for c in cards:
        if len(strip(c.get('q', ''))) >= 6:
            grp[subj(c['q'])].append(c['id'])
    hits = []
    for t, ids in grp.items():
        if not (2 <= len(ids) <= 5): continue
        on = [i for i in ids if c2p.get(i)]
        off = [i for i in ids if not c2p.get(i)]
        if not on or not off: continue
        pans = set().union(*(c2p[i] for i in on))
        if len(pans) != 1: continue          # 걸린 형제가 전부 한 판
        if len(on) < len(off): continue      # 걸린 쪽이 다수
        hits.append((sorted(pans)[0], t, on, off))
    return {c['id']: c for c in cards}, sorted(hits)

if __name__ == '__main__':
    A, hits = sweep()
    n = sum(len(o) for _, _, _, o in hits)
    if '--sum' in sys.argv:
        print(f'형제는 걸렸는데 빠진 카드 — {len(hits)}자리 · {n}장'); sys.exit(0)
    print(f'★ 「걸린 형제가 모두 한 판에 있고, 나만 아무 데도 안 걸린」 — {len(hits)}자리 · {n}장\n')
    cur = None
    for P, t, on, off in hits:
        if P != cur: print(f'\n── {P} ──'); cur = P
        print(f'  「{t}」 걸림 {on} → 빠짐 {off}')
        for i in off:
            print(f'      {i} | {strip(A[i].get("q"))[:66]} → {strip(A[i].get("a"))[:66]}')
