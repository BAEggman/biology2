# -*- coding: utf-8 -*-
"""
갈라진 갈래(v17 병합본 aaca7c0 계열)에 라이브(origin/main)의 s34 추가분을 얹는다.

  git fetch origin
  python3 tools/merge_v17/apply.py --check    # 검사만, 파일은 안 쓴다
  python3 tools/merge_v17/apply.py            # 주입

■ 하드코딩이 없다
  얹을 것을 이 파일에 적어 두지 않는다. **origin/main의 sketchy.html을 직접 읽어**
  거기 있는데 여기 없는 s34 패널·함정·숫자를 찾아 붙인다.
  그래서 라이브에 패널이 더 쌓여도 이 스크립트는 고칠 필요가 없다.

■ 무엇을 얹는가
  - 장면 s34의 패널 중 **여기 없는 id**를 origin/main에서 원문 그대로 가져와 넣는다
  - 장면 s34의 traps·nums 중 **여기 없는 문자열**만 뒤에 붙인다

■ 무엇을 안 건드리는가
  - 다른 장면, 다른 패널, 사실표, bx는 한 글자도 안 바꾼다
  - 이미 있는 항목은 절대 덮어쓰지 않는다 (v17 쪽 수정이 우선)
  - 멱등이다. 두 번 돌려도 같은 결과다

■ 쓰기 전에
  반드시 node로 다시 파싱해 보고, 실패하면 원본을 안 건드리고 중단한다.

■ 얹은 뒤
  스크립트가 찍어 주는 대로 이미지 checkout → node build.js && npm test
  → test/baseline.json을 build.js가 찍은 실측값으로 올린다 (래칫이므로 큰 값을 쓴다).
"""
import io, os, sys, subprocess, tempfile

ROOT   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SK     = os.path.join(ROOT, 'sketchy.html')
SCENE  = "s34"
REF    = os.environ.get('MERGE_REF', 'origin/main')
CHECK  = '--check' in sys.argv


def sh(*args):
    r = subprocess.run(args, cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise SystemExit('❌ 실패: %s\n%s' % (' '.join(args), r.stderr.decode('utf-8', 'replace')[-800:]))
    return r.stdout.decode('utf-8')


def close_bracket(s, i):
    """s[i]가 '[' 또는 '{'일 때 짝이 되는 닫는 괄호 인덱스. 문자열 리터럴 안은 무시한다."""
    op = s[i]
    cl = ']' if op == '[' else '}'
    d, q, j = 0, None, i
    while j < len(s):
        c = s[j]
        if q:
            if c == '\\':
                j += 2; continue
            if c == q:
                q = None
        elif c in "'\"`":
            q = c
        elif c == op:
            d += 1
        elif c == cl:
            d -= 1
            if d == 0:
                return j
        j += 1
    raise AssertionError('짝이 되는 %s를 못 찾았다' % cl)


def scene_span(s):
    i = s.find("{id:'%s'" % SCENE)
    assert i != -1, "장면 %s를 못 찾았다" % SCENE
    return i, close_bracket(s, i)


def panels_of(s):
    """[(id, 원문), ...] 과 panels 배열의 닫는 ']' 위치"""
    i0, i1 = scene_span(s)
    p = s.index('panels:[', i0)
    o = s.index('[', p)
    c = close_bracket(s, o)
    out, j = [], o + 1
    while j < c:
        if s[j] == '{':
            e = close_bracket(s, j)
            src = s[j:e + 1]
            k = src.index("id:'") + 4
            out.append((src[k:src.index("'", k)], src))
            j = e + 1
        else:
            j += 1
    return out, c


def array_span(s, field):
    i0, i1 = scene_span(s)
    f = s.find(field + ':[', i0)
    assert f != -1 and f < i1, '%s 배열을 못 찾았다' % field
    o = s.index('[', f)
    return o, close_bracket(s, o)


def literals(src):
    """['a','b',...] 소스에서 최상위 문자열 리터럴을 원문 그대로"""
    out, j = [], 1
    while j < len(src) - 1:
        c = src[j]
        if c in "'\"`":
            k = j + 1
            while k < len(src):
                if src[k] == '\\':
                    k += 2; continue
                if src[k] == c:
                    break
                k += 1
            out.append(src[j:k + 1]); j = k + 1
        else:
            j += 1
    return out


# ── 참조본(라이브) 가져오기 ──────────────────────────────────────────
print('참조: %s' % REF)
ref = sh('git', 'show', '%s:sketchy.html' % REF)
s   = io.open(SK, encoding='utf-8').read()
orig_len = len(s)
log = []

# ── 1. 패널 ────────────────────────────────────────────────────────
ref_panels, _ = panels_of(ref)
mine, close_at = panels_of(s)
have = set(pid for pid, _ in mine)
add  = [(pid, src) for pid, src in ref_panels if pid not in have]

log.append('%s 패널 — 여기 %d장 / 라이브 %d장' % (SCENE, len(mine), len(ref_panels)))
for pid, _ in ref_panels:
    log.append(('  + %s 주입' if pid not in have else '  · %s 이미 있다') % pid)

if add:
    s = s[:close_at] + ',\n ' + ',\n '.join(src for _, src in add) + s[close_at:]

# ── 2. traps · nums ────────────────────────────────────────────────
for field in ('traps', 'nums'):
    ro, rc = array_span(ref, field)
    want = literals(ref[ro:rc + 1])
    mo, mc = array_span(s, field)
    have_l = literals(s[mo:mc + 1])
    hs = set(x[1:-1] for x in have_l)
    new = [x for x in want if x[1:-1] not in hs]
    if new:
        s = s[:mc] + ',\n  ' + ',\n  '.join(new) + s[mc:]
    log.append('%s — 여기 %d개 · 추가 %d개' % (field, len(have_l), len(new)))

# ── 2.5 카드 충돌 검사 (PMAP은 카드→패널 1:1이라 한쪽이 덮인다) ────
def cards_in(src):
    """패널 원문에서 카드 ID를 전부 뽑는다 (pc와 행 단위 모두)"""
    out, j = set(), 0
    while True:
        j = src.find('"', j)
        if j == -1:
            break
        k = src.index('"', j + 1)
        tok = src[j + 1:k]
        if 2 < len(tok) < 12 and '-' in tok and ' ' not in tok:
            out.add(tok)
        j = k + 1
    return out

idx = os.path.join(ROOT, 'index.html')
if add and os.path.exists(idx):
    import re, json as _json
    h = io.open(idx, encoding='utf-8').read()
    m = re.search(r'var PMAP=(\{.*?\});var PROW', h, re.S)
    if m:
        pmap = _json.loads(m.group(1))
        clash = set()
        for pid, src in add:
            for c in cards_in(src):
                for key in {c, c.split('#')[0]}:
                    if key in pmap and pmap[key] != pid:
                        clash.add((key, pmap[key], pid))
        clash = sorted(clash)
        if clash:
            log.append('⚠ 카드 충돌 %d건 — PMAP은 카드→패널 1:1이라 한쪽이 덮인다:' % len(clash))
            for c, was, now in clash:
                log.append('    %s : 여기 %s → 라이브 %s' % (c, was, now))
            log.append('  둘 중 어느 패널이 그 카드를 더 잘 나르는지 사람이 판정한다.')
        else:
            log.append('카드 충돌 0건 — 들어오는 카드가 전부 여기서 미연결이다')

# ── 3. 쓰기 전에 반드시 재파싱 ─────────────────────────────────────
tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8')
tmp.write(s); tmp.close()
lib = os.path.join(ROOT, 'test', '_lib').replace('\\', '/')
js = ("const L=require('%s'),fs=require('fs');"
      "const D=L.parseDATA(fs.readFileSync(process.argv[1],'utf8'));"
      "const c=D.find(x=>x.id==='%s');"
      "process.stdout.write(JSON.stringify({scenes:D.length,"
      "panels:D.reduce((a,x)=>a+x.panels.length,0),"
      "s34:c.panels.map(p=>p.id),traps:c.traps.length,nums:c.nums.length}));") % (lib, SCENE)
r = subprocess.run(['node', '-e', js, tmp.name], cwd=ROOT, capture_output=True, text=True)
os.unlink(tmp.name)

print('\n'.join(log))
if r.returncode != 0:
    print('\n❌ 재파싱 실패 — 원본은 건드리지 않았다.\n' + (r.stderr or '')[-1500:])
    sys.exit(1)
print('재파싱 OK →', r.stdout)
print('길이 %d → %d (%+d)' % (orig_len, len(s), len(s) - orig_len))

if CHECK:
    print('\n--check 이므로 파일은 쓰지 않았다.')
    sys.exit(0)

io.open(SK, 'w', encoding='utf-8').write(s)

imgs = [l.strip() for l in sh('git', 'ls-tree', '--name-only', '%s' % REF, 'img/').splitlines()
        if os.path.basename(l).startswith(SCENE)]
print('\n✅ sketchy.html 갱신. 이제:')
print('   git checkout %s -- %s' % (REF, ' '.join(imgs)))
print('   node build.js && npm test')
print('   그 뒤 test/baseline.json을 실측값으로 올린다.')
print('\n⚠ img/s34p02.webp는 반드시 새 것으로 덮어쓴다. 옛 s34p02는 바구니에 붉은 옷이 있어')
print('   s34p03의 「붉은 옷 = 정자」와 충돌한다 — 적대적 검수 단독 실격 항목이다.')
