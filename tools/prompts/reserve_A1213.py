#!/usr/bin/env python3
# reserve_A1213.py — 12장 덧붙임(2026-11-15 · Opus 5.5)의 새 물건 예약 + 이어 쓰는 물건에 쪽지.
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
B = '[2026-11-15 12장 덧붙임]'
new = {
 '유리 배양 접시에 한 겹으로 빽빽이 맞닿아 가만한 크림색 덩이(빈틈 곁 하나만 갈라짐) + 그 위에 올라타 쌓인 잿빛 덩이': f'밀도 의존성 억제(접촉 저해 · 캐드헤린) — 암세포는 잃음 전용 {B} — L19a s13. 덩이 = 세포(L19a 의 약속) · 잿빛 덩이 = 암세포(이 과에서만 — 덱 전체의 암은 【작은 검은 게】). 캐드헤린은 물건 없이 말로만(맞닿음을 알리는 세포 연접 단백질).',
 '덩이 밑의 작은 검은 갈고리 발(접시 바닥을 쥠) / 갈고리 발 없이 맨바닥에 홀로 가만한 덩이 · 발 없이도 갈라지는 잿빛 덩이': f'발판 의존성 — 바닥(세포외기질)에 붙어야 분열 · 갈고리 발 = 인테그린 · 암세포는 잃음 전용 {B} — L19a s14. ⚠ 갈고리가 가늘어 1× 에선 잘 안 보인다(일치 검사 1회 — 「벌레 다리 · 바늘땀」으로도).',
 '낮은 나무 말뚝 울 안에 가만히 모인 작은 검은 게 무리 / 제 울을 쓰러뜨리고 쏟아져 나와 붉은 호스 끝을 끌어온 게 무리 · 호스 위에 올라탄 게 하나': f'양성종양(국소에 머묾) / 악성종양(침윤) · 혈관 신생(혈관을 끌어옴) · 전이(혈관을 타고 퍼짐) 전용 {B} — L19d s14. 말뚝 울 = 조직의 경계 · 붉은 호스 = 혈관(【진홍 호스】 문법).',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
def add(key, note):
    v = R[key]; assert isinstance(v, str), key
    R[key] = v + ' ' + note
add('작은 검은 게', f'★ {B} L19d s14 음반 더미 오른쪽 마루 — 말뚝 울 안에 머문 무리(양성) · 울을 쓰러뜨린 무리(악성 · 침윤)가 붉은 호스를 끌어옴(혈관 신생) · 호스 위에 올라탄 하나(전이).')
out = json.dumps(d, ensure_ascii=False, indent=1)
assert json.loads(out) == d
open(P, 'w', encoding='utf-8').write(out)
print('예약', len(R))
