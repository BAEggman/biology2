# -*- coding: utf-8 -*-
"""s04p07 「세 겹 반죽 — 낭배와 배엽」 주입.

  python3 tools/inject_s04p07.py --check
  python3 tools/inject_s04p07.py
"""
import io, os, re, sys, subprocess, tempfile

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK    = os.path.join(ROOT, 'sketchy.html')
CHECK = '--check' in sys.argv

T = '세 겹 반죽 — 낭배와 배엽'

BR = ('<b>겹의 자리가 곧 이름이다</b> — 바깥이 외배엽, 가운데가 중배엽, 안이 내배엽. '
      '외우기 어려운 것은 이름이 아니라 <b>어느 겹에서 뭐가 나오는가</b>다. '
      '겹마다 끈이 하나씩 나와 자기 산물로 이어져 있다.')

BX = """<p><b>손가락 자국 하나가 낭배형성이다.</b> 속이 빈 공(포배)의 한쪽을 안으로 밀어 넣으면 굴이 생긴다. 그 굴이 <b>원장</b>(archenteron, 미래의 소화관)이고 굴의 입구가 <b>원구</b>(blastopore)다. 밀려 들어간 자리라 <b>굴 안벽이 곧 안쪽 겹</b>이 된다 — 그림에서 굴의 안쪽 색이 맨 안 겹과 같은 이유가 이것이다.</p><p><b>시험이 노리는 곳은 딱 두 군데다.</b> ① <b>간과 폐가 내배엽</b>이라는 것. 둘 다 「기관」이라 중배엽 같아 보이지만, 발생에서는 <b>소화관 벽에서 곁주머니로 부풀어 나온 것</b>이라 안쪽 겹의 산물이다. 그림에서 두 주머니가 굴 벽에 붙어 있는 것이 그 장면이다 — 잎사귀 모양이 폐, 묵직하게 처진 자루가 간이다. ② <b>중추신경이 외배엽</b>이라는 것. 뇌와 척수가 겉가죽과 같은 겹에서 나온다는 것이 뜻밖이라 자주 틀린다. 겉 겹의 한 자락이 <b>안으로 접혀 들어가 관</b>이 된 것이 신경관이고, 그래서 선반 위의 대롱은 <b>속이 뚫려</b> 있다.</p><p><b>가운데 겹만 「대부분」을 맡는다.</b> 근육·뼈·심장·콩팥·생식샘·진피 — 몸의 살점 대부분이 중배엽이다. 그래서 붉은 끈 끝에는 물건이 하나가 아니라 <b>연장이 쏟아지는 상자</b>가 놓여 있다. 「대부분」이라는 말이 그림에서 상자 하나로 뭉쳐 있는 것이다.</p><p><b>왼쪽의 작은 공에는 붉은 겹이 없다.</b> 겹이 둘뿐인 동물 — <b>자포동물과 유즐동물</b>이 그것이고, 좌우대칭동물은 전부 셋이다. 가운데 겹이 없으면 <b>진짜 근육도 진짜 기관도 못 만든다</b>. 해파리가 물살에 실려 다니는 까닭이 여기 있다.</p><span class='q'><b>여기서 갈리는 문제.</b> 「간·이자·폐는 어느 배엽에서 유래하는가」 → <b>내배엽</b>. 「기관이니까 중배엽」으로 고르면 오답이다. 반대로 「진피·뼈·혈액」을 물으면 <b>중배엽</b>이고, 「표피·뇌·척수·망막」을 물으면 <b>외배엽</b>이다. 셋을 가르는 기준은 <b>겉인가 속인가</b>가 아니라 <b>어느 겹에서 떨어져 나왔는가</b>다.</span>"""

F = [
 ['오른쪽 옆구리를 엄지로 눌러 안으로 깊이 난 굴 하나 — 바깥에 뚫린 둥근 입구가 있다',
  '<b>낭배형성</b>이다. 속 빈 공(포배)의 한쪽이 안으로 밀려 들어가 <b>낭배</b>가 된다. '
  '생긴 굴이 <b>원장</b>(미래의 소화관)이고 그 입구가 <b>원구</b>다',
  ['N0-5#4','N0-5#5','N0-6']],
 ['잘린 면에 겹이 셋 — 바깥부터 파랑 · 빨강 · 노랑이 고르게 둘러 있다',
  '<b>세 배엽</b>. 바깥이 <b>외</b>배엽, 가운데가 <b>중</b>배엽, 안이 <b>내</b>배엽이다. '
  '★ 이름의 외·중·내가 곧 겹의 자리다 — 이름은 외울 것이 없고, 외울 것은 겹마다 무엇이 나오는가뿐이다. '
  '좌우대칭동물은 모두 셋이다',
  ['N0-7','N0-12#2']],
 ['맨 바깥 <b>파란</b> 겹에서 나온 파란 끈 → 선반의 <b>가죽 조각</b>과 <b>양끝이 뚫린 대롱</b>(가까운 끝에 작은 혹이 달렸다)',
  '<b>외배엽 = 외피 · 중추신경</b>. 가죽이 겉껍질이고, 속이 뚫린 대롱이 <b>신경관</b>(혹이 뇌)이다. '
  '★ 겉 겹의 한 자락이 <b>안으로 접혀 들어가 관이 된 것</b>이 신경관이라, 뇌·척수가 피부와 같은 겹에서 나온다. '
  '시험이 여기를 노린다',
  ['N0-7#1']],
 ['가운데 <b>빨간</b> 겹에서 나온 빨간 끈 → <b>불끈 솟은 팔뚝</b>과 그 뒤의 <b>연장이 쏟아지는 상자</b>',
  '<b>중배엽 = 근육 · 대부분의 기관</b>. 팔뚝이 근육이고, 물건 하나가 아니라 <b>상자째</b>인 것이 「대부분」이다 — '
  '뼈 · 심장 · 콩팥 · 생식샘 · 진피가 다 여기서 나온다',
  ['N0-7#3']],
 ['맨 안 <b>노란</b> 겹 — 끈이 선반으로 안 가고 <b>굴 안벽</b>을 따라 되돌아 들어간다. '
  '그 벽에서 <b>곁주머니 둘</b>이 부풀어 나왔다 — 위는 <b>잎사귀 모양</b>, 아래는 <b>묵직하게 처진 자루</b>',
  '<b>내배엽 = 소화관 내벽 · 간 · 폐 내벽</b>. 굴 안벽이 곧 소화관 안벽이고, '
  '★ <b>간과 폐는 그 벽에서 곁주머니로 부풀어 나온 것</b>이라 내배엽이다 — 잎사귀가 폐, 처진 자루가 간. '
  '「기관이니까 중배엽」이 이 카드의 대표 오답이다',
  ['N0-7#2']],
 ['왼쪽에 뚝 떨어진 작은 공 — 잘린 면에 겹이 <b>둘</b>뿐이고 <b>빨간 겹이 아예 없다</b>',
  '<b>2배엽</b> — 외배엽 + 내배엽뿐이다(<b>자포동물 · 유즐동물</b>). 3배엽은 외 + 중 + 내이고 '
  '좌우대칭동물은 전부 여기다. 가운데 겹이 없으면 진짜 근육도 진짜 기관도 못 만든다',
  ['N0-12','N0-12#1']],
]

TRAPS = [
 '<b>간·이자·폐는 내배엽이다.</b> 기관이라 중배엽처럼 보이지만 소화관 벽에서 곁주머니로 부풀어 나온 것이다. (캠벨 32장)',
 '<b>뇌·척수는 외배엽이다.</b> 겉 겹의 한 자락이 안으로 접혀 관이 된 것이 신경관이라 피부와 같은 겹에서 나온다. (캠벨 32장)',
]

NUMS = [
 '<b>세 배엽</b> 외(바깥)=외피·중추신경 / 중(가운데)=근육·대부분 기관 / 내(안)=소화관 내벽·간·폐 내벽',
 '<b>배엽 수</b> 2배엽=자포·유즐 / 3배엽=모든 좌우대칭동물',
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

PANEL = ("{id:'s04p07',t:" + q1(T) + ",br:" + q1(BR) + ",bx:" + qb(BX)
         + ",f:[" + ',\n  '.join(row(r) for r in F) + "]}")


def main():
    s = io.open(SK, encoding='utf-8').read()
    n0 = len(s)
    if "{id:'s04p07'" in s:
        print('이미 s04p07이 있다 — 아무것도 안 한다.'); return 0

    anc = '성체가 되어도 넷을 그대로 유지한다",["N2-2","N2-2#1","N2-2#2","S-AN-13"]]]}'
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
          "const c=D.find(x=>x.id==='s04');const p=c.panels.find(x=>x.id==='s04p07');"
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
