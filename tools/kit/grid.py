# grid.py <src.png> x0,y0,x1,y1 <배율> <out.png> [눈금 간격=20] — 그림 한 구역을 키워 눈금(빨강 = x · 파랑 = y · 5칸마다 좌표)을 얹는다. 구역 편집 상자 · PIL 좌표 · 상자(box)를 잡을 때 쓴다.
import sys
from PIL import Image, ImageDraw
src, box, f, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3]), sys.argv[4]
im = Image.open(src).convert('RGB').crop(box)
im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
d = ImageDraw.Draw(im)
step = int(sys.argv[5]) if len(sys.argv) > 5 else 20
for x in range(box[0] - box[0] % step, box[2], step):
    X = (x - box[0]) * f
    if X < 0: continue
    d.line([(X, 0), (X, im.height)], fill=(255, 0, 0) if x % (step*5) == 0 else (255, 180, 180), width=1)
    if x % (step*5) == 0: d.text((X + 2, 2), str(x), fill=(200, 0, 0))
for y in range(box[1] - box[1] % step, box[3], step):
    Y = (y - box[1]) * f
    if Y < 0: continue
    d.line([(0, Y), (im.width, Y)], fill=(0, 0, 255) if y % (step*5) == 0 else (180, 180, 255), width=1)
    if y % (step*5) == 0: d.text((2, Y + 2), str(y), fill=(0, 0, 200))
im.save(out)
