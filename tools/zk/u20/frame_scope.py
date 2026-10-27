# frame_scope.py — cur1 → cur2: ① 세로 틀선(x 1686~1689)을 겹선 + 크림 여백으로 ② 닫힌 칸 스코프 발톱이 작은 흰 기포 하나를 또렷이 문다
import math, numpy as np
from PIL import Image, ImageDraw
A = np.asarray(Image.open('cur1.png').convert('RGB')).astype(float); H, W, _ = A.shape
img = Image.fromarray(A.astype('uint8')); d = ImageDraw.Draw(img)
DK, CREAM = (38, 32, 26), (247, 241, 224)
y0, y1 = 24, 847
d.rectangle([1681, y0, 1694, y1], fill=CREAM)
d.rectangle([1680, y0, 1682, y1], fill=DK); d.rectangle([1693, y0, 1695, y1], fill=DK)
# ② 기포 + 발톱(닫힌 칸 렌즈 중심 ≈ (1893,724) · 오른쪽으로 기포)
bx, by, r = 1916, 724, 9
d.ellipse([bx - r - 1, by - r - 1, bx + r + 1, by + r + 1], fill=(30, 30, 34))
d.ellipse([bx - r + 1, by - r + 1, bx + r - 1, by + r - 1], fill=(236, 242, 248))
d.ellipse([bx - r + 3, by - r + 3, bx - 1, by - 2], fill=(255, 255, 255))
d.arc([bx - r + 2, by - r + 2, bx + r - 2, by + r - 2], 20, 120, fill=(170, 186, 200), width=2)
GOLD, GOLD_D = (214, 170, 72), (90, 62, 20)
def claw(p0, p1, p2):
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, 12)]
    d.line(pts, fill=GOLD_D, width=5, joint='curve'); d.line(pts, fill=GOLD, width=3, joint='curve')
    d.ellipse([p2[0] - 2.2, p2[1] - 2.2, p2[0] + 2.2, p2[1] + 2.2], fill=GOLD, outline=GOLD_D)
claw((1899, 708), (1912, 700), (1921, 713))
claw((1899, 740), (1912, 748), (1921, 735))
img.save('cur2.png')
img.crop((1860, 680, 1950, 770)).resize((540, 540), Image.LANCZOS).save('v2_scope.png')
img.crop((1640, 400, 1740, 520)).resize((400, 480), Image.LANCZOS).save('v2_frame.png'); print('cur2 saved')
