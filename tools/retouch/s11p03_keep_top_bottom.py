#!/usr/bin/env python3
"""s11p03 — 제미나이 v1(가운데 벽 NER: 손상 둘레 윗켜만 도려낸 홈 · 톱을 가로로)이 손대지 말라던 위 벽(BER)의 오른쪽 끝
「망치로 새 벽돌을 얹는 자리」(중합효소가 빈자리를 채움)를 지우고 그 자리에 은빛 조각(= 위 벽 우라실 쇠 벽돌과 같은 모양)을 그림,
아래 벽(MMR) 절단기 둘레도 조금 바꿈 → 가운데 판(y 376..752)만 v1 에서 쓰고 위(0..376)·아래(752..)는 설치본에서 되옮긴다.
이음매 y 376–392 · 736–752 는 두 그림 모두 빈 바탕이라 줄 단위로 섞는다(8px).
사용: python3 tools/retouch/s11p03_keep_top_bottom.py <설치본.png> <v1.png> <출력.png>"""
import sys
import numpy as np
from PIL import Image
old_p, new_p, out = sys.argv[1:4]
O = np.asarray(Image.open(old_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
N = np.asarray(Image.open(new_p).convert('RGB').resize((1024, 1024), Image.LANCZOS), dtype=float)
w = np.zeros(1024)  # weight of NEW
Y0, Y1, F = 380, 748, 8
w[Y0:Y1] = 1.0
w[Y0 - F:Y0] = np.linspace(0, 1, F)
w[Y1:Y1 + F] = np.linspace(1, 0, F)
w = w[:, None, None]
res = N * w + O * (1 - w)
Image.fromarray(res.round().clip(0, 255).astype(np.uint8)).save(out)
print('saved', out)
