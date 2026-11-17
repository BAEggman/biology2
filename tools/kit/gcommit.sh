#!/bin/bash
# gcommit.sh <msgfile> — 저장소에서 바뀐 것 전부를 커밋한다(Antigravity · Gemini 용 — Claude 귀속 줄을 붙이지 않는다 · 2026-11-17).
#   토큰 꼴 문자열(github_pat_…)이 바뀐 내용에 있으면 멈추고 아무것도 커밋하지 않는다.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
MSG="$1"; [ -f "$MSG" ] || { echo "메시지 파일이 없다: $MSG"; exit 1; }
git add -A
if git diff --cached | grep -qE "^\+.*github_pat_[A-Za-z0-9_]{20,}"; then git reset -q; echo "✕ 커밋에 토큰 꼴 문자열이 있다 — 멈춤(아무것도 커밋하지 않음)"; exit 1; fi
git commit -q -F "$MSG"
git log --oneline -1
