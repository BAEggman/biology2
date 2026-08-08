# -*- coding: utf-8 -*-
"""s04p04 「절지 갑옷 가게」 전면 재작 — 패널 블록을 통째로 갈아 끼운다.

  python3 tools/rewrite_s04p04.py --check
  python3 tools/rewrite_s04p04.py

안전장치: 앵커 1개 assert · 따옴표 검사 · 쓰기 전 node 재파싱 · 실패 시 원본 무손상
"""
import io, os, sys, subprocess, tempfile

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK    = os.path.join(ROOT, 'sketchy.html')
CHECK = '--check' in sys.argv

PC = ["N1-24", "S-AN-10"]
T  = '절지 갑옷 가게'

BR = ('절지동물은 <b>딱딱한 겉옷 + 마디 난 다리</b>다. 겉옷의 재료가 <b>키틴</b>이고, '
      '무리는 <b>얼굴에 붙은 것</b>으로 갈린다 — 갑각류만 더듬이 <b>2쌍</b>, 곤충은 <b>1쌍</b>, '
      '협각류는 <b>0쌍</b>에 집게 엄니. 진열장을 왼쪽 위부터 Z자로 읽으면 2 → 1 → 0으로 줄어든다.')

BX = """<p><b>이름이 곧 정의다.</b> 절지(節肢) = <b>마디 난 다리</b>. 모든 관절에 박힌 검은 경첩이 <b>관절지</b>이고, 이것이 절지동물 세 형질 중 하나다. 나머지 둘은 <b>외골격</b>과 <b>체절</b>. 셋을 「겉옷 · 마디 · 관절」로 묶어 두면 빠지지 않는다.</p><p><b>겉옷의 재료는 키틴이다.</b> 갑옷이 가재 껍질처럼 겹비늘진 것이 <b>키틴 외골격</b>이다. 균류의 <b>세포벽</b>도 같은 키틴이라 「균류와 절지동물의 공통점」을 물으면 답이 <b>키틴</b>이다 — 그래서 균류 마을(s05)의 벽도 같은 질감으로 그려 두었다. 겉옷은 자라지 않으므로 커지려면 <b>탈피</b>해야 하고, 그래서 선충과 함께 <b>탈피동물</b>이다.</p><p><b>진열장 넷이 곧 분류표다.</b> 왼쪽 위 → 오른쪽 위 → 왼쪽 아래로 <b>더듬이가 2쌍 → 1쌍 → 0쌍</b>으로 줄어든다.<br>• <b>갑각류</b> — 더듬이 <b>2쌍</b>. 절지동물 중 유일하다. 물통에 서 있는 것이 수생이라는 뜻이고, <b>물벼룩</b>이 곤충이 아니라 갑각류인 이유가 이것이다.<br>• <b>곤충(육각류)</b> — 더듬이 <b>1쌍</b> · 다리 <b>3쌍</b>. 곤충은 <b>갑각류에서 진화</b>했고 둘을 합쳐 범갑각류로 묶는다.<br>• <b>협각류</b> — 더듬이가 <b>아예 없고</b> 대신 <b>협각</b>(집게·엄니) 한 쌍. 거미·전갈·진드기·투구게가 여기다. 책허파로 숨 쉬고 거미는 부속지가 6쌍이다.<br>• <b>다지류</b> — 몸이 길고 마디마다 다리가 붙는다.</p><p><b>★ 말피기관은 곤충만의 것이 아니다.</b> 황동 관 다발을 <b>협각 갑옷</b>에 달아 둔 이유다. 「말피기관을 배설계로 쓰는 동물은?」의 답이 <b>거미</b>로 나온 적이 있다 — 곤충·다지류·협각류가 다 쓰고 <b>갑각류만 안 쓴다</b>. 오답으로 나오는 <b>지렁이는 신관</b>, <b>플라나리아는 원신관</b>이다.</p><p><b>다지류의 다리 수는 식성과 짝지어 외운다.</b> <b>노래기는 마디당 2쌍이고 초식</b>(풀을 물었다), <b>지네는 마디당 1쌍이고 육식</b>(독발톱에 붉은 방울, 고기를 물었다). <b>「다리가 많은 쪽이 순한 쪽」</b>으로 붙여 두면 뒤집히지 않는다. 강(綱) 이름도 갈린다 — <b>왕지네는 순각강</b>이지 결합강이 아니다.</p><p><b>나머지 형질을 한 줄로.</b> 절지동물은 <b>원중배엽 세포</b>에서 중배엽이 생기는 <b>진체강</b> 동물이고, <b>사다리꼴 신경계</b>와 <b>개방혈관계</b>를 쓰며 배설은 <b>말피기관</b>, 기체교환은 아가미 또는 곤충의 <b>기관계</b>다. <b>동물 중 종 수가 가장 많은 문</b>이고 <b>선구동물</b>이며 <b>겉뼈대</b>를 갖는다(극피동물은 속뼈대).</p><span class='q'><b>여기서 갈리는 문제.</b> <b>① 말피기관 → 거미.</b> 「말피기관을 배설계로 사용하는 동물은?」 → <b>③ 거미</b>. 오답 ①지렁이(신관) ②플라나리아(원신관) ④거머리 (BM하 #768). <b>② 협각류 고르기.</b> 「협각류(주형강)에 속하는 것은?」 → <b>③ 거미</b>. 오답은 메뚜기·바퀴벌레·노린재(곤충)와 <b>노래기(다지류)</b> (BM하 #1180). <b>③ 곤충이 아닌 것.</b> → <b>⑤ 물벼룩</b>(갑각류) (BM하 #1178). <b>④ 강 이름 짝짓기.</b> 「결합강 - 왕지네」가 <b>틀린</b> 연결이다 — 왕지네는 <b>순각강</b> (BM하 #1190). <b>⑤ 키틴.</b> 「균류와 절지동물의 공통점」 → <b>④ 키틴</b> (BM하 #1167), 「곤충·갑각류 외골격의 다당류」 → <b>④ chitin</b> (원광①-5). <b>⑥ 형질 묶음.</b> 「원중배엽 · 진체강 · 사다리꼴 신경계 · 개방혈관계 · 말피기관」 → <b>② 절지동물</b> (BM하 #1196).</span>"""

F = [
 ['가게의 모든 갑옷이 가재 껍질처럼 겹비늘로 덮여 있다 — 균류 마을의 벽과 같은 질감이다',
  '키틴 외골격. 균류의 세포벽과 재료가 같아서 「균류와 절지동물의 공통점」의 답이 키틴이다'],
 ['팔·다리 관절마다 박힌 검은 쇠 경첩',
  '관절지(節肢). 마디 난 다리가 이름 그대로이고, 외골격·체절과 함께 절지동물의 세 형질을 이룬다'],
 ['왼쪽 위 칸 — 투구에 더듬이 넷. 둘은 머리 위로, 둘은 얼굴 앞으로 가로. 물통 안에 서 있다',
  '갑각류. 절지동물 중 더듬이가 2쌍인 것은 이 무리뿐이고 물에 산다 — 물벼룩이 곤충이 아닌 이유가 이것이다', ["N1-27"]],
 ['오른쪽 위 칸 — 더듬이 둘이 머리 위로만, 얼굴 앞은 비어 있다',
  '곤충(육각류). 더듬이 1쌍 · 다리 3쌍. 갑각류에서 진화해 둘을 합쳐 범갑각류로 묶는다', ["N1-28"]],
 ['왼쪽 아래 칸 — 투구 위가 맨들맨들해 더듬이가 하나도 없고, 입 앞에 뾰족한 엄니 한 쌍',
  '협각류(거미·전갈·진드기·투구게). 더듬이가 아예 없고 대신 협각(집게·엄니)을 갖는다', ["N1-25", "N1-25#1", "N1-25#2", "X-AN-15"]],
 ['그 협각 갑옷의 허리에서 바닥으로 늘어진 황동빛 가는 관 다발 — 이 칸에만 있다',
  '말피기관. 곤충만이 아니라 거미도 쓴다 — 「말피기관을 쓰는 동물」의 답이 거미다. 지렁이는 신관, 플라나리아는 원신관이라 오답이다', ["H1-190", "H1-190#3"]],
 ['오른쪽 아래 칸 위쪽 — 다리가 빈틈없이 빽빽한 긴 몸이 풀을 물었다',
  '노래기. 마디당 다리 2쌍이고 초식이다 — 다리가 많은 쪽이 순한 쪽', ["N1-26", "N1-26#1"]],
 ['그 아래 — 다리가 성기게 벌어진 긴 몸이 독 방울 달린 발톱으로 고기를 물었다',
  '지네. 마디당 다리 1쌍이고 육식이며 독발톱을 갖는다. 왕지네는 순각강이지 결합강이 아니다', ["N1-26#2", "N1-33"]],
]

TRAPS = [
 '<b>말피기관은 곤충 전용이 아니다.</b> 협각류(거미)·다지류도 쓰고 갑각류만 안 쓴다. 「말피기관을 쓰는 동물」의 답으로 거미가 나온다 (BM하 #768).',
 '<b>더듬이 2쌍은 갑각류뿐이다.</b> 곤충은 1쌍, 협각류는 0쌍이다. 물벼룩은 갑각류라 곤충이 아니다 (BM하 #1178).',
 '<b>왕지네는 순각강이다.</b> 결합강이 아니다 (BM하 #1190). 노래기는 협각류가 아니라 다지류다 (BM하 #1180).',
 '<b>키틴은 균류와 절지동물의 공통점이다.</b> 균류는 세포벽, 절지동물은 외골격에 쓴다 (BM하 #1167 · 원광①-5).',
]

NUMS = [
 '<b>더듬이</b> 갑각류 2쌍 · 곤충 1쌍 · 협각류 0쌍 (다지류 1쌍)',
 '<b>다지류 다리</b> 노래기 마디당 2쌍(초식) · 지네 마디당 1쌍(육식) — 많은 쪽이 순하다',
]


def q1(x):
    assert "'" not in x, "작은따옴표: " + x[:50]
    return "'" + x + "'"


def q2(x):
    assert '"' not in x, '큰따옴표: ' + x[:50]
    return '"' + x + '"'


def qb(x):
    assert '`' not in x and '${' not in x, '백틱 위험'
    return '`' + x + '`'


def row(r):
    p = [q2(r[0]), q2(r[1])]
    if len(r) > 2:
        p.append('[' + ','.join(q2(c) for c in r[2]) + ']')
    return '[' + ','.join(p) + ']'


PANEL = ("{id:'s04p04',pc:[" + ','.join(q2(c) for c in PC) + "],t:" + q1(T)
         + ",br:" + q1(BR) + ",bx:" + qb(BX)
         + ",f:[" + ',\n  '.join(row(r) for r in F) + "]}")


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


def main():
    s = io.open(SK, encoding='utf-8').read(); n0 = len(s)

    i = s.find("{id:'s04p04'")
    assert i != -1, 's04p04를 못 찾았다'
    assert s.count("{id:'s04p04'") == 1, '중복'
    e = cb(s, i)
    old_len = e - i + 1
    s = s[:i] + PANEL + s[e + 1:]
    print('패널 블록 %d자 → %d자' % (old_len, len(PANEL)))

    # traps · nums (s04 장면 안)
    i0 = s.find("{id:'s04'"); i1 = cb(s, i0)
    ins = []
    for field, items in (('traps', TRAPS), ('nums', NUMS)):
        f = s.find(field + ':[', i0); assert f != -1 and f < i1
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
          "const c=D.find(x=>x.id==='s04');const p=c.panels.find(x=>x.id==='s04p04');"
          "process.stdout.write(JSON.stringify({panels:D.reduce((a,x)=>a+x.panels.length,0),"
          "t:p.t,pc:p.pc.length,f:p.f.length,links:p.f.filter(r=>r[2]).length,"
          "traps:c.traps.length,nums:c.nums.length}));") % lib
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
