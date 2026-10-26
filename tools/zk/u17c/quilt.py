# quilt.py — cur1 → cur1q: 수갱 바깥 누런 요를 「소금 더미에 걸친 이불」에서 「껍질 쐐기의 아래 켜」로 —
#   요의 위쪽 절반 남짓을 소금이 덮는다(불규칙 경계 · 합성 껍질 결 · 경계에 먹선) → 요는 소금 아래 깔린 누런 켜로 보인다 · 문과 가루는 그대로
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, binary_dilation, binary_fill_holes

src = Image.open('cur1.png').convert('RGB'); A = np.asarray(src).astype(float); C = A.copy(); H, W, _ = A.shape
rng = np.random.default_rng(11)
R, G, B = A[..., 0], A[..., 1], A[..., 2]
# 1) 요 가면(노랑 + 바느질 선) — 문 상자 제외
ym = (R > 150) & (G > 120) & (B < 135) & (R - B > 55)
box = np.zeros((H, W), bool); box[560:800, 950:1180] = True; ym &= box
ym = binary_dilation(ym, iterations=3); ym = binary_fill_holes(ym)
ext = binary_dilation(ym, iterations=5); zone = np.zeros((H, W), bool); zone[560:604, 1040:1140] = True
ym |= (ext & zone)                                   # 위 가장자리(껍질 쪽)로만 5px 더 — 옛 먹선 잔재를 덮는다
door = np.zeros((H, W), bool); door[612:669, 1134:1177] = True
ym &= ~door
ys, xs = np.where(ym); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
print('요 bbox', x0, y0, x1, y1)
h, w = y1 - y0, x1 - x0
# 2) 덮개 알파: 위 → 아래 램프(요 높이의 52% 까지) + 낮은 주파수 노이즈로 울퉁불퉁한 경계
nz = gaussian_filter(rng.random((h, w)), 5.0); nz = (nz - nz.mean()) / (nz.std() + 1e-6) * 0.28
yy = np.arange(h)[:, None] / h
grad = (0.52 - yy) * 7.0 + 0.5                      # 0.52h 에서 0.5 — 그 위는 1, 아래는 0 으로 빠르게
al = np.clip(grad + nz, 0, 1) * ym[y0:y1, x0:x1]
al = gaussian_filter(al, 0.8) * ym[y0:y1, x0:x1]
# 3) 합성 껍질 결: 흰 바탕 + 드문 회색 점 + 저주파 음영
salt = np.full((h, w, 3), 242.0); salt[..., 2] = 236
dots = rng.random((h, w)) < 0.03
salt[dots] = (122, 122, 116); salt = gaussian_filter(salt, (0.6, 0.6, 0))
shade = gaussian_filter(rng.random((h, w)), 5); shade = (shade - shade.mean()) * 55
salt += shade[..., None]
reg = C[y0:y1, x0:x1]; C[y0:y1, x0:x1] = reg * (1 - al[..., None]) + salt * al[..., None]
# 4) 경계 먹선(소금 가장자리가 요 위에 드리운 선) — al 0.5 등고선
m8 = ((al > 0.5) * 255).astype(np.uint8)
cs, _ = cv2.findContours(m8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
img = Image.fromarray(np.clip(C, 0, 255).astype('uint8')); d = ImageDraw.Draw(img, 'RGBA')
for c in cs:
    pts = [(int(p[0][0]) + x0, int(p[0][1]) + y0) for p in c]
    # 요 가면 안쪽(요 위에 드리운 경계)만 — 가면 밖 테두리는 원래 껍질 윤곽이 있다
    seg = []
    for (x, y) in pts:
        top_edge = (not ym[max(0, y - 3), x]) and ym[y, min(W - 1, x + 3)] and ym[y, max(0, x - 3)]
        if not top_edge: seg.append((x, y))
        else:
            if len(seg) > 3: d.line(seg, fill=(92, 86, 80, 225), width=2); d.line([(px, py + 3) for (px, py) in seg], fill=(150, 150, 146, 90), width=4)
            seg = []
    if len(seg) > 3: d.line(seg, fill=(92, 86, 80, 225), width=2); d.line([(px, py + 3) for (px, py) in seg], fill=(150, 150, 146, 90), width=4)
img.save('cur1q.png')
img.crop((880, 480, 1240, 868)).resize((720, 776), Image.LANCZOS).save('v_quilt_new.png')
print('cur1q saved')
