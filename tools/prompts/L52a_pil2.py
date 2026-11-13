import cv2, numpy as np
im = cv2.imread('final_r1.png'); H, W = im.shape[:2]
# ① 알약 세균을 빨간 콩 크기로 줄임(0.6배)
x0, y0, x1, y1 = 462, 1050, 545, 1102
patch = im[y0:y1, x0:x1].copy()
TAB = np.array([161, 186, 201])
d = np.abs(patch.astype(int) - TAB).sum(axis=2)
m = (d > 28).astype(np.uint8) * 255
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
big = max(cnts, key=cv2.contourArea); mm = np.zeros_like(m); cv2.drawContours(mm, [big], -1, 255, -1)
bx, by, bw, bh = cv2.boundingRect(big); print('pill bbox', x0 + bx, y0 + by, bw, bh)
# 자리 비우기(탁자빛)
reg = im[y0:y1, x0:x1]; reg[cv2.dilate(mm, np.ones((5, 5), np.uint8)) > 0] = TAB
s = 0.6
sp = cv2.resize(patch[by:by + bh, bx:bx + bw], (round(bw * s), round(bh * s)), interpolation=cv2.INTER_AREA)
sm = cv2.resize(mm[by:by + bh, bx:bx + bw], (round(bw * s), round(bh * s)), interpolation=cv2.INTER_AREA)
cx, cy = x0 + bx + bw // 2 - 6, y0 + by + bh // 2 + 2
px, py = cx - sp.shape[1] // 2, cy - sp.shape[0] // 2
a = (sm.astype(np.float32) / 255)[..., None]
dst = im[py:py + sp.shape[0], px:px + sp.shape[1]].astype(np.float32)
im[py:py + sp.shape[0], px:px + sp.shape[1]] = (sp * a + dst * (1 - a)).astype(np.uint8)
# ② 공 오른쪽 위 바깥으로 나가는 화살표 · 알갱이 지움
CX, CY, R = 592, 968, 94
G = np.median(im[925:960, 700:740].reshape(-1, 3), axis=0); IN = np.median(im[915:935, 610:640].reshape(-1, 3), axis=0)
print('grass', G, 'ball in', IN)
for y in range(856, 924):
    for x in range(650, 724):
        rr = ((x - CX) ** 2 + (y - CY) ** 2) ** 0.5
        p = im[y, x].astype(int)
        if rr > R + 4: im[y, x] = G
        elif rr < R - 3 and p.sum() > 600: im[y, x] = IN
# ③ 가운데 작은 물감 공 속(하양) → 분홍
PINK = np.array([174, 128, 240]); HI = np.array([205, 175, 250])
yy, xx = np.mgrid[975:1030, 1080:1160]
ell = (((xx - 1118) / 27.0) ** 2 + ((yy - 1004) / 15.0) ** 2) <= 1
reg = im[975:1030, 1080:1160].astype(int)
light = reg.sum(axis=2) > 590
sel = ell & light
reg[sel] = PINK
hl = ((((xx - 1110) / 8.0) ** 2 + ((yy - 996) / 4.0) ** 2) <= 1) & sel
reg[hl] = HI
im[975:1030, 1080:1160] = reg.astype(np.uint8)
# ④ 금빛 끈 고리의 꼬리(풀린 끝) 지움 — 바닥빛
FL = np.median(np.concatenate([im[676:684, 1600:1636].reshape(-1, 3), im[704:710, 1600:1636].reshape(-1, 3)]), axis=0)
print('floor', FL)
reg = im[683:704, 1600:1640].astype(int)
dd = np.abs(reg - FL).sum(axis=2)
mt = (dd > 45).astype(np.uint8) * 255
mt = cv2.dilate(mt, np.ones((3, 3), np.uint8))
mask = np.zeros((H, W), np.uint8); mask[683:704, 1600:1640] = mt
im = cv2.inpaint(im, mask, 5, cv2.INPAINT_TELEA)
# ⑤ 펜촉 같은 기둥 꼭대기 → 납작한 뚜껑(하늘은 줄마다 양옆 빛으로 보간)
for y in range(236, 312):
    L = im[y, 562].astype(float); Rr = im[y, 628].astype(float)
    for x in range(566, 625):
        t = (x - 562) / 66.0
        im[y, x] = (L * (1 - t) + Rr * t).astype(np.uint8)
cv2.rectangle(im, (574, 310), (614, 322), (60, 60, 60), -1)
cv2.rectangle(im, (574, 310), (614, 322), (20, 20, 20), 2)
cv2.imwrite('final_r2.png', im)
for nm, (a0, b0, a1, b1, sc) in {'v_ball': (440, 840, 740, 1110, 2), 'v_tray': (1060, 960, 1180, 1040, 4), 'v_loop': (1590, 650, 1700, 720, 4), 'v_pen': (540, 230, 650, 360, 3), 'v_guest': (1640, 900, 1750, 980, 4)}.items():
    c = im[b0:b1, a0:a1]; cv2.imwrite(nm + '.png', cv2.resize(c, ((a1 - a0) * sc, (b1 - b0) * sc), interpolation=cv2.INTER_LANCZOS4))
