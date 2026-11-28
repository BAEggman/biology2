#!/usr/bin/env python3
# pil_s13edge.py <in.png> <out.png> <바탕 커밋> — Z3(피디)의 허용 상자를 큐시트 모서리 때문에 x 1505 까지 넓혔으므로,
# 그 띠 가운데 큐시트 아래(x 1478 ~ 1512 · y 858 ~ 1048 — s13 녹음 상자의 빈 좌석 가장자리)를 바탕 그림으로 되돌린다.
import io, os, subprocess, sys
import numpy as np
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
raw = subprocess.run(['git', 'show', f'{sys.argv[3]}:lesson/img/L15a.webp'], cwd=ROOT, capture_output=True, check=True).stdout
a = np.array(Image.open(io.BytesIO(raw)).convert('RGB')); b = np.array(Image.open(sys.argv[1]).convert('RGB'))
b[858:1048, 1478:1512] = a[858:1048, 1478:1512]
Image.fromarray(b).save(sys.argv[2])
