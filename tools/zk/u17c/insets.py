# insets.py — cur7 → cur8: 왼쪽 아래 빈 벽에 틀선 칸 둘(같은 수갱의 다른 날) — 왼 칸은 cur5(V·문 없음) 무리, 오른 칸은 cur7(V·문 있음) 무리를 0.6 배로
import numpy as np
from PIL import Image, ImageDraw

S = 2
src5 = Image.open('cur5.png').convert('RGB'); src7 = Image.open('cur7.png').convert('RGB')
out = src7.copy(); d = ImageDraw.Draw(out)
# 수갱 무리 (1배) x 405~648, y 102~432
gx0, gy0, gx1, gy1 = 405, 102, 648, 432
scale = 0.60
w, h = round((gx1 - gx0) * scale), round((gy1 - gy0) * scale)   # ≈146 × 198 (1배)
# 칸 자리(1배): 왼 칸 x 72, 오른 칸 x 248 · y 165
slots = [(72, 165, src5), (248, 165, src7)]
for (px, py, src) in slots:
    reg = src.crop((gx0 * S, gy0 * S, gx1 * S, gy1 * S)).resize((w * S, h * S), Image.LANCZOS)
    out.paste(reg, (px * S, py * S))
    # 틀선: 바깥 크림 띠 + 짙은 갈색 테
    m = 5 * S
    d.rectangle([px * S - m, py * S - m, (px + w) * S + m, (py + h) * S + m], outline=(247, 241, 224), width=m)
    d.rectangle([px * S - 2, py * S - 2, (px + w) * S + 2, (py + h) * S + 2], outline=(62, 46, 34), width=3 * S)
out.save('cur8.png')
print('insets', w, h, [(px, py, px + w, py + h) for (px, py, _) in slots])
out.resize((1024, 434), Image.LANCZOS).save('view_cur8.png')
