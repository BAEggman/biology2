# -*- coding: utf-8 -*-
"""
v17 병합본(aaca7c0 계열)에 라이브 9e17a8b의 s34 추가분을 얹는다.

  python3 tools/merge_v17/apply.py            # 실제로 쓴다
  python3 tools/merge_v17/apply.py --check    # 검사만, 파일은 안 쓴다

무엇을 얹는가
  - 패널 s34p03 「화분관 길」 · s34p04 「종자 창고」
  - s34 장면의 함정 8건 · 숫자 4건 (이미 있는 문자열은 건너뛴다)

무엇을 안 건드리는가
  - 다른 장면·패널·사실표·bx는 한 글자도 안 바꾼다
  - traps/nums는 기존 항목을 그대로 두고 없는 것만 뒤에 붙인다

이미지는 저장소에서 받는다:
  git checkout origin/main -- img/s34p02.webp img/s34p03.webp img/s34p04.webp
  (s34p02는 반드시 새 것으로. 옛 s34p02는 바구니에 붉은 옷이 있어
   s34p03의 「붉은 옷 = 정자」와 충돌한다 — 적대적 검수 단독 실격 항목)

얹은 뒤: node build.js && npm test  → baseline.json을 실측값으로 올린다.
"""
import io, os, sys, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT  = os.path.join(ROOT, 'tools', 'merge_v17')
SK   = os.path.join(ROOT, 'sketchy.html')
CHECK = '--check' in sys.argv


def read(p):
    return io.open(p, encoding='utf-8').read()


def close_bracket(s, i):
    """s[i]가 '[' 또는 '{'일 때 짝이 되는 닫는 괄호의 인덱스를 준다.
    문자열 리터럴 안의 괄호는 무시한다."""
    open_c = s[i]
    close_c = ']' if open_c == '[' else '}'
    d = 0
    q = None          # 현재 열려 있는 따옴표
    j = i
    while j < len(s):
        c = s[j]
        if q:
            if c == '\\':
                j += 2
                continue
            if c == q:
                q = None
        elif c in "'\"`":
            q = c
        elif c == open_c:
            d += 1
        elif c == close_c:
            d -= 1
            if d == 0:
                return j
        j += 1
    raise AssertionError('짝이 되는 %s를 못 찾았다' % close_c)


def literals(arr_src):
    """['a','b',...] 형태 배열 소스에서 최상위 문자열 리터럴을 원문 그대로 뽑는다."""
    out, j = [], 1
    while j < len(arr_src) - 1:
        c = arr_src[j]
        if c in "'\"`":
            k = j + 1
            while k < len(arr_src):
                if arr_src[k] == '\\':
                    k += 2
                    continue
                if arr_src[k] == c:
                    break
                k += 1
            out.append(arr_src[j:k + 1])
            j = k + 1
        else:
            j += 1
    return out


s = read(SK)
orig_len = len(s)
log = []

# ── 1. 장면 s34 찾기 ────────────────────────────────────────────────
i_scene = s.find("{id:'s34'")
assert i_scene != -1, "장면 s34를 못 찾았다"
end_scene = close_bracket(s, i_scene)
scene = s[i_scene:end_scene + 1]

# ── 2. 패널 두 장 ──────────────────────────────────────────────────
i_panels = s.index('panels:[', i_scene)
i_open = s.index('[', i_panels)
i_close = close_bracket(s, i_open)

add = []
for pid in ('s34p03', 's34p04'):
    if ("{id:'%s'" % pid) in s:
        log.append('· %s 이미 있다 — 건너뜀' % pid)
    else:
        add.append(read(os.path.join(KIT, '%s.panel.txt' % pid)).strip())
        log.append('+ %s 주입' % pid)

if add:
    s = s[:i_close] + ',\n ' + ',\n '.join(add) + s[i_close:]

# ── 3. traps · nums ────────────────────────────────────────────────
for field, kitfile in (('traps', 's34.traps.txt'), ('nums', 's34.nums.txt')):
    i_scene = s.find("{id:'s34'")                 # 위에서 길이가 바뀌었으므로 다시
    end_scene = close_bracket(s, i_scene)
    i_f = s.find(field + ':[', i_scene)
    assert i_f != -1 and i_f < end_scene, '%s 배열을 못 찾았다' % field
    i_open = s.index('[', i_f)
    i_close = close_bracket(s, i_open)
    have = literals(s[i_open:i_close + 1])
    want = literals(read(os.path.join(KIT, kitfile)))
    have_set = set(x[1:-1] for x in have)
    new = [x for x in want if x[1:-1] not in have_set]
    if new:
        s = s[:i_close] + ',\n  ' + ',\n  '.join(new) + s[i_close:]
    log.append('%s: 기존 %d · 추가 %d' % (field, len(have), len(new)))

# ── 4. 쓰기 전에 반드시 다시 파싱해 본다 ──────────────────────────
tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8')
tmp.write(s)
tmp.close()
js = (
    "const L=require('%s');const fs=require('fs');"
    "const D=L.parseDATA(fs.readFileSync(process.argv[1],'utf8'));"
    "const s=D.find(x=>x.id==='s34');"
    "process.stdout.write(JSON.stringify({scenes:D.length,"
    "panels:D.reduce((a,x)=>a+x.panels.length,0),"
    "s34:s.panels.map(p=>p.id),traps:s.traps.length,nums:s.nums.length}));"
) % os.path.join(ROOT, 'test', '_lib').replace('\\', '/')
r = subprocess.run(['node', '-e', js, tmp.name], cwd=ROOT, capture_output=True, text=True)
os.unlink(tmp.name)
if r.returncode != 0:
    print('\n'.join(log))
    print('\n❌ 재파싱 실패 — 원본은 건드리지 않았다.\n' + (r.stderr or '')[-1500:])
    sys.exit(1)

print('\n'.join(log))
print('재파싱 OK →', r.stdout)
print('길이 %d → %d (+%d)' % (orig_len, len(s), len(s) - orig_len))

if CHECK:
    print('\n--check 이므로 파일은 쓰지 않았다.')
    sys.exit(0)

io.open(SK, 'w', encoding='utf-8').write(s)
print('\n✅ sketchy.html 갱신. 이제:')
print('   git checkout origin/main -- img/s34p02.webp img/s34p03.webp img/s34p04.webp')
print('   node build.js && npm test')
print('   그 뒤 test/baseline.json을 실측값으로 올린다.')
