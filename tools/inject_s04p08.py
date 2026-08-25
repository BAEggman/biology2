# -*- coding: utf-8 -*-
"""s04p08 「세 겹 반죽 — 낭배와 배엽」 주입.

  python3 tools/inject_s04p08.py --check
  python3 tools/inject_s04p08.py
"""
import io, os, re, sys, subprocess, tempfile

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK    = os.path.join(ROOT, 'sketchy.html')
CHECK = '--check' in sys.argv

T = '난할의 두 길 — 선구와 후구'

BR = ('맨 위 띠가 <b>발생의 네 걸음</b>이고, 그 아래가 <b>왼쪽 선구 · 오른쪽 후구</b>다. '
      '왼쪽은 <b>어긋나게 쌓이고 · 덜 된 채로 나오고 · 덩이가 갈라진다</b>. '
      '오른쪽은 <b>똑바로 쌓이고 · 온전한 채로 나오고 · 벽에서 주머니가 떨어진다</b>. 셋이 다 짝이다.')

BX = """<p><b>맨 위 띠 넷이 동물 발생의 공통 순서다.</b> 한 덩이(접합자) → 금이 그어져 넷으로 갈린 덩이(<b>난할</b>) → 속이 빈 껍질(<b>포배</b>) → 엄지로 눌러 굴이 난 것(<b>낭배형성</b>, 그 결과가 <b>낭배</b>). 난할은 <b>커지지 않고 쪼개지기만</b> 한다 — 그림에서 공의 크기가 넷 내내 그대로인 것이 그 뜻이다.</p><p><b>아래는 왼쪽이 선구, 오른쪽이 후구다.</b> 세 줄이 나란히 짝을 이룬다.</p><p><b>첫째 줄 — 쌓는 법.</b> 왼쪽은 위 공이 아래 두 공 <b>사이 홈</b>에 앉아 층이 어긋난다(<b>나선난할</b>). 오른쪽은 위 공이 아래 공 <b>바로 위</b>에 앉아 줄이 곧다(<b>방사난할</b>). 나선인지 방사인지는 <b>위층이 어긋났나 곧은가</b>만 보면 된다.</p><p><b>둘째 줄 — 떼어 냈을 때.</b> 왼쪽 접시의 것은 <b>덜 된 덩어리</b>다 — 운명이 이미 정해져 있어 혼자서는 온전해지지 못한다(<b>결정난할</b>). 오른쪽 접시의 것은 작지만 <b>온전한 공</b>이다 — 할구가 아직 전능성을 가진다(<b>부정난할</b>). ★ <b>일란성 쌍둥이</b>가 후구동물에서 가능한 까닭이 바로 이것이다.</p><p><b>셋째 줄 — 체강이 생기는 법.</b> 왼쪽은 <b>속이 찬 붉은 덩이가 갈라져</b> 그 사이에 빈 곳이 생긴다(<b>분열체강</b>, schizo=쪼개다). 오른쪽은 <b>굴 벽에서 주머니가 떨어져 나와</b> 그 속이 빈 곳이 된다(<b>장체강</b>, entero=창자). 「덩이가 갈라지나, 벽이 떨어지나」가 이름 그대로다.</p><span class='q'><b>여기서 갈리는 문제.</b> 「4세포기 할구를 떼어도 완전한 개체가 되는 난할과 그 무리는?」 → <b>부정난할 · 후구동물</b>. 선구는 결정난할이라 안 된다. 그리고 선구·후구를 가르는 네 형질을 한 줄로 물으면 — 선구 = <b>나선 · 결정 · 분열체강 · 원구→입</b>, 후구 = <b>방사 · 부정 · 장체강 · 원구→항문</b>. 앞의 셋이 이 판에 있고 넷째(원구가 입이냐 항문이냐)는 옆 판 「후구 구역」에 있다.</span>"""

F = [
 ['맨 위 띠 — 화살표로 이어진 넷: 덩이 하나 → 금이 그어져 넷으로 갈린 덩이 → 속이 빈 껍질 → 엄지로 눌러 굴이 난 것',
  '<b>동물 발생의 공통 순서</b> — 접합자 → <b>난할</b> → <b>포배</b> → <b>낭배형성</b> → <b>낭배</b>. '
  '★ 공이 넷 내내 <b>커지지 않는다</b> — 난할은 쪼개지기만 하고 자라지 않는다',
  ['N0-5','N0-5#1','N0-5#2','N0-5#3','N0-5#4','N0-5#5']],
 ['왼쪽 위 — 공 무리가 <b>어긋나게</b> 쌓였다. 위 공이 아래 두 공 사이 홈에 앉는다',
  '<b>나선난할</b>(선구동물). 층이 비스듬히 어긋나는 것이 「나선」이다'],
 ['오른쪽 위 — 공 무리가 <b>똑바로</b> 쌓였다. 위 공이 아래 공 바로 위에 앉아 줄이 곧다',
  '<b>방사난할</b>(후구동물). 위아래가 곧게 줄 서는 것이 「방사」다'],
 ['왼쪽 접시 — 떼어 놓은 것이 <b>덜 된 덩어리</b>, 공이 되다 만 모양이다',
  '<b>결정난할</b> — 할구의 운명이 일찍 정해져 있어 혼자서는 온전해지지 못한다. 선구동물이 이쪽이다',
  ['N0-17']],
 ['오른쪽 접시 — 떼어 놓은 것이 작지만 <b>온전한 공</b>이다',
  '<b>부정난할</b> — 할구가 아직 전능성을 가져 떼어 내도 완전한 개체가 된다. '
  '★ <b>일란성 쌍둥이</b>가 후구동물에서 가능한 까닭이 이것이다',
  ['N0-18','N0-22','X-AN-5']],
 ['왼쪽 아래 — 속이 찬 붉은 덩이가 <b>가운데가 갈라져</b> 그 사이에 빈 틈이 났다',
  '<b>분열체강</b>(선구동물) — 중배엽 덩어리가 <b>쪼개져</b> 체강이 된다. schizo가 쪼갠다는 뜻이다',
  ['N0-19#1']],
 ['오른쪽 아래 — 굴 벽에서 <b>주머니 둘이 떨어져</b> 나오고 그 속이 비었다',
  '<b>장체강</b>(후구동물) — <b>원장 벽</b>에서 주머니가 떨어져 나와 체강이 된다. entero가 창자다',
  ['N0-19#2']],
 ['★ 왼쪽 칸이 통째로 <b>선구</b>, 오른쪽 칸이 통째로 <b>후구</b>다',
  '선구 = <b>나선 · 결정 · 분열체강</b> / 후구 = <b>방사 · 부정 · 장체강</b>. '
  '여기에 넷째 형질 <b>원구가 입이냐 항문이냐</b>를 더하면 넷이 된다 — 그것은 옆 판 「후구 구역」에 있다',
  ['S-AN-3','X-AN-3','N0-19']],
]

TRAPS = [
 '<b>난할은 자라지 않는다.</b> 쪼개지기만 하므로 전체 크기는 그대로다 — 세포 수만 는다. (캠벨 32장)',
 '<b>일란성 쌍둥이는 부정난할 덕이다.</b> 4세포기 할구를 떼어도 각각 온전한 개체가 된다 — 후구동물 쪽이다. (캠벨 32장)',
]

NUMS = [
 '<b>발생 네 걸음</b> 접합자 → 난할 → 포배 → 낭배형성(→낭배)',
 '<b>선구 vs 후구 네 형질</b> 나선·결정·분열체강·원구→입 / 방사·부정·장체강·원구→항문',
]


def q1(x):
    assert "'" not in x, "작은따옴표 리터럴에 ' 가 있다: " + x[:60]
    return "'" + x + "'"

def qb(x):
    assert '`' not in x and '${' not in x, '백틱 리터럴에 ` 또는 ${ 가 있다'
    return '`' + x + '`'

def q2(x):
    assert '"' not in x, '큰따옴표 리터럴에 " 가 있다: ' + x[:60]
    return '"' + x + '"'

def row(r):
    parts = [q2(r[0]), q2(r[1])]
    if len(r) > 2:
        parts.append('[' + ','.join(q2(c) for c in r[2]) + ']')
    return '[' + ','.join(parts) + ']'

PANEL = ("{id:'s04p08',t:" + q1(T) + ",br:" + q1(BR) + ",bx:" + qb(BX)
         + ",f:[" + ',\n  '.join(row(r) for r in F) + "]}")


def main():
    s = io.open(SK, encoding='utf-8').read()
    n0 = len(s)
    if "{id:'s04p08'" in s:
        print('이미 s04p08이 있다 — 아무것도 안 한다.'); return 0

    anc = ' 좌우대칭동물은 전부 여기다. 가운데 겹이 없으면 진짜 근육도 진짜 기관도 못 만든다",["N0-12","N0-12#1"]]]}'
    assert s.count(anc) == 1, '앵커가 %d개다' % s.count(anc)
    s = s.replace(anc, anc + ',\n ' + PANEL)

    def cb(t, i):
        op = t[i]; cl = ']' if op == '[' else '}'
        d, q, j = 0, None, i
        while j < len(t):
            c = t[j]
            if q:
                if c == '\\': j += 2; continue
                if c == q: q = None
            elif c in "'\"`": q = c
            elif c == op: d += 1
            elif c == cl:
                d -= 1
                if d == 0: return j
            j += 1
        raise AssertionError('짝 없음')

    i0 = s.find("{id:'s04'"); assert i0 != -1
    i1 = cb(s, i0)
    ins = []
    for field, items in (('traps', TRAPS), ('nums', NUMS)):
        f = s.find(field + ':[', i0)
        assert f != -1 and f < i1, '%s 배열을 못 찾았다' % field
        o = s.index('[', f); c = cb(s, o)
        add = [x for x in items if x not in s[o:c + 1]]
        if add:
            ins.append((c, ',\n  ' + ',\n  '.join(q1(x) for x in add)))
        print('%s — 추가 %d개' % (field, len(add)))
    for pos, txt in sorted(ins, reverse=True):
        s = s[:pos] + txt + s[pos:]

    tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8')
    tmp.write(s); tmp.close()
    lib = os.path.join(ROOT, 'test', '_lib').replace('\\', '/')
    js = ("const L=require('%s'),fs=require('fs');"
          "const D=L.parseDATA(fs.readFileSync(process.argv[1],'utf8'));"
          "const c=D.find(x=>x.id==='s04');const p=c.panels.find(x=>x.id==='s04p08');"
          "process.stdout.write(JSON.stringify({panels:D.reduce((a,x)=>a+x.panels.length,0),"
          "s04:c.panels.map(x=>x.id),f:p.f.length,"
          "links:p.f.reduce((a,r)=>a+((r[2]||[]).length),0),traps:c.traps.length,nums:c.nums.length}));") % lib
    r = subprocess.run(['node', '-e', js, tmp.name], cwd=ROOT, capture_output=True, text=True)
    os.unlink(tmp.name)
    if r.returncode != 0:
        print('❌ 재파싱 실패 — 원본 무손상\n' + (r.stderr or '')[-1200:]); return 1
    print('재파싱 OK →', r.stdout)
    print('길이 %d → %d (%+d)' % (n0, len(s), len(s) - n0))
    if CHECK:
        print('--check 이므로 파일은 쓰지 않았다.'); return 0
    io.open(SK, 'w', encoding='utf-8').write(s)
    print('✅ sketchy.html 갱신')
    return 0

sys.exit(main())
