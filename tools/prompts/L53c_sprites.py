#!/usr/bin/env python3
# sprites.py — 그림에서 물건 하나를 알파 스프라이트로 떼어 낸다(평평한 물빛 바탕 위의 물건).
import cv2, numpy as np
from PIL import Image
INK = (22, 20, 18)
def cut(path, bbox, bg, pad=4, thr=60):
    im = cv2.imread(path)[..., ::-1].astype(int); x, y, w, h = bbox
    x0, y0, x1, y1 = x - pad, y - pad, x + w + pad, y + h + pad
    reg = im[y0:y1, x0:x1]; m = (np.abs(reg - np.array(bg)).sum(axis=2) > thr).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8); k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); m = (lab == k).astype(np.uint8)
    cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); full = np.zeros_like(m); cv2.drawContours(full, cnt, -1, 1, -1)     # 구멍 메움
    inner = cv2.erode(full, np.ones((3, 3), np.uint8), iterations=1)
    rgb = reg.copy().astype(np.uint8); rgb[(full > 0) & (inner == 0)] = INK                                            # 가장자리 한 겹은 먹빛(바탕 물빛 번짐 제거)
    alpha = cv2.GaussianBlur((full * 255).astype(np.uint8), (0, 0), 0.6)
    return Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), 'RGBA')
if __name__ == '__main__':
    SP = '/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'; B = f'{SP}/L53c/r1/base.png'; O = f'{SP}/L53c/spr'
    UP, DEEP, UPb = (117, 187, 231), (40, 111, 187), (117, 187, 233)
    cut(f'{SP}/L53b/r1/final.png', (1884, 135, 44, 49), UPb).save(f'{O}/sack.png')
    cut(B, (420, 807, 20, 79), DEEP).save(f'{O}/knife.png')
    cut(B, (1152, 114, 54, 34), UP).save(f'{O}/lemon.png')
    cut(B, (1263, 904, 45, 45), DEEP).save(f'{O}/bsack.png')
    cut(B, (1688, 941, 33, 24), DEEP).save(f'{O}/pebble.png')
    cut(B, (1439, 147, 36, 37), UP).save(f'{O}/grape.png')
    cut(B, (523, 830, 30, 43), DEEP).save(f'{O}/coin.png')
    names = ['sack', 'knife', 'lemon', 'bsack', 'pebble', 'grape', 'coin']
    sh = Image.new('RGB', (760, 200), (200, 120, 200)); x = 10
    for nme in names:
        s = Image.open(f'{O}/{nme}.png'); print(nme, s.size); s2 = s.resize((s.width * 2, s.height * 2), Image.LANCZOS); sh.paste(s2, (x, 10), s2); x += s2.width + 16
    sh.save(f'{O}/sheet.png')
