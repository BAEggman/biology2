#!/usr/bin/env python3
"""frame_panels.py — 통합판 오른쪽에 「틀선으로 떼어 낸 세로 칸」을 놓는다 (2026-10-17 · s32u01 v12).

  python3 frame_panels.py base2x.png out.png --panels top.png,mid.png,bot.png
          [--crops "x0,y0,x1,y1;x0,y0,x1,y1;x0,y0,x1,y1"] [--layout layout.json] [--boxes boxes.json]

- 큰 장면 오른쪽 끝에 바깥 테두리와 같은 선을 긋고(설치본 테두리 단면 — 헤일로·램프·코어·램프·헤일로 — 을 그대로 옮김),
  세로 틈(바깥 여백과 같은 종이색) 뒤에 칸 셋을 위→아래로 붙인다. 칸마다 제 테두리 · 가로 틈도 종이색.
- 선은 「더 어두운 값이 이긴다」로 겹쳐 모서리가 깔끔하다.
- --crops: 칸 그림마다 쓸 사각형(그 그림의 화소 좌표). 비우면 칸 비율에 맞춰 가운데를 자른다.
- 기본 배치(2배 2048×868 — 바깥 테두리 코어: 위 37 · 아래 831 · 왼 40 · 오른 2008):
  큰 장면 오른쪽 선 코어 x 1478 · 세로 틈(종이) 1483–1514(32) · 칸 왼쪽 선 코어 1519 · 칸 안 x 1521–2006(486)
  칸 안 y 39–278 / 315–553 / 590–829 (가로 틈 24) · 칸 크기 486×240 안팎.
--boxes 로 칸 안 사각형을 json 으로 남긴다(언샤프를 칸 안에만 걸 때 쓴다)."""
import argparse, json
import numpy as np
from PIL import Image

PAPER = np.array([252, 240, 219], float)
PROFILE = [254, 255, 167, 7, 0, 39, 159, 240, 254]   # 바깥 → 안 · index 4 = 코어 가운데
HALF = 4

DEF = {
    'main_right_core': 1478,
    'panel_left_core': 1519,
    'outer_right_core': 2008, 'outer_top_core': 37, 'outer_bot_core': 831,
    'panel_x': [1521, 2006],
    'panel_cores_y': [[37, 280], [313, 555], [588, 831]],   # 칸마다 (위 선 코어, 아래 선 코어)
}

class Lines:
    def __init__(s, H, W):
        s.V = np.full((H, W), 255.0); s.F = np.zeros((H, W), bool)
    def v(s, xc, y0, y1, inside=+1):
        """세로 선 · inside=+1 이면 오른쪽이 안(왼 테두리), -1 이면 왼쪽이 안"""
        for k, val in enumerate(PROFILE):
            x = xc + (k - HALF) * inside
            s.V[y0:y1 + 1, x] = np.minimum(s.V[y0:y1 + 1, x], val); s.F[y0:y1 + 1, x] = True
    def h(s, yc, x0, x1, inside=+1):
        for k, val in enumerate(PROFILE):
            y = yc + (k - HALF) * inside
            s.V[y, x0:x1 + 1] = np.minimum(s.V[y, x0:x1 + 1], val); s.F[y, x0:x1 + 1] = True
    def apply(s, A):
        A[s.F] = s.V[s.F][:, None]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('out')
    ap.add_argument('--panels', required=True)
    ap.add_argument('--crops', default='')
    ap.add_argument('--layout', default='')
    ap.add_argument('--boxes', default='')
    a = ap.parse_args()
    L = dict(DEF)
    if a.layout:
        L.update(json.load(open(a.layout)))
    B = np.asarray(Image.open(a.base).convert('RGB')).astype(float)
    H, W, _ = B.shape
    A = B.copy()
    mrc, plc, orc = L['main_right_core'], L['panel_left_core'], L['outer_right_core']
    ot, ob = L['outer_top_core'], L['outer_bot_core']
    px0, px1 = L['panel_x']
    # 큰 장면 오른쪽 선 바깥(오른쪽)을 그림 끝까지 종이로
    A[:, mrc + 1:W] = PAPER
    ln = Lines(H, W)
    # 큰 장면: 위·아래 테두리를 오른쪽 선까지 다시 긋고(지운 몫) 오른쪽 선
    ln.h(ot, mrc - 12, mrc, inside=+1)
    ln.h(ob, mrc - 12, mrc, inside=-1)
    ln.v(mrc, ot, ob, inside=-1)
    boxes = []
    paths = a.panels.split(',')
    crops = a.crops.split(';') if a.crops else [''] * len(paths)
    for i, p in enumerate(paths):
        tc, bc = L['panel_cores_y'][i]
        y0, y1 = tc + 2, bc - 2
        if i == len(paths) - 1:
            y1 = bc - 2
        tw, th = px1 - px0 + 1, y1 - y0 + 1
        im = Image.open(p).convert('RGB')
        if crops[i]:
            im = im.crop(tuple(int(v) for v in crops[i].split(',')))
        else:
            r = tw / th
            if im.width / im.height > r:
                nw = round(im.height * r); x = (im.width - nw) // 2
                im = im.crop((x, 0, x + nw, im.height))
            else:
                nh = round(im.width / r); y = (im.height - nh) // 2
                im = im.crop((0, y, im.width, y + nh))
        im = im.resize((tw, th), Image.LANCZOS)
        A[y0:y1 + 1, px0:px1 + 1] = np.asarray(im).astype(float)
        boxes.append([px0, y0, px1, y1])
        ln.h(tc, plc, orc, inside=+1)
        ln.h(bc, plc, orc, inside=-1)
        ln.v(plc, tc, bc, inside=+1)
        ln.v(orc, tc, bc, inside=-1)
    ln.apply(A)
    Image.fromarray(np.clip(A, 0, 255).astype('uint8')).save(a.out)
    if a.boxes:
        json.dump({'panel_boxes': boxes, 'main_right_core': mrc}, open(a.boxes, 'w'))
    print(json.dumps({'panel_boxes': boxes, 'sizes': [[b[2] - b[0] + 1, b[3] - b[1] + 1] for b in boxes]}))

if __name__ == '__main__':
    main()
