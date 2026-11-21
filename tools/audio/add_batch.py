#!/usr/bin/env python3
"""add_batch.py — 검수를 통과한 녹음을 manifest 에 더하고 검수 기록을 쓴다.

  python3 tools/audio/add_batch.py <spec.json> [--check]

spec.json:
  {"batch": "20261121-batch-04", "hashes": "<경로: '이름 wav_sha mp3_sha 길이' 줄들>",
   "accepted": [{"id": "L20f_s1_v2", "review": "...", "notes": "..."}, ...],
   "rejected_attempts": [...], "reviews": {...}, "extra": {...}}

· 구간은 tools/audio/locked.json 에 잠겨 있어야 하고(지금 say 의 sha256 이 잠금과 같아야) 받아 적기 대조가 끝난 것만 넣는다.
· manifest 항목: src = https://baeggman.github.io/biology2-audio/<과>_<sid>_<판>.mp3 · text = say · status ready · sha256 = mp3.
· 검수 기록: lesson/audio/reviews/<batch>.json (human_listening 은 늘 false — 사람이 들은 것은 heard.json 에만 적는다).
"""
import json, sys, hashlib, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
spec = json.load(open(sys.argv[1])); check = '--check' in sys.argv
H = {}
for line in open(P(spec['hashes'])):
    p = line.split()
    if len(p) >= 4: H[p[0]] = dict(wav=p[1], mp3=p[2], dur=float(p[3]))
locked = json.load(open(P('tools/audio/locked.json')))
man = json.load(open(P('lesson/audio/manifest.json')))
head = subprocess.check_output(['git', '-C', ROOT, 'rev-parse', 'HEAD']).decode().strip()
sha = lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()
norm = "const T=require(%r);const lex=require(%r);const ord=require(%r)();" % (P('tools/tts_norm.js'), P('tools/tts_lexicon.json'), P('tools/tts_order.js'))
acc, bad = [], []
for a in spec['accepted']:
    L, sid, ver = a['id'].split('_')
    say = next(s['say'] for s in json.load(open(P('lessons', L + '.json')))['stops'] if s['sid'] == sid)
    lk = locked['잠김'].get(L, {}).get('구간', {}).get(sid)
    if lk is None or not sha(say).startswith(lk): bad.append(f'{a["id"]}: 잠김 아님 또는 글이 바뀜'); continue
    if a['id'] not in H: bad.append(f'{a["id"]}: 해시 없음'); continue
    spoken = subprocess.check_output(['node', '-e', norm + 'process.stdout.write(T.ttsNorm(process.argv[1],lex,ord,process.argv[2]))', say, L]).decode()
    h = H[a['id']]
    acc.append(dict(lesson_id=L, sid=sid, version=ver, source_commit=head, say_sha256=sha(say), spoken_sha256=sha(spoken),
                    wav_sha256=h['wav'], mp3_sha256=h['mp3'], duration_sec=h['dur'],
                    content_check=a.get('content_check', 'blind transcript compared with spoken script (spaces/punctuation ignored); every difference resolved by must-hear re-check'),
                    audio_review='independent Gemini task-mode conversation, MP3 given without script (multimodal audio input, not ASR)',
                    review_independent=True, human_listening=False, pronunciation_status=a.get('status', 'CLEAR'),
                    structural_decode_pass=True, review=a.get('review', ''), notes=a.get('notes', '')))
    e = dict(src=f'https://baeggman.github.io/biology2-audio/{L}_{sid}_{ver}.mp3', text=say, status='ready', sha256=h['mp3'])
    man['lessons'].setdefault(L, {})[sid] = e
if bad: print('\n'.join(bad)); sys.exit(1)
rec = dict(batch=spec['batch'], status='accepted_for_integration', date=spec.get('date', ''), by=spec.get('by', ''),
           clips=len(acc), accepted=acc, rejected_attempts=spec.get('rejected_attempts', []), reviews=spec.get('reviews', {}),
           acceptance_policy='뜻이 통하는 가벼운 발음 흔들림은 수용 · 누락/뜻 뒤집힘/수 · 방향 · 부정의 잘못은 다시(사용자 기준)',
           method_limit='AI 검수(따로 연 Gemini 대화가 MP3 를 원문 없이 받아 적고, 다른 곳은 A/B 필청으로 다시 확인). 사람이 듣지 않았다 — human_listening false.',
           **spec.get('extra', {}))
print(f'accepted {len(acc)} · manifest {sum(len(v) for v in man["lessons"].values())} 항목')
if not check:
    man['updated'] = spec.get('date', man.get('updated'))
    json.dump(man, open(P('lesson/audio/manifest.json'), 'w'), ensure_ascii=False, indent=2); open(P('lesson/audio/manifest.json'), 'a').write('\n')
    json.dump(rec, open(P('lesson/audio/reviews', spec['batch'] + '.json'), 'w'), ensure_ascii=False, indent=2); open(P('lesson/audio/reviews', spec['batch'] + '.json'), 'a').write('\n')
