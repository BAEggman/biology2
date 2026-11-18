import sys, numpy as np, cv2
from PIL import Image

base = np.array(Image.open('L36c_b1.png').convert('RGB'))
cm_sd = cv2.resize(np.array(Image.open('z/cm_SDA1.png').convert('RGB')), (800, 450), interpolation=cv2.INTER_LANCZOS4)
cm_fr = cv2.resize(np.array(Image.open('z/cm_FRA1.png').convert('RGB')), (800, 450), interpolation=cv2.INTER_LANCZOS4)
up_sd = cv2.resize(np.array(Image.open('z/up_SD.png').convert('RGB')), (800, 450), interpolation=cv2.INTER_AREA)
up_fr = cv2.resize(np.array(Image.open('z/up_FR.png').convert('RGB')), (800, 450), interpolation=cv2.INTER_AREA)

# For SD (sleeping seed at x=260..512, y=45..405):
sub_sd = cm_sd[45:405, 260:512].copy()
sub_up_sd = up_sd[45:405, 260:512]
d_sky = np.max(np.abs(sub_sd.astype(np.int16) - np.array([184, 233, 250])), axis=2) < 28
d_grs = np.max(np.abs(sub_sd.astype(np.int16) - np.array([154, 214, 92])), axis=2) < 26
d_shd = np.max(np.abs(sub_sd.astype(np.int16) - np.array([118, 169, 68])), axis=2) < 22
same_sd = np.max(np.abs(sub_sd.astype(np.int16) - sub_up_sd.astype(np.int16)), axis=2) < 20
bg_sd = d_sky | d_grs | d_shd | same_sd
bg_sd[96:115, :60] = True
bg_sd[96:115, 238:] = True

bg_u8 = bg_sd.astype(np.uint8)
h, w = bg_u8.shape
ff = np.zeros((h+2, w+2), np.uint8)
for x in range(w):
    for y in [0, h-1]:
        if bg_u8[y, x] == 1:
            cv2.floodFill(bg_u8, ff, (x, y), 2)
for y in range(h):
    for x in [0, w-1]:
        if bg_u8[y, x] == 1:
            cv2.floodFill(bg_u8, ff, (x, y), 2)
fg_sd = (bg_u8 != 2).astype(np.uint8)
fg_sd = cv2.morphologyEx(fg_sd, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
cnts, _ = cv2.findContours(fg_sd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
filled_sd = np.zeros_like(fg_sd)
for c in cnts:
    if cv2.contourArea(c) > 200:
        cv2.drawContours(filled_sd, [c], -1, 1, -1)

# In the white pappus region (relative y < 105, x > 135), any sky-tinted pixel (B > R + 8) was blended with blue sky in cm_sd;
# since the scaled seed pappus sits over green grass (154, 214, 92), make sky-tinted pixels transparent!
r_sd, g_sd, b_sd = sub_sd[...,0].astype(np.float32), sub_sd[...,1].astype(np.float32), sub_sd[...,2].astype(np.float32)
sky_tint = (b_sd > r_sd + 6) & (g_sd > r_sd + 4)
filled_sd[:105, 135:][sky_tint[:105, 135:]] = 0
a_sd = cv2.GaussianBlur(filled_sd.astype(np.float32), (3,3), 0.6)

out = base.copy().astype(np.float32)
scale_sd = 0.72
nw, nh = int(w * scale_sd), int(h * scale_sd)
s_rgb = cv2.resize(sub_sd, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
s_a = cv2.resize(a_sd, (nw, nh), interpolation=cv2.INTER_AREA)[..., None]
px, py = 1255, 868
out[py:py+nh, px:px+nw] = out[py:py+nh, px:px+nw] * (1 - s_a) + s_rgb * s_a

b_boxes = [
    (52, 168, 204, 422),   # cherry
    (236, 224, 388, 422),  # strawberry
    (420, 152, 572, 422),  # pineapple
    (612, 236, 762, 422),  # apple
]
target_xs = [1460, 1558, 1656, 1754]
scale_fr = 0.56

for idx, (bx0, by0, bx1, by1) in enumerate(b_boxes):
    sub = cm_fr[by0:by1, bx0:bx1]
    bh0, bw0 = sub.shape[:2]
    d_sky = np.max(np.abs(sub.astype(np.int16) - np.array([184, 233, 250])), axis=2) < 25
    d_grs = np.max(np.abs(sub.astype(np.int16) - np.array([154, 214, 92])), axis=2) < 25
    d_shd = np.max(np.abs(sub.astype(np.int16) - np.array([118, 169, 68])), axis=2) < 22
    sub_up = up_fr[by0:by1, bx0:bx1]
    same_as_up = np.max(np.abs(sub.astype(np.int16) - sub_up.astype(np.int16)), axis=2) < 16
    # Also exclude grass-tuft dark strokes or man's blue pants (B > R + 25) outside the basket
    blue_pants = (sub[...,2].astype(np.int16) > sub[...,0].astype(np.int16) + 20)
    bg = d_sky | d_grs | d_shd | same_as_up | blue_pants
    bg_u8 = bg.astype(np.uint8)
    ff = np.zeros((bh0+2, bw0+2), np.uint8)
    for x in range(bw0):
        for y in [0, bh0-1]:
            if bg_u8[y, x] == 1:
                cv2.floodFill(bg_u8, ff, (x, y), 2)
    for y in range(bh0):
        for x in [0, bw0-1]:
            if bg_u8[y, x] == 1:
                cv2.floodFill(bg_u8, ff, (x, y), 2)
    fg = (bg_u8 != 2).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
    n_c, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    if n_c > 1:
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        fg = (labels == largest).astype(np.uint8)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(fg)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    # Erode 1px to ensure zero border fringe
    filled = cv2.erode(filled, np.ones((3,3), np.uint8), iterations=1)
    a_m = cv2.GaussianBlur(filled.astype(np.float32), (3,3), 0.6)
    nw, nh = int(bw0 * scale_fr), int(bh0 * scale_fr)
    s_rgb = cv2.resize(sub, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    s_a = cv2.resize(a_m, (nw, nh), interpolation=cv2.INTER_AREA)[..., None]
    tx = target_xs[idx]
    ty = 1132 - nh
    out[ty:ty+nh, tx:tx+nw] = out[ty:ty+nh, tx:tx+nw] * (1 - s_a) + s_rgb * s_a

Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save('L36c_final.png')
print("saved L36c_final.png")
