# sheets.py — 과마다 감사용 그림 셋: A(깨끗한 전체) · B(상자 번호를 그린 전체) · C(상자대로 자른 조각 모음)
import json,glob,os,sys,math
from PIL import Image,ImageDraw,ImageFont
OUT=sys.argv[1]; ONLY=sys.argv[2:] 
F=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',s)
COL=[(255,221,0),(0,229,255),(255,105,180),(124,252,0),(255,140,0),(186,130,255)]
def boxes(s):
    b=s.get('box')
    if not b: return []
    return b if isinstance(b[0],list) else [b]
for f in sorted(glob.glob('/tmp/b2/lessons/L*.json')):
    d=json.load(open(f)); i=d['id']
    if ONLY and i not in ONLY: continue
    im=Image.open(f'/tmp/b2/lesson/img/{i}.webp').convert('RGB'); W,H=im.size
    assert (W,H)==(d['w'],d['h']),(i,W,H)
    sc=1536/W
    A=im.resize((1536,round(H*sc)),Image.LANCZOS); A.save(f'{OUT}/img/{i}_A.jpg',quality=88)
    B=A.copy(); dr=ImageDraw.Draw(B); cells=[]; txt=[f'# {i} — {d["title"]}', f'요약: {d.get("sub","")}', '']
    for k,s in enumerate(d['stops']):
        bs=boxes(s); labs=[]
        for j,(x,y,w,h) in enumerate(bs):
            lab=str(k) if len(bs)==1 else f'{k}{chr(97+j)}'; labs.append(lab)
            c=COL[k%len(COL)]
            x0,y0,x1,y1=[round(v*sc) for v in (x,y,x+w,y+h)]
            x1=min(x1,B.width-1); y1=min(y1,B.height-1)
            dr.rectangle([x0,y0,x1,y1],outline=(0,0,0),width=5); dr.rectangle([x0+1,y0+1,x1-1,y1-1],outline=c,width=3)
            fn=F(22); tw=dr.textlength(lab,font=fn); tx=min(max(x0+4,2),B.width-tw-8); ty=y0+4 if y0+30<B.height else y0-28
            dr.rectangle([tx-3,ty-1,tx+tw+3,ty+25],fill=(0,0,0)); dr.text((tx,ty),lab,font=fn,fill=c)
            cells.append((lab,im.crop((max(0,x),max(0,y),min(W,x+w),min(H,y+h)))))
        txt.append(f'## 정거장 {k}  (상자: {", ".join(labs) if labs else "없음 — 전체 그림"})')
        txt.append(f'물건: {s["obj"]}'); txt.append(f'고리: {s["hook"]}'); txt.append(f'말: {s["say"]}'); txt.append('')
    B.save(f'{OUT}/img/{i}_B.jpg',quality=88)
    # C: 조각 모음 — 4열, 칸 384×300(위 26px 는 이름표)
    CW,CH,CAP,NC=384,300,26,4; per=16; parts=[cells[a:a+per] for a in range(0,len(cells),per)] or [[]]
    names=[]
    for pi,part in enumerate(parts):
        rows=max(1,math.ceil(len(part)/NC)); S=Image.new('RGB',(CW*NC,CH*rows),(40,40,40)); ds=ImageDraw.Draw(S)
        for n,(lab,cr) in enumerate(part):
            cx,cy=(n%NC)*CW,(n//NC)*CH
            mw,mh=CW-8,CH-CAP-8; r=min(mw/cr.width,mh/cr.height,3.0)
            cr2=cr.resize((max(1,round(cr.width*r)),max(1,round(cr.height*r))),Image.LANCZOS)
            S.paste(cr2,(cx+4+(mw-cr2.width)//2,cy+CAP+4+(mh-cr2.height)//2))
            ds.rectangle([cx,cy,cx+CW-1,cy+CAP-1],fill=(0,0,0)); ds.text((cx+6,cy+1),lab,font=F(20),fill=(255,221,0))
            ds.rectangle([cx,cy,cx+CW-1,cy+CH-1],outline=(90,90,90),width=1)
        nm=f'{i}_C.jpg' if len(parts)==1 else f'{i}_C{pi+1}.jpg'; S.save(f'{OUT}/img/{nm}',quality=88); names.append(nm)
    txt.insert(2,f'그림 파일: {i}_A.jpg (깨끗한 전체) · {i}_B.jpg (상자 번호) · {" · ".join(names)} (상자대로 자른 조각)')
    open(f'{OUT}/pk/{i}_v.txt','w').write('\n'.join(txt))
print('done')
