#!/usr/bin/env python3
# reserve_A45.py — 45장 덧붙임 L04d +2(곤충 변태 호르몬)
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
T = '[2026-11-11 45장 덧붙임 L04d]'
new = {
 '공갈 젖꼭지': f'유충호르몬(JH · 아기로 붙잡아 둠) 전용 {T} — L04d s12 애벌레 갑옷이 투구 앞에 문 젖꼭지(높으면 탈피해도 유충) · 고치 아래 판자 턱에 뱉어 놓은 젖꼭지(낮아지면 번데기 → 성충). ⚠ 다른 판의 아기(L46f 요람 · L46g 기저귀 · L51a 횃불 · L07f 크레용 · L32b 갈색 담요)에 젖꼭지를 물리지 마라.',
 '벽 못에 매달린 하얀 실 고치(꼭대기로 더듬이 끝 둘)': f'번데기(변태 단계) 전용 {T} — L04d s12. 성충은 같은 판 진열장 곤충 칸 갑옷. ⚠ 나비는 【뱃전 난간의 큰 나비】(파필로마) 예약이라 성충을 나비로 그리지 않았다.',
 '애벌레 갑옷의 투구 → 검은 전선 → 금빛 고리 넷 상자 · 등 뒤의 회색 빈 허물': f'곤충 탈피의 호르몬 길(뇌 PTTH → 전흉선 → 엑디스테로이드 → 탈피) 전용 {T} — L04d s11. 상자 = 앞가슴샘(전흉선) · 문장 = 스테로이드 · 허물 = 탈피(L04b#11 「머리 위로 제 껍질을 벗는 사람」 = 탈피동물과 같은 뜻).',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
def add(key, note):
    v = R[key]; assert isinstance(v, str), key
    R[key] = v + ' ' + note
add('검은 전선', f'★ {T} L04d s11 애벌레 투구(뇌)에서 가슴 상자(전흉선)로 꽂힌 굵은 검은 전선 = 신경분비 호르몬 PTTH(L07a 후엽 전선과 같은 문법 — 신경이 내는 호르몬).')
add('금빛 고리 넷 덩이(육각 셋 + 오각 하나가 붙은 한 덩이)', f'★ {T} L04d s11 애벌레 가슴 상자 앞면 문장 = 엑디스테로이드(PIL grub_pil.py 로 그림).')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('예약', len(R))
