# tools/merge — GitHub main 이 다른 곳에서 앞서 나갔을 때 새 과 커밋을 그 위로 옮겨 싣기

2026-11-14: 이 작업 사본(새 과 L52a ~ L13b · 12 커밋)이 `196971e` 에서 갈라진 사이, GitHub main 에는 다른 도구가 바로 올린 11 커밋(2026-11-12 ~ 13 · 「wordless」 그림 고침 · 단원 목차 · L48c/L48d · L07a/L07e · L49a/L49b 그림 합치기 · 카드 고침 7)이 쌓였다. 번들은 얕은 clone 에서 앞 커밋을 못 찾아 `push_b2.command` 가 「prerequisite 196971e 없음」으로 멈췄다. 그래서 새 과 커밋을 GitHub main(`e3ef5f3`) 위로 **재배치(rebase)** 했다 — GitHub 쪽 커밋은 하나도 고치지 않았다.

## 언제
번들을 만들기 **전에 늘** GitHub main 을 본다(공개 저장소라 토큰 없이 읽힌다):

```sh
git -c credential.helper= fetch https://github.com/BAEggman/biology2.git +refs/heads/main:refs/remotes/gh/main
git merge-base --is-ancestor gh/main main && echo "그대로 — gh/main..main 으로 번들" || echo "갈라짐 — 아래대로"
```

## 갈라졌을 때
```sh
sh tools/merge/setup.sh                                   # 병합 드라이버 켜기(한 번)
git branch backup/pre-integrate-$(git rev-parse --short main) main
B=$(git merge-base main gh/main)
git rebase --onto gh/main $B main -x tools/merge/regen.sh # 커밋마다 생성물을 다시 만든다
#   멈추면: 대개 lessons/<ID>.json 을 두 쪽이 모두 고친 것 — 두 뜻을 다 살려 손으로 풀고 git add → git rebase --continue
node build.js --check && node test/all.js                 # 다 통과해야
git bundle create bN.bundle gh/main..main                 # 앞 커밋 = GitHub main 하나뿐 → 얕은 clone 으로도 얹힌다
```

## 드라이버
| 파일 | 드라이버 | 어떻게 |
|---|---|---|
| `index.html` | `drv_index.py` | CARDS 줄은 카드 id · 필드 단위 3-way · BUILD 줄과 「새 Sketchy 과」 배지는 HEAD 를 두고 regen 이 다시 만든다 · 나머지 줄은 `git merge-file` |
| `tools/hooks.json` | `drv_json.py` | 키 단위 3-way(indent=1 꼴 그대로) · 같은 예약 글을 두 쪽이 고쳤으면 한쪽이 덧붙이기만 했을 때에 한해 「고친 글 + 덧붙임」 |
| `test/baseline.json` | `drv_baseline.py` | 줄 단위 · 부딪친 한 줄 사전(예: `"cardEdits"`)은 키 단위로 합친다 |
| `lesson/*.html` · `lesson/map.js` · `links_report.md` | `true` | 생성물 — HEAD 를 두고 `regen.sh` 가 다시 만든다 |
