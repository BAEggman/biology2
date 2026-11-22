"""L38b-01 — 띠 두께 = 양. 둘째 · 셋째 · 넷째 시험관의 띠를 줄 단위로 다시 쌓는다(zbuild.py 의 pil 걸음).
  중간 띠(반검반흰 · 둘째 ~ 넷째) = 윤곽 사이 24 px(476 ~ 500) — 세 관 모두 같은 두께(중간 DNA 는 늘 두 분자)
  가벼운 띠(흰 · 셋째) = 24 px(408 ~ 432) → 셋째 관 1 : 1
  가벼운 띠(흰 · 넷째) = 72 px(384 ~ 456) → 넷째 관 3 : 1 · 두 관의 가벼운 띠 가운데(420)는 같다(밀도 = 자리) · 위 선반 판(아래 끝 371)과 13 px 띄움
  방법: 관 안쪽 열만 · 몸통 줄(띠 없는 줄)로 372 ~ 511 을 덮은 뒤, 옛 띠의 위 · 아래 윤곽 띠줄(곡선 그대로)을 새 자리로 옮기고 그 사이를 띠 속 줄로 채운다.
쓰는 법: python3 pil_bands.py <in.png> <out.png>"""
import sys
import numpy as np
from PIL import Image
A = np.array(Image.open(sys.argv[1]).convert('RGB')); B = A.copy()
TUBES = {  # 안쪽 x · 몸통 줄 · 가벼운 띠(옛 윗선 · 옛 아랫선 · 새 윗선 · 새 아랫선 · 속 줄) · 중간 띠 속 줄
    't2': dict(x=(1432, 1518), body=430, light=None),
    't3': dict(x=(1597, 1684), body=440, light=(398, 410, 408, 432, 405)),
    't4': dict(x=(1764, 1851), body=445, light=(386, 424, 384, 456, 405)),
}
MID = (466, 494, 476, 500, 480)          # 중간 띠: 옛 윗선 · 옛 아랫선 · 새 윗선 · 새 아랫선 · 속 줄(검 · 흰 나뉨 포함)
def band(xa, xb, ot, ob, nt, nb, fill):
    top = A[ot - 2:ot + 6, xa:xb]        # 윗선 띠줄 8 줄(위 몸통 · 선 · 아래 속)
    bot = A[ob - 2:ob + 6, xa:xb]        # 아랫선 띠줄 8 줄(위 속 · 선 · 아래 몸통)
    for y in range(nt + 6, nb - 2): B[y, xa:xb] = A[fill, xa:xb]
    B[nt - 2:nt + 6, xa:xb] = top; B[nb - 2:nb + 6, xa:xb] = bot
for t, c in TUBES.items():
    xa, xb = c['x']
    for y in range(372, 512): B[y, xa:xb] = A[c['body'], xa:xb]
    if c['light']: band(xa, xb, *c['light'])
    band(xa, xb, *MID)
Image.fromarray(B).save(sys.argv[2])
