import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

im = Image.open(sys.argv[1]).convert('RGB')
a = np.array(im)
base0 = np.array(Image.open('L22d_base0.png').convert('RGB'))
b2 = np.array(Image.open('L22d_b2.png').convert('RGB'))
H, W = a.shape[:2]
S = 2

# 1. Fix s11 half-cut brown pellets above the upper filter tank (x=1022..1115, y=395..458)
for y in range(395, 458):
    for x in range(1022, 1115):
        a[y, x] = base0[y, x]

# 2. Erase the cork stopper (x=1085..1104, y=1010..1035) while keeping the original hand (x <= 1084) intact
for y in range(1010, 1035):
    for x in range(1085, 1104):
        t = (x - 1085) / 19.0
        c_left = np.array([212, 200, 188], dtype=np.float32)
        a[y, x] = (c_left * (1 - t) + a[y, 1105].astype(np.float32) * t).astype(np.uint8)

# 3. Erase old vertical pipe stub above y=940 (x=1070..1100, y=865..940) using L22d_b2.png
a[865:939, 1070:1100] = b2[865:939, 1070:1100]

canvas = Image.fromarray(a).resize((W*S, H*S), Image.LANCZOS)
dr = ImageDraw.Draw(canvas, 'RGBA')

# Whole round dark-brown pellets trickling from under the leaf pile into the upper filter tank
pellets = [
    (1122, 412, 6), (1096, 420, 6), (1072, 432, 6),
    (1105, 442, 6), (1084, 452, 6),
]
for px, py, pr in pellets:
    dr.ellipse([(px-pr)*S, (py-pr)*S, (px+pr)*S, (py+pr)*S], fill=(128, 82, 45, 255), outline=(28, 22, 18, 255), width=2*S)

# Anti-aliased flat metallic blue-silver bottle cap held by the fingertips
cap_poly = [(1083*S, 1013*S), (1100*S, 1008*S), (1102*S, 1016*S), (1085*S, 1021*S)]
dr.polygon(cap_poly, fill=(185, 208, 226, 255), outline=(28, 22, 18, 255), width=2*S)

# Clean anti-aliased narrow pipe from cellar ceiling (1085, 944) -> (1085, 905) -> (1012, 905) -> (1012, 435) -> (1042, 355)
pts = [(1085*S, 944*S), (1085*S, 905*S), (1012*S, 905*S), (1012*S, 435*S), (1042*S, 355*S)]
dr.line(pts, fill=(28, 22, 18, 255), width=13*S, joint='curve')
dr.line(pts, fill=(192, 206, 216, 255), width=7*S, joint='curve')
dr.line([(1010*S, 903*S), (1010*S, 436*S)], fill=(232, 242, 248, 255), width=2*S)
dr.ellipse([1034*S, 350*S, 1050*S, 360*S], fill=(160, 175, 185, 255), outline=(28, 22, 18, 255), width=2*S)

# Crisp cartoon steam puffs with subtle dark-gray outline rising into the sky above pipe tip (1042, 350)
puffs = [
    (1042, 336, 9, 12),
    (1046, 314, 13, 15),
    (1038, 288, 17, 19),
    (1046, 256, 21, 22),
    (1040, 222, 24, 23),
]
for cx, cy, rx, ry in puffs:
    dr.ellipse([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], fill=(246, 251, 255, 215), outline=(145, 165, 180, 140), width=S)

canvas.resize((W, H), Image.LANCZOS).convert('RGB').save(sys.argv[2])
print("saved", sys.argv[2])
