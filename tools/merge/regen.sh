#!/bin/sh
# regen.sh — `git rebase … -x tools/merge/regen.sh` 로 쓴다: 방금 옮겨 실은 커밋마다 생성물을 다시 만들어 그 커밋에 덧붙인다.
#   생성물 = lesson/*.html · lesson/index.html · lesson/map.js · lesson/symbols.html(build_lesson.js) · index.html 의 BUILD 칸 · links_report.md(build.js)
set -e
L="${TMPDIR:-/tmp}/b2_regen.log"
echo "=== $(git log -1 --format='%h %s' | cut -c1-60)" >> "$L"
node tools/build_lesson.js > "$L.bl" 2>&1 || { echo "build_lesson 실패" >> "$L"; tail -20 "$L.bl" >> "$L"; exit 1; }
grep -E "^lesson/|index.html" "$L.bl" >> "$L" || true
node build.js > "$L.bj" 2>&1 || { echo "build.js 실패" >> "$L"; tail -20 "$L.bj" >> "$L"; exit 1; }
git add -A
if git diff --cached --quiet; then echo "(다시 만든 것 바뀜 없음)" >> "$L"; else git diff --cached --stat | tail -1 >> "$L"; git commit --amend --no-edit -q --no-verify; fi
