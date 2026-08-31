#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""혼동쌍 훑기 — 「발문이 이름을 준다」 규칙의 뒷면을 본다.

★ 왜 만들었나 (2026-08-31, 사용자 지적)
  s14p03 의 억제제 넷 — 택솔·팔로이딘·콜히친·사이토칼라신 — 은
  **어느 감사에도 안 잡혔다.** 네 이름이 전부 카드의 **발문(q)** 에만 있고
  **답(a)** 에는 없었기 때문이다.

      audit_answers.js  → ④「발문이 그 이름을 준다」로 면제
      sweep_loanblind.py → 답만 본다 (`if t in q: continue`)

  그런데 기출은 이 넷을 **서로 바꿔서** 낸다 —
  「사이토칼라신이 미세소관을 탈중합 억제한다」 같은 꼴이다.
  그런 문항에서 학생은 **이름을 단서로 받아 자리(대상 × 방향)를 인출**한다.

  ★ 즉 인출 방향이 반대다.
      답에 있는 이름  : 그림 → 이름   (기존 감사가 보는 방향)
      발문에 있는 이름: 이름 → 그림   (이 훑기가 보는 방향)

  「발문이 이름을 주면 인출 대상이 아니다」는 **맞다**. 그러나 발문이 이름을
  주는 순간 그 이름은 **열쇠**가 된다. 열쇠가 여럿이고 서로 바꿔치기당하는
  자리에서는 이름이 그림에 붙어 있어야 학생이 자리로 갈 수 있다.

★ 무엇을 자리로 보는가
  한 판에 걸린 카드들의 **발문**에 음차/임의 이름이 **둘 이상** 나오고,
  그중 **하나라도** 그 판의 소품이 안 나르는 자리.
  둘 이상을 요구하는 것은 **혼동은 짝이 있어야 생기기** 때문이다.

⚠ 이것은 래칫이 아니다. 어림짐작이라 잡음이 섞인다 — **한 줄씩 손으로 판정**한다.
"""
import os, sys, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep_loanblind import load, build, isLoan, strip, KOR, JOSA


def sweep(th=1.2, need=2):
    s, A, H = load()
    exempt, score, EV, C2P, hooks = build(s, H)

    def carries(e, w):
        if w in e:
            return True
        hk = hooks.get(w)
        return bool(hk and any(p in e for p in hk.get('props', [])))

    per = collections.defaultdict(lambda: {'miss': {}, 'ok': set()})
    for cid, c in A.items():
        if cid not in C2P:
            continue
        q = strip(c.get('q', ''))
        for t in KOR.findall(q):
            t = JOSA.sub('', t)
            if len(t) < 3 or t in exempt:
                continue
            if score(t) < th:
                continue
            for p in C2P[cid]:
                if carries(EV.get(p, ''), t):
                    per[p]['ok'].add(t)
                else:
                    per[p]['miss'].setdefault(t, set()).add(cid)

    out = []
    for p, v in per.items():
        names = len(v['miss']) + len(v['ok'])
        if names >= need and v['miss']:
            out.append((p, v['miss'], sorted(v['ok'])))
    out.sort(key=lambda x: -len(x[1]))
    return out, score


if __name__ == '__main__':
    th = float(os.environ.get('TH', '1.2'))
    need = int(os.environ.get('NEED', '2'))
    out, score = sweep(th, need)
    cards = {c for _, m, _ in out for s_ in m.values() for c in s_}
    if '--sum' in sys.argv:
        print(f'혼동쌍 자리 {len(out)}개 · 카드 {len(cards)}장 (문턱 {th} · 이름 {need}개 이상)')
        sys.exit(0)
    print(f'★ 발문에만 있는 이름이 짝을 이루는 자리 {len(out)}개 · 카드 {len(cards)}장 '
          f'(문턱 {th} · 한 판에 이름 {need}개 이상)\n')
    for p, miss, ok in out:
        ms = ' · '.join(f'{w}({score(w):+.1f})' for w in sorted(miss, key=lambda w: -score(w)))
        print(f'  {p:9s} 안 나름 {len(miss)}개: {ms}')
        if ok:
            print(f'  {"":9s} 나름   : {" · ".join(ok)}')
