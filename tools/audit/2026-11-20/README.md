# tools/audit/2026-11-20 — 인계문(그림–대본 전수 감사 246건)의 작업 대장

2026-11-20 · Fable 5.2 가 뼈대를 만들었고 Opus 5.5 세션이 채운다. 무엇을 어떤 차례로 하는지는 `tools/plan/2026-11-20/지시서_Opus_인계문실행.md`.

## 여기 있는 것
| 파일 | 무엇 | 누가 고치나 |
|---|---|---|
| `issues.json` | **대장** — 한 줄에 한 항목(250줄 = 감사 246 + 사용자가 11-19 에 짚었는데 감사에 없는 `N-` 4) | Opus 가 칸을 채운다 |
| `lessons.json` | 과 142의 감사 판정(hold = 녹음 보류 · cond = 조건부 통과) · 감사 때의 그림 blob · 항목 ID | 연장이 만든다(손대지 않는다) |
| `repaired44.json` | 11-20 에 다른 도구가 복구한 44 구간의 「복구 뒤」 글귀 — 되돌아가면 안 되는 목록(`test/verify_saytext.js` 가 읽게 한다) | 그대로 둔다. 과학 고침으로 그 문장 자체가 바뀌면 그 줄을 새 글귀로 고치고 까닭을 커밋에 적는다 |
| `convloss.json` | 반말 변환(27ee5d1) 앞뒤를 견준 거친 체 — 부정 표현 수가 준 구간 219 · 15 % 넘게 짧아진 구간 38. **후보일 뿐**(대부분은 바꿔 말하기) | 0단계에서 다 읽고, 뜻이 빠진 것만 `N-` 항목으로 대장에 올린다 |
| `parse_handoff.py` | 인계문을 읽어 뼈대를 만들고 지금 저장소와 다시 맞춰 보는 연장 | — |
| `승급/<과>.md` | 과를 `content_verified` 로 올릴 때의 증거 한 쪽(지시서 §5) | Opus 가 만든다 |
| `보류_보고.md` | 떨어진 글 · 그림 · 음성과 그 이유(지시서 §8) | 세션마다 다시 만든다 |

## 대장의 칸
- 인계문에서 온 칸(연장이 다시 채운다): `id` · `lesson` · `sids` · `sev`(critical 최우선 · major 중요 · minor 경미 · resolved_lang 언어 복구로 해결 · user 사용자 지적) · `kind`(감사의 꼬리표) · `cat`(갈래 어림) · `quote`(감사가 인용한 글귀가 지금 그 구간에 있는가 — found · partial · elsewhere · not_found · n/a) · `line`(인계문의 줄 번호 — 원문을 찾아갈 때).
- 첫 짐작(Fable 5.2 가 감사의 글만 읽고 달았다 — **그림을 열어 본 것이 아니다**): `fix0` · `grp` · `note0`.
  | `fix0` | 뜻 |
  |---|---|
  | 글 | 글만 고치면 닫힌다 |
  | 글→그림 | 글로 먼저 · 독자 검사에서 안 닫히면 그림 |
  | 글+그림 | 그림도 고쳐야 닫힌다 |
  | 그림 | 구역 고침(수 · 방향 · 자리 · 크기 · 이음매) |
  | 그림+6+1 | 새 고리 · 새 사건 — `tools/cue/README.md` 의 6+1 |
  | 유지? | 지금 고리로 충분한지 심판이 정한다 |
  | 이미고침? | 인용문이 지금 글에 없다 |
  | 상자 | 보기 상자(`box`)만 맞춘다 |
  `grp` = 여러 과에 걸친 기호 묶음(지시서 §4.3 의 표) — 과보다 묶음을 먼저 정한다.
- Opus 가 채우는 칸(인계문 §3 의 칸을 우리 말로): `state` · `reproduced`(지금도 그런가 — 그림을 열어 본 날짜와 한 줄) · `scope`(확정한 범위: 글 / 그림 / 둘 다 / 유지) · `keep`(보존할 cue) · `basis`(과학 근거 — 기본서 문서 · 기출 번호 · 출처) · `fix`(우리 말로 한두 줄) · `commit` · `recheck`(재검증 결과) · `risk`(남은 위험) · `sc`(science correction 이면 true).
- `state`: `open → reproduced → proposed → changed → verified` · `already_fixed` · `rejected_with_evidence` · `blocked` · `resolved_lang`.
- 한 줄에 한 항목 꼴을 지킨다(diff 가 읽히게). 줄을 지우지 않는다.

## 연장 쓰는 법
```bash
# 인계문은 저장소 밖에 둔다(사용자 컴퓨터 ~/Downloads/biology_claude_handoff_full_20261120.md · 프로젝트 문서 claude/인계문_2026-11-20_전문.md)
python3 tools/audit/2026-11-20/parse_handoff.py <인계문.md>                    # 세어 보기만: 수 · 인용문 대조 · 그림 blob
python3 tools/audit/2026-11-20/parse_handoff.py <인계문.md> --write            # 대장의 인계문 칸만 새로 고침(손으로 채운 칸 · N- 줄은 그대로)
python3 tools/audit/2026-11-20/parse_handoff.py <인계문.md> --full <밖의 경로>  # 원문 칸까지 든 작업용 JSON 을 저장소 밖에
```
- 2026-11-20 에 돌린 결과: 과 142(hold 86 · cond 56) · 항목 246(critical 8 · major 121 · minor 87 · resolved_lang 30) · 미해결 216의 인용문 — found 211 · partial 2(L13a-03 · L37a-01) · not_found 2(L54a-04 · L54c-04) · n/a 1 · 그림 blob 142 / 142 같음.
- 글을 고친 뒤 `--write` 로 돌리면 `quote` 가 `found` 에서 `not_found` 로 바뀐다 — 고쳐졌다는 표시의 하나일 뿐, `verified` 의 근거는 아니다.

## 여기 넣지 않는 것
- **인계문과 감사 원문의 글**(현재 표현 · 그림 관찰 · 판단 · 수정안 · 근거를 베낀 것). 공개 저장소다 — 대장에는 우리 말로 줄인 것만 적는다.
- 사용자의 계정 이름 · 메일 · Gemini 대화 주소 · 토큰.
