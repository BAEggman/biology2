# split.py <tag> — (기기) raw/<tag>/list.txt 의 MP3 를 3.4MB 이하 ZIP 여럿(rv_<tag>_N.zip)으로 묶는다(zip 명령은 지우기 권한 없이 실패 — zipfile 로).
import zipfile,sys,os
T=sys.argv[1];R=os.path.expanduser(f'~/mnt/Downloads/b2audio/raw/{T}')
ps=open(f'{R}/list.txt').read().split();g=[];c=[];s=0
for p in ps:
  z=os.path.getsize(p)
  if c and s+z>3.4e6: g.append(c);c=[];s=0
  c.append(p);s+=z
g.append(c)
for i,c in enumerate(g):
  with zipfile.ZipFile(f'{R}/rv_{T}_{i}.zip','w') as Z:
    for p in c: Z.write(p,os.path.basename(p))
  print(f'/Users/mac/Downloads/b2audio/raw/{T}/rv_{T}_{i}.zip',len(c))
