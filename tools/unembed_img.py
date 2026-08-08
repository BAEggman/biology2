#!/usr/bin/env python3
"""sketchy.html 에서 base64 그림을 걷어내고 img/*.webp 경로를 쓰게 바꾼다.

왜
  같은 그림 105장이 두 벌 있었다 — img/ 11.85MB + sketchy.html 안의 base64 15.8MB = 27MB.
  그래서 배포마다 16MB 블롭이 .git 에 쌓였고, 훑어보기 화면은 16.3MB 를 한 번에 받아야 했고,
  두 벌이 조용히 갈라지는 사고(2026-08-08 18장 낡음 · 7장 빈칸)도 거기서 나왔다.
  경로를 쓰면 이 셋이 한꺼번에 사라진다. sketchy.html 16.3MB → 약 0.55MB.

  ⚠ 대신 sketchy.html 파일 하나만 따로 받아서는 그림이 안 보인다.
    사용자 확인함(2026-08-08): 「항상 웹사이트로만 본다」.
    오프라인 단독본이 필요해지면 tools/bundle_img.py 로 base64 판을 다시 만든다.

무엇을 하나
  1) `const IMG = {…}` 객체를 통째로 지운다
  2) 렌더러의 `src="${IMG[p.id]||''}"` 를 `src="img/${p.id}.webp"` 로 바꾼다
     — 그림이 없는 도해 패널(d0*)은 지금도 빈 src 였으므로, PNOIMG 대신
       `p.noimg` 판정 대신 파일 유무를 그대로 반영한다(없으면 404 → alt 만 보인다).
       도해 패널은 원래 IMG 에도 없어서 빈 칸이었으니 동작이 같다.
  DATA 는 건드리지 않는다.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

ANCHOR = 'const IMG = '
OLD_SRC = '<div class="shot"><img src="${IMG[p.id]||\'\'}" alt="${sc.t} ${p.t}" loading="lazy"></div>'
NEW_SRC = '<div class="shot"><img src="img/${p.id}.webp" alt="${sc.t} ${p.t}" loading="lazy" onerror="this.closest(\'.shot\').style.display=\'none\'"></div>'


def close_brace(t, i):
    op = t[i]
    cl = {'{': '}', '[': ']'}[op]
    d, q, j = 0, None, i
    while j < len(t):
        c = t[j]
        if q:
            if c == '\\':
                j += 2
                continue
            if c == q:
                q = None
        elif c in '"\'`':
            q = c
        elif c == op:
            d += 1
        elif c == cl:
            d -= 1
            if d == 0:
                return j
        j += 1
    raise SystemExit('괄호 안 닫힘')


def main():
    src = open(SK, encoding='utf-8').read()
    before = len(src)

    n = src.count(ANCHOR)
    if n != 1:
        print('✗ IMG 앵커 %d회 — 이미 걷어냈나?' % n)
        return 1
    i = src.index(ANCHOR)
    j = close_brace(src, i + len(ANCHOR))
    # 선언문 전체(`const IMG = {…};` 와 뒤따르는 줄바꿈)를 지운다
    k = j + 1
    while k < len(src) and src[k] in ';\n':
        k += 1
    removed = k - i

    assert src.count(OLD_SRC) == 1, 'src 앵커 %d회' % src.count(OLD_SRC)

    out = src[:i] + src[k:]
    out = out.replace(OLD_SRC, NEW_SRC)

    assert 'const IMG' not in out, 'IMG 잔존'
    assert 'IMG[' not in out, 'IMG 참조 잔존'
    assert 'data:image/webp;base64' not in out, 'base64 잔존'
    assert out.count('img/${p.id}.webp') == 1

    # DATA 배열이 그대로인지 확인
    # (렌더러는 DATA 뒤에 있으므로 「DATA 이후 전부」로 비교하면 안 된다 — src 교체분이 걸린다)
    def data_arr(t):
        s = t.index('[', t.index('const DATA'))
        return t[s:close_brace(t, s) + 1]
    assert data_arr(src) == data_arr(out), 'DATA 가 바뀌었다'

    open(SK, 'w', encoding='utf-8').write(out)
    print('IMG 객체 %.2fMB 제거 · sketchy.html %.2fMB → %.2fMB'
          % (removed / 1048576, before / 1048576, len(out) / 1048576))
    return 0


if __name__ == '__main__':
    sys.exit(main())
