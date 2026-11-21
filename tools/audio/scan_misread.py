# scan_misread.py <tts JSON> — 오독기록.json 의 낱말 · 꼴을 대본에서 찾아 구간마다 사전 줄을 낸다(stdout JSON {L_sid:[hint...]}).
import json,re,sys,os
H=os.path.dirname(os.path.abspath(__file__))
rec=json.load(open(f'{H}/오독기록.json'));T=json.load(open(sys.argv[1]));out={};notes={}
for k,v in T.items():
  t=v['t'];hs=[w['hint'] for w in rec['words'] if w['w'] in t]
  for p in rec['patterns']:
    if re.search(p['re'],t):
      if p['hint']: hs.append(p['hint'])
      notes.setdefault(k,[]).append(p['why'])
  if hs: out[k]=sorted(set(hs))
print(json.dumps({'hints':out,'notes':notes},ensure_ascii=False,indent=1))
