#!/bin/sh
# setup.sh — 병합 도구를 이 저장소에 켠다(.git/config 의 merge 드라이버 + .git/info/attributes). 커밋되지 않는 설정이라 새로 받은 저장소마다 한 번.
set -e
R="$(git rev-parse --show-toplevel)"; D="$R/tools/merge"
git config merge.b2index.name "b2 index.html (CARDS 카드 단위)";      git config merge.b2index.driver "python3 $D/drv_index.py %O %A %B"
git config merge.b2json.name "b2 hooks.json (키 단위)";               git config merge.b2json.driver "python3 $D/drv_json.py %O %A %B"
git config merge.b2baseline.name "b2 baseline.json (한 줄 사전)";     git config merge.b2baseline.driver "python3 $D/drv_baseline.py %O %A %B"
git config merge.b2keep.name "b2 생성물 — HEAD 를 두고 다시 만든다"; git config merge.b2keep.driver "true"
mkdir -p "$R/.git/info"
cat > "$R/.git/info/attributes" <<'ATTR'
index.html merge=b2index
tools/hooks.json merge=b2json
test/baseline.json merge=b2baseline
lesson/*.html merge=b2keep
lesson/map.js merge=b2keep
links_report.md merge=b2keep
ATTR
echo "병합 도구 켬 — $(git check-attr merge index.html tools/hooks.json | tr '\n' ' ')"
