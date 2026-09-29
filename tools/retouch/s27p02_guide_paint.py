#!/usr/bin/env python3
"""s27p02 — 개념 논리 M 1·3 + m(K⁺ = 칼): 제미나이에게 줄 **안내 그림**을 칠한다(설치본을 고치는 스크립트가 아니다).
v2(제미나이 같은 대화 둘째 그림: 구슬 → 칼 · 지붕 털·실·뚜껑문 ✓)는 아래 두 방 지붕 위에 큰 칼 더미가 남고 칼이 방 **안으로** 쏟아졌다 —
말로 두 번 고치라 해도 안 됨. 그래서 v2 위에 평면으로 칠해 「비울 곳(크림·벽색)」과 「칼 더미(회색 덩어리)」 자리를 박고,
새 대화에 「이 칠을 깨끗한 그림으로」라고 주었다(v3) → 같은 대화 후속으로 아래 두 방 안 더미를 더함(v4 = 설치본).
사용: python3 s27p02_guide_paint.py (작업 폴더에 s27p02_v2.png 가 있어야 함) → s27p02_guide.png"""
from PIL import Image, ImageDraw
im=Image.open('s27p02_v2.png').convert('RGB')
d=ImageDraw.Draw(im)
CREAM=(242,243,229); TEAL=(152,169,161); GRAYW=(172,170,163)
KN=(176,178,182); OUT=(70,70,72)
# 1) left: side heap above bottom-left room + center-roof spill on the left -> cream
d.polygon([(28,688),(28,640),(100,606),(170,556),(250,512),(300,484),(346,468),(346,688)],fill=CREAM)
d.polygon([(284,356),(346,356),(346,530),(284,530)],fill=CREAM)
# right mirror
d.polygon([(996,688),(996,640),(924,606),(854,556),(774,512),(724,484),(680,468),(680,688)],fill=CREAM)
d.polygon([(680,356),(742,356),(742,530),(680,530)],fill=CREAM)
# restore bottom rooms' top rims (dark line) where the heaps sat
d.line([(34,690),(338,690)],fill=(40,40,40),width=4)
d.line([(686,690),(988,690)],fill=(40,40,40),width=4)
# 2) inflow streams inside bottom rooms -> plain back wall
d.polygon([(205,694),(334,694),(334,702),(290,722),(262,746),(246,790),(240,840),(246,884),(210,890),(176,884),(170,840),(178,780),(195,730)],fill=TEAL)
d.polygon([(700,694),(820,694),(870,694),(905,730),(905,800),(900,880),(870,886),(840,880),(835,820),(820,760),(790,715),(740,700)],fill=GRAYW)
d.polygon([(104,694),(214,694),(206,740),(192,800),(180,852),(150,872),(118,866),(104,840)],fill=TEAL)
# 3) heaps inside top rooms (gray blobs)
for poly in [[(40,346),(112,346),(106,318),(82,302),(52,306),(40,318)],
             [(168,346),(252,346),(262,322),(240,300),(206,294),(178,306)],
             [(772,346),(852,346),(846,316),(816,298),(786,302),(772,318)],
             [(918,346),(986,346),(986,312),(960,300),(930,306),(918,320)]]:
    d.polygon(poly,fill=KN,outline=OUT)
# 4) outflow streams from the bottom rooms' doors into the middle corridor (gray streaks)
d.polygon([(338,902),(392,888),(452,922),(476,950),(424,962),(352,938)],fill=KN,outline=OUT)
d.polygon([(686,902),(634,888),(574,922),(550,950),(602,962),(672,938)],fill=KN,outline=OUT)
im.save('s27p02_guide.png'); im.save('s27p02_guide_for_gemini.png')

