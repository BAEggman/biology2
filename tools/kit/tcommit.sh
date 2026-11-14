#!/bin/bash
# tcommit.sh <msgfile> — 저장소에서 바뀐 것 전부를 커밋한다. 귀속 두 줄은 세션마다 다르다(모델 이름 · 세션 주소) → 환경변수로 받는다.
#   CO_AUTHOR='Claude Opus 5.5 <noreply@anthropic.com>' SESSION_URL='https://claude.ai/code/session_…' bash tools/kit/tcommit.sh /path/msg.txt
#   두 값은 그 세션의 system-reminder 「Attribution for git commits」가 주는 줄 그대로 쓴다(이 파일에 모델 이름을 박아 두지 않는다).
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
MSG="$1"; [ -f "$MSG" ] || { echo "메시지 파일이 없다: $MSG"; exit 1; }
if ! grep -q "^Claude-Session:" "$MSG"; then
  [ -n "$CO_AUTHOR" ] && [ -n "$SESSION_URL" ] || { echo "CO_AUTHOR · SESSION_URL 을 주거나, 메시지 끝에 귀속 두 줄을 직접 적어라"; exit 1; }
  printf '\nCo-Authored-By: %s\nClaude-Session: %s\n' "$CO_AUTHOR" "$SESSION_URL" >> "$MSG"
fi
git add -A
if git diff --cached | grep -qE "^\+.*github_pat_[A-Za-z0-9_]{20,}"; then git reset -q; echo "✕ 커밋에 토큰 꼴 문자열이 있다 — 멈춤(아무것도 커밋하지 않음)"; exit 1; fi
git commit -q -F "$MSG"
git log --oneline -1
