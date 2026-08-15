#!/usr/bin/env python3
"""d05 도해의 SVG를 생성기 최신본으로 갈아 끼운다.

왜 필요한가 — 감사에서 잡힌 것을 고치려면 SVG를 다시 뽑아야 하는데,
패널은 이미 sketchy.html 안에 들어가 있다. DATA를 통째로 다시 쓰지 않고
`svg:` 백틱 블록만 정확히 잘라 바꿔 넣는다(규칙: DATA를 재직렬화하지 않는다).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')
PANELS = ['d05p01', 'd05p02', 'd05p03']


def backtick_block(t, i):
    """i는 여는 백틱 위치. 닫는 백틱 위치를 돌려준다(이스케이프 고려)."""
    j = i + 1
    while j < len(t):
        if t[j] == '\\':
            j += 2
            continue
        if t[j] == '`':
            return j
        j += 1
    raise SystemExit('백틱 안 닫힘')


def main():
    src = open(SK, encoding='utf-8').read()
    changed = 0
    for pid in PANELS:
        path = os.path.join(ROOT, 'tools', '_%s.svg' % pid)
        svg = open(path, encoding='utf-8').read().strip()
        assert '`' not in svg and '\\' not in svg, pid + ': SVG에 백틱·역슬래시'
        assert svg.startswith('<svg') and svg.endswith('</svg>'), pid

        k = src.index("{id:'%s'" % pid)
        s0 = src.index('svg:`', k) + 4          # 여는 백틱 위치
        s1 = backtick_block(src, s0)
        old = src[s0 + 1:s1]
        if old == svg:
            print('%s 그대로 (%d바이트)' % (pid, len(svg)))
            continue
        src = src[:s0 + 1] + svg + src[s1:]
        print('%s 갱신 %d → %d바이트' % (pid, len(old), len(svg)))
        changed += 1

    if not changed:
        print('바뀐 것 없음')
        return 0

    # 재파싱해서 깨지지 않았는지 확인한다 — 통과가 아니라 결과로 본다
    open(SK, 'w', encoding='utf-8').write(src)
    ids = re.findall(r"\{id:'([sd]\d+p\d+[ab]?)'", src)
    assert len(ids) == len(set(ids)), '패널 id 중복'
    for pid in PANELS:
        k = src.index("{id:'%s'" % pid)
        s0 = src.index('svg:`', k) + 4
        s1 = backtick_block(src, s0)
        got = src[s0 + 1:s1]
        want = open(os.path.join(ROOT, 'tools', '_%s.svg' % pid), encoding='utf-8').read().strip()
        assert got == want, pid + ': 넣은 것과 디스크가 다르다'
    print('✅ %d장 갱신 · 재확인 통과' % changed)
    return 0


if __name__ == '__main__':
    sys.exit(main())
