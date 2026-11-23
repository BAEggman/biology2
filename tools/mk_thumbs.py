#!/usr/bin/env python3
"""mk_thumbs.py [ID ...] — 과 목록의 썸네일을 만든다 (보기 화면 명세 §1.3).

lesson/img/<ID>.webp → 320 x 179 · WEBP 품질 72 → lesson/thumb/<ID>.webp
lesson/thumb/manifest.json = {ID: 원본 sha256 앞 12자} — 빌드(build_lesson.js)가 이것과 원본 해시를 견줘
낡았거나 없는 썸네일이 있으면 실패한다(잊지 못하게).

인자가 없으면 낡았거나 없는 것만 다시 만든다. 인자(과 번호)를 주면 그 과만 새로 만든다.
의존성: PIL(Pillow, WEBP 지원) 하나.
"""
import hashlib
import json
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IMG = os.path.join(ROOT, "lesson", "img")
OUT = os.path.join(ROOT, "lesson", "thumb")
MAN = os.path.join(OUT, "manifest.json")
W, H, Q = 320, 179, 72


def sha12(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    man = {}
    if os.path.exists(MAN):
        with open(MAN, encoding="utf-8") as f:
            man = json.load(f)
    ids = argv or sorted(n[:-5] for n in os.listdir(IMG) if n.endswith(".webp"))
    made = 0
    for i in ids:
        src = os.path.join(IMG, i + ".webp")
        if not os.path.exists(src):
            print("[%s] 원본 그림이 없다: %s" % (i, src), file=sys.stderr)
            return 1
        dst = os.path.join(OUT, i + ".webp")
        h = sha12(src)
        if not argv and man.get(i) == h and os.path.exists(dst):
            continue
        im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
        im.save(dst, "WEBP", quality=Q, method=6)
        man[i] = h
        made += 1
    # 원본이 없어진 과의 항목은 정리한다
    for k in list(man):
        if not os.path.exists(os.path.join(IMG, k + ".webp")):
            del man[k]
    with open(MAN, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(man.items())), f, ensure_ascii=False, indent=0)
        f.write("\n")
    total = sum(os.path.getsize(os.path.join(OUT, n)) for n in os.listdir(OUT) if n.endswith(".webp"))
    print("썸네일 %d개 새로 만듦 · 전체 %d개 · %.1f MB" % (made, len(man), total / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
