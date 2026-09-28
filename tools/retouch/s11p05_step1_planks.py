import cv2, numpy as np
from PIL import Image
src='/mnt/user-data/uploads/Downloads/s11p05_v3_1789807065018.png'
a=cv2.imread(src); out=a.copy()
L={1:101,2:169,3:237,4:306,5:374,6:441,7:510,8:579,9:647,10:717,11:786,12:855}
R={1:144,2:212,3:281,4:349,5:417,6:486,7:554,8:622,9:691,10:760,11:830,12:899}
TR={'top':(118,362),'mid':(392,628),'bot':(672,910)}
def copy(track,src_k,dst_k,m=8):
    y0,y1=TR[track]
    x0,x1=L[src_k]-m,R[src_k]+m
    dx=L[dst_k]-L[src_k]
    out[y0:y1,x0+dx:x1+dx]=a[y0:y1,x0:x1]
    print(track,src_k,'->',dst_k,'dx',dx)
copy('bot',3,4); copy('bot',2,5); copy('bot',8,10); copy('mid',8,6)
cv2.imwrite('s11p05_step1.png',out)
Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB)).resize((768,768),Image.LANCZOS).save('s11p05_step1.jpg',quality=90)
