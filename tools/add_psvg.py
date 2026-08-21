# -*- coding: utf-8 -*-
"""도해 판을 「그림으로 복구」 화면에 인라인으로 띄운다.

★ 무엇이 문제였나 — 460장이 복구 화면에서 그림을 못 봤다
  showPicFix 는 img/<pid>.webp 만 그린다. 도해 판(d01p01 … d07p01, 21개)은
  webp 가 없어 PNOIMG 에 올라 있고, 그래서 **사실표만** 뜬다.
  그 판들에만 걸린 카드가 460장 — 걸린 카드 1838장의 4분의 1이다.
  「그림으로 복구」인데 그림이 없었다.

★ 왜 래스터가 아니라 인라인인가
  webp 로 구워 넣을 수도 있지만 ① 글꼴이 컨테이너 것으로 굳고 ② 작은 글자가 뭉개지고
  ③ 새 이진 파일 21개가 는다. SVG 를 그대로 넣으면 선명하고 확대해도 깨지지 않는다.
  전체 240KB 라 index.html 이 2.93MB → 3.17MB 가 된다 — 받아들일 만하다.

⚠ 같은 화면에 도해가 둘 이상 뜨면 <title id="t1"> 같은 id 가 겹친다.
   그림은 정상으로 나오고 스크린리더만 헷갈리는 정도라 그대로 둔다.
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── ① build.js — PSVG 지도를 만든다 ────────────────────────────────
p = os.path.join(ROOT, 'build.js')
s = open(p, encoding='utf-8').read()
assert 'PSVG' not in s, '이미 있다'

s = s.replace("     PNOIMG 이미지 없는 패널(도해)",
              "     PNOIMG 이미지 없는 패널(도해)\n"
              "     PSVG  패널 → 도해 SVG 원본 (복구 화면에 인라인으로 그린다)", 1)
s = s.replace("const PMAP={}, PROW={}, PTIT={}, PBR={}, PFACT={};",
              "const PMAP={}, PROW={}, PTIT={}, PBR={}, PFACT={}, PSVG={};", 1)
a = "    if(p.br) PBR[p.id]=p.br;"
assert s.count(a) == 1
s = s.replace(a, a + "\n    if(p.svg) PSVG[p.id]=p.svg;", 1)
a = "\n +';var PNOIMG='+JSON.stringify(NOIMG)+';/*BUILD:END*/';"
assert s.count(a) == 1
s = s.replace(a, "\n +';var PNOIMG='+JSON.stringify(NOIMG)"
                 "\n +';var PSVG='+JSON.stringify(PSVG)+';/*BUILD:END*/';", 1)
open(p, 'w', encoding='utf-8').write(s)
print('build.js — PSVG 지도 추가')

# ── ② index.html — 복구 화면이 SVG 를 그린다 ────────────────────────
p = os.path.join(ROOT, 'index.html')
s = open(p, encoding='utf-8').read()

a = "    if(!noimg[pid]) out+='<img class=\"pfimg\" loading=\"lazy\" src=\"img/'+pid+'.webp\" alt=\"\">';"
assert s.count(a) == 1
b = ("    /* [2026-08-21] 도해 판은 webp 가 없어 여기서 아무 그림도 안 나왔다 — 460장이 그랬다.\n"
     "       PSVG 에 원본이 있으면 그대로 심는다. 래스터보다 선명하고 확대해도 안 깨진다. */\n"
     "    if(!noimg[pid]) out+='<img class=\"pfimg\" loading=\"lazy\" src=\"img/'+pid+'.webp\" alt=\"\">';\n"
     "    else if(typeof PSVG!=='undefined' && PSVG[pid]) out+='<div class=\"pfsvg\">'+PSVG[pid]+'</div>';")
s = s.replace(a, b, 1)

a = '.pfimg{width:100%;max-width:520px;border-radius:10px;border:1px solid #FCD34D;display:block;margin:0 auto 8px}'
assert s.count(a) == 1
b = (a + '\n.pfsvg{width:100%;max-width:640px;border-radius:10px;border:1px solid #FCD34D;'
         'background:#fff;padding:6px;margin:0 auto 8px;overflow-x:auto}'
         '\n.pfsvg svg{width:100%;height:auto;display:block}')
s = s.replace(a, b, 1)
open(p, 'w', encoding='utf-8').write(s)
print('index.html — 복구 화면이 도해를 인라인으로 그린다 + .pfsvg 서식')
