#!/usr/bin/env python3
"""sketchy.html 의 IMG 맵을 img/*.webp 로부터 통째로 다시 만든다.

왜 필요한가
  sketchy.html 은 그림을 base64 로 품고 있고(자기완결 파일), index.html 은 img/*.webp 를 쓴다.
  그림을 고칠 때 img/ 만 갈아 끼우면 두 화면이 갈라진다 — 2026-08-08 에 17장이 갈라져 있었고
  s04p06·s34p01~06 일곱 장은 sketchy.html 에서 아예 안 보였다(IMG 키가 없어 src="" 였다).
  이 스크립트가 유일한 원본을 img/ 로 못 박는다.

안전 규칙
  · DATA 는 절대 재직렬화하지 않는다. `const IMG = {…}` 객체만 문자열로 잘라 갈아 끼운다.
  · 도해(PNOIMG, d0*) 는 파일이 없으므로 건너뛴다.
  · 앵커는 정확히 1개여야 한다.

용법  python3 tools/sync_img.py [--check]
      --check : 고치지 않고 어긋난 것만 보고한다(테스트용, 어긋나면 exit 1)
"""
import base64, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK   = os.path.join(ROOT, 'sketchy.html')
IMGD = os.path.join(ROOT, 'img')
CHECK = '--check' in sys.argv


def close_brace(t, i):
    """t[i] 가 여는 괄호일 때 짝이 되는 닫는 괄호의 인덱스."""
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
    raise SystemExit('괄호가 안 닫힌다')


def main():
    src = open(SK, encoding='utf-8').read()

    anchor = 'const IMG = '
    assert src.count(anchor) == 1, '앵커가 %d개' % src.count(anchor)
    i = src.index(anchor) + len(anchor)
    assert src[i] == '{', 'IMG 가 객체가 아니다'
    j = close_brace(src, i)
    old = json.loads(src[i:j + 1])

    # 패널 목록은 DATA 에서 뽑는다 — img/ 에 있어도 DATA 에 없으면 넣지 않는다.
    ids = re.findall(r"\{id:'([sd]\d+p\d+[ab]?)'", src)
    assert len(ids) == len(set(ids)), '패널 id 중복'

    new, added, changed, skipped = {}, [], [], []
    for pid in ids:
        p = os.path.join(IMGD, pid + '.webp')
        if not os.path.exists(p):
            skipped.append(pid)          # 도해(d0*) 등 그림 없는 패널
            continue
        b = open(p, 'rb').read()
        assert b[:4] == b'RIFF' and b[8:12] == b'WEBP', pid + ' 가 webp 가 아니다'
        uri = 'data:image/webp;base64,' + base64.b64encode(b).decode()
        new[pid] = uri
        if pid not in old:
            added.append(pid)
        elif old[pid] != uri:
            changed.append(pid)

    dropped = [k for k in old if k not in new]

    print('패널 %d · 그림 %d · 그림없음 %d' % (len(ids), len(new), len(skipped)))
    if added:   print('  신규  %2d : %s' % (len(added), ' '.join(added)))
    if changed: print('  갱신  %2d : %s' % (len(changed), ' '.join(changed)))
    if dropped: print('  제거  %2d : %s' % (len(dropped), ' '.join(dropped)))
    if skipped: print('  건너뜀%2d : %s' % (len(skipped), ' '.join(skipped)))

    if not (added or changed or dropped):
        print('이미 일치한다.')
        return 0
    if CHECK:
        print('✗ sketchy.html 의 IMG 가 img/ 와 다르다 — python3 tools/sync_img.py 로 맞춰라')
        return 1

    body = json.dumps(new, ensure_ascii=False, separators=(',', ':'))
    assert '`' not in body and '</' not in body, '문자열 안전성 위반'
    out = src[:i] + body + src[j + 1:]

    # 갈아 끼운 뒤 다시 읽어 확인한다.
    k = out.index(anchor) + len(anchor)
    chk = json.loads(out[k:close_brace(out, k) + 1])
    assert chk == new, '재파싱 불일치'
    assert out[:i] == src[:i] and out[len(out) - (len(src) - j - 1):] == src[j + 1:], '바깥이 바뀌었다'

    open(SK, 'w', encoding='utf-8').write(out)
    print('sketchy.html %.2fMB → %.2fMB' % (len(src) / 1048576, len(out) / 1048576))
    return 0


if __name__ == '__main__':
    sys.exit(main())
