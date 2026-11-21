import json,sys,os
import os;P=os.environ.get('DEC','/tmp/work/decisions.json')
D=json.load(open(P)) if os.path.exists(P) else {}
# usage: dec.py id status review [notes]
i,st,rv=sys.argv[1:4]; nt=sys.argv[4] if len(sys.argv)>4 else None
D[i]={'status':st,'review':rv,**({'notes':nt} if nt else {})}
json.dump(D,open(P,'w'),ensure_ascii=False,indent=1); print(len(D))
