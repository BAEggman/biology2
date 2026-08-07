# -*- coding: utf-8 -*-
"""s04p06 「척삭 상회」 주입 — sketchy.html을 재직렬화하지 않고 문자열로 끼워 넣는다.

  python3 tools/inject_s04p06.py --check   # 검사만
  python3 tools/inject_s04p06.py           # 주입

안전장치
  · 앵커가 정확히 1개인지 assert
  · 이미 s04p06이 있으면 중단 (멱등)
  · 백틱 리터럴에 ` 또는 ${ 가 있으면 중단
  · 작은따옴표 리터럴에 ' 가 있으면 중단
  · 쓰기 전 node로 재파싱, 실패하면 원본 무손상
"""
import io, os, re, sys, subprocess, tempfile

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK    = os.path.join(ROOT, 'sketchy.html')
CHECK = '--check' in sys.argv

PC = ["S-AN-13", "J0-29", "N2-2", "N2-2#1", "N2-2#2", "N2-3", "N2-3#1", "N2-3#2"]

T = '척삭 상회'

BR = ('척삭동물의 네 가지가 건물 하나에 다 있다 — <b>들보(척삭)</b> · <b>그 위의 속 빈 관(등쪽 신경관)</b> · '
      '<b>앞벽의 틈(인두열)</b> · <b>뒷문보다 뒤로 뻗은 뒤채(항문 뒤 꼬리)</b>. '
      '<b>위·앞·뒤라는 자리가 곧 이름이다.</b> 오른쪽 작은 가게는 어른이 되며 틈만 남기고 다 잃었다.')

BX = """<p><b>자리가 이름을 말한다.</b> 넷 중 셋은 <b>어디에 있는가</b>가 그대로 이름이다. <b>등쪽</b> 속 빈 신경관은 들보보다 <b>위</b>, <b>인두</b>열은 목이라 <b>앞</b>, <b>항문 뒤</b> 꼬리는 뒷문보다 <b>뒤</b>. 위치를 외우면 이름이 따라 나온다.</p><p><b>무척추동물과 정확히 반대인 자리가 둘이다.</b> 무척추동물의 신경삭은 <b>배쪽</b>이고 <b>속이 차 있다</b>(고형). 척삭동물은 <b>등쪽</b>이고 <b>속이 비어 있다</b>. 그래서 그림에서 흰 관은 들보 <b>위</b>에 있고 양 끝이 <b>뚫려</b> 있다 — 둘 다 무척추동물과 뒤집힌 것이다. 같은 장면의 은색 배관(s04p03)은 <b>순환계</b>이니 색으로 갈라 둔다.</p><p><b>척삭은 척추가 아니다.</b> 척삭은 속이 찬 막대 하나이고, 척추동물에서는 발생 중에 <b>척추가 그 자리를 대신</b>한다. 그래서 사람은 성체에 척삭이 없고 <b>추간판의 수핵</b>에 흔적만 남는다. 「척삭동물이면 척추가 있다」는 선지는 오답이다 — 창고기·멍게는 척추가 없다.</p><p><b>인두열은 처음부터 숨쉬기용이 아니었다.</b> 원래는 <b>물을 걸러 먹는</b> 여과 장치이고, 어류에 와서 <b>아가미</b>가 되었다. 기출에서는 <b>새열(鰓裂)</b>이라고도 쓴다 — 같은 것이다.</p><p><b>오른쪽 작은 가게가 시험에 나오는 자리다.</b> 멍게(피낭동물·미삭동물)는 <b>유생 때만</b> 넷을 다 갖고, 성체가 되면 부두에 <b>딱 붙어</b>(고착) 물을 걸러 먹으며 <b>인두열만 남긴다</b>. 벽에 걸린 액자 속 자기 모습이 그 유생 시절이다. 반대로 <b>창고기(두삭동물)</b>는 성체가 되어도 넷을 <b>그대로 유지</b>한다 — 그래서 조상 척삭동물이 창고기와 비슷했으리라 본다.</p><span class='q'><b>여기서 갈리는 문제.</b> <b>① 「새열만 남는 동물」을 묻는다.</b> 「척삭동물 중 유생 때는 인두·새열·근육질 꼬리에 척삭과 배신경색을 갖지만, 성체가 되며 꼬리·척삭·신경계 대부분이 없어지고 <b>새열만 갖는</b> 동물은?」 → <b>④ 멍게</b> (BM하 #1176). 오답 <b>①창고기</b>가 정확히 반대 극이다 — <b>평생 척삭을 유지</b>한다. <b>②먹장어·③칠성장어</b>는 무악류라 척삭을 성체까지 유지하고, <b>⑤뱀장어</b>는 경골어다. 액자 걸린 가게가 멍게라는 것만 붙들면 된다. <b>② 4대 특징을 나열시킨다.</b> 「척삭동물의 4가지 특징은 <b>신경다발(신경삭)·척삭·인두열·꼬리</b>이다」가 <b>옳은</b> 선지로 나온다 (BM하 #1198 ③). 넷을 셀 때 <b>「위·앞·뒤 그리고 관통하는 막대」</b>로 세면 빠뜨리지 않는다.</span>"""

F = [
 ['쇠받침 셋에 얹혀 벽 앞을 앞뒤로 가로지르는 굵은 나무 들보 하나 — 잘린 끝의 나이테가 통짜임을 보여 준다',
  '척삭(notochord). 속이 찬 막대 하나가 몸을 앞뒤로 꿴다. 척추가 아니라 척삭이다 — 척추동물에서는 나중에 척추가 이 자리를 대신한다'],
 ['그 들보 바로 위에 나란히 얹힌 흰 관 — 양 끝이 뚫려 속이 들여다보인다',
  '등쪽 속 빈 신경관(dorsal hollow nerve cord). 「등쪽」이라 들보보다 위에 있고 「속 빈」이라 관이다. 무척추동물의 신경삭은 배쪽이고 속이 차 있다 — 정확히 반대다'],
 ['왼쪽 끝 벽에 세로로 촘촘히 뚫린 좁은 틈 여럿',
  '인두열(pharyngeal slits). 인두는 목이라 앞쪽에 있다. 물을 걸러 먹는 데 쓰다가 어류에서 아가미가 된다', ["J0-29"]],
 ['청록 뒷문보다 더 뒤로 뻗어 나가 끝이 뾰족한 낮은 부속 건물',
  '항문 뒤 꼬리(post-anal tail). 뒷문(항문)보다 뒤에 있다는 것이 이름 전부다 — 항문 앞이면 꼬리가 아니다'],
 ['오른쪽에 뚝 떨어져 혼자 선 통 건물 — 들보도 흰 관도 뒤채도 없고 왼쪽 벽의 틈만 남았다',
  '피낭동물(멍게, 미삭동물). 성체는 넷 중 인두열(새열)만 남기고 척삭·꼬리·신경계 대부분을 잃는다', ["N2-3", "N2-3#1"]],
 ['그 통의 밑동이 부둣돌에 붙어 굳었고, 지붕의 깔때기로 물이 쏟아져 들어간다',
  '성체 멍게는 고착 생활을 하며 물을 걸러 먹는다(여과섭식). 물은 들어가는 쪽이다 — 뿜어 나오는 것이 아니다', ["N2-3#2"]],
 ['통 벽에 걸린 액자 — 액자 속 자기 자신은 들보·흰 관·틈·작은 문과 그 문보다 뒤의 꼬리를 다 갖고 있다',
  '유생 때는 네 가지를 다 갖는다. 반대로 두삭동물(창고기)은 성체가 되어도 넷을 그대로 유지한다', ["N2-2", "N2-2#1", "N2-2#2"]],
]

TRAPS = [
 '<b>척삭은 척추가 아니다.</b> 속이 찬 막대 하나이고, 척추동물에서는 척추가 그 자리를 대신해 성체엔 추간판 수핵에만 남는다. 창고기·멍게는 척추가 없다. (캠벨 34장)',
 '<b>신경관은 등쪽이고 속이 비어 있다.</b> 무척추동물의 신경삭은 배쪽이고 속이 차 있다 — 두 가지가 다 반대다. (캠벨 34장)',
 '<b>항문 「뒤」 꼬리다.</b> 항문보다 뒤에 있어야 꼬리다. 항문 앞이면 꼬리가 아니다. (캠벨 34장)',
 '<b>멍게는 성체에 새열만 남는다.</b> 척삭·꼬리·신경계 대부분을 잃는다. 평생 유지하는 것은 창고기다 (BM하 #1176).',
]

NUMS = [
 '<b>척삭동물 4대 특징</b> 척삭(관통하는 막대) · 등쪽 속 빈 신경관(위) · 인두열(앞) · 항문 뒤 꼬리(뒤)',
 '<b>유지 정도</b> 두삭(창고기) = 성체도 넷 다 / 피낭(멍게) = 유생만 넷, 성체는 새열만',
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


PANEL = ("{id:'s04p06',pc:[" + ','.join(q2(c) for c in PC) + "],t:" + q1(T)
         + ",br:" + q1(BR) + ",bx:" + qb(BX)
         + ",f:[" + ',\n  '.join(row(r) for r in F) + "]}")


def main():
    s = io.open(SK, encoding='utf-8').read()
    n0 = len(s)
    if "{id:'s04p06'" in s:
        print('이미 s04p06이 있다 — 아무것도 안 한다.'); return 0

    # ── 패널: s04p05 블록 끝 바로 뒤에 붙인다 ────────────────────────
    anc = '["등을 따라 난 곧은 막대","척삭"]]}'
    assert s.count(anc) == 1, '앵커가 %d개다 (1개여야 한다)' % s.count(anc)
    s = s.replace(anc, anc + ',\n {id:__P__}'.replace('{id:__P__}', PANEL))

    # ── traps · nums: s04 장면 안에서만 ──────────────────────────────
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

    i0 = s.find("{id:'s04'"); assert i0 != -1, 's04 장면을 못 찾았다'
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

    for pos, txt in sorted(ins, reverse=True):     # 뒤에서 앞으로
        s = s[:pos] + txt + s[pos:]

    # ── 재파싱 ──────────────────────────────────────────────────────
    tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8')
    tmp.write(s); tmp.close()
    lib = os.path.join(ROOT, 'test', '_lib').replace('\\', '/')
    js = ("const L=require('%s'),fs=require('fs');"
          "const D=L.parseDATA(fs.readFileSync(process.argv[1],'utf8'));"
          "const c=D.find(x=>x.id==='s04');const p=c.panels.find(x=>x.id==='s04p06');"
          "process.stdout.write(JSON.stringify({panels:D.reduce((a,x)=>a+x.panels.length,0),"
          "s04:c.panels.map(x=>x.id),pc:p.pc.length,f:p.f.length,"
          "links:p.f.filter(r=>r[2]).length,traps:c.traps.length,nums:c.nums.length}));") % lib
    r = subprocess.run(['node', '-e', js, tmp.name], cwd=ROOT, capture_output=True, text=True)
    os.unlink(tmp.name)
    if r.returncode != 0:
        print('❌ 재파싱 실패 — 원본 무손상\n' + (r.stderr or '')[-1200:]); return 1
    print('재파싱 OK →', r.stdout)
    print('길이 %d → %d (%+d)' % (n0, len(s), len(s) - n0))

    if CHECK:
        print('--check 이므로 파일은 쓰지 않았다.'); return 0
    io.open(SK, 'w', encoding='utf-8').write(s)
    print('✅ sketchy.html 갱신 → node build.js && npm test')
    return 0


sys.exit(main())
