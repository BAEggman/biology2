# 검증 스위트

```bash
npm i jsdom          # 유일한 의존성
node test/all.js     # 전체
node test/verify_build.js   # 하나만
```

**전체 히스토리가 필요하다.** 비교 기준본을 과거 커밋에서 꺼내 쓴다.
`--depth 1` 로 클론했으면 먼저 `git fetch --unshallow`.

| 파일 | 무엇을 지키나 |
|---|---|
| `verify_links.js` | PMAP에 죽은 참조가 없다 · PTIT 106패널 전수 · 카드ID 실재 |
| `verify_picfix.js` | 복구 화면 구조 · 이미지 95개 · CARDS·EXAM·localStorage 키 무변경 |
| `verify_build.js` | 빌드 재현성 · **일부러 망가뜨렸을 때 죽는지** · 리포트 정합 |
| `smoke_links.js` | 앱을 띄워 실제로 채점하며 링크가 살아있는지 |
| `smoke_picfix.js` | 세션을 돌려 오답 시 뜨고 정답 시 안 뜨는지 |
| `migrate_safe.js` | 실사용 DB(2166장)를 새 버전으로 열어 진도가 보존되는지 |

기준본은 하드코딩하지 않는다. `_lib.js`가 git 로그에서 **내용으로** 찾는다
(v9 딥링크 블록은 있고 picFix는 없는 커밋 = v12). 리베이스해도 안 깨진다.

`_migrate4_once.py`는 스키마 이관을 한 번 돌린 기록이다. 다시 돌리면 안 된다.

## 검증이 못 잡는 것

그림이 사실과 맞는지는 기계가 판정 못 한다. 사실표 대조는 여전히 사람이 한다
(마스터노트 §10). 여기 있는 것은 **구조가 어긋나지 않았다**는 보장까지다.
