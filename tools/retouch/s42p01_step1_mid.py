import cv2, numpy as np
from PIL import Image
src='/mnt/user-data/uploads/Downloads/s42p01_v5_1790603811156.png'
a=cv2.imread(src); out=a.copy().astype(np.float32)
hsv=cv2.cvtColor(a,cv2.COLOR_BGR2HSV).astype(int); H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(int)
tan=(H>=8)&(H<=24)&(S>=35)&(V>=90)&(V<=230)
dark=g<110
floorlike=(S<45)&(V>=170)
erase_boxes={
 'mid_red_R':(467,354,481,372),'mid_teal_L':(554,356,566,373),'mid_red2_R':(627,408,640,426),'mid_grey_R':(509,450,524,470),
 'rl_k1_L':(734,449,748,467),'rl_k2_L':(763,438,777,459),'rl_k3_R':(815,449,829,467),'rl_k4_R':(903,450,915,468),'rl_k6_R':(957,447,972,466),
}
keep={}
for k,(x0,y0,x1,y1) in erase_boxes.items():
    sub=tan[y0:y1,x0:x1].astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(sub,8)
    kk=1+int(np.argmax(st[1:,cv2.CC_STAT_AREA])); core=(lab==kk).astype(np.uint8)
    core=cv2.morphologyEx(core,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    ring=cv2.dilate(core,np.ones((5,5),np.uint8))
    m=(core | (ring & dark[y0:y1,x0:x1].astype(np.uint8)))
    m=cv2.dilate(m,np.ones((3,3),np.uint8))
    keep[k]=(m.astype(bool),(x0,y0,x1,y1))
    # background colour: floor-like pixels in an enlarged box, not in mask
    X0,Y0,X1,Y1=x0-6,y0-4,x1+6,y1+4
    big=np.zeros((Y1-Y0,X1-X0),bool); big[y0-Y0:y1-Y0,x0-X0:x1-X0]=m.astype(bool)
    fl=floorlike[Y0:Y1,X0:X1]&(~big)
    col=np.median(a[Y0:Y1,X0:X1][fl].reshape(-1,3),axis=0) if fl.sum()>10 else np.array([210,225,235])
    # vertical gradient: use per-row median where available
    fill=np.zeros((y1-y0,x1-x0,3),np.float32)
    for r in range(y1-y0):
        yy=y0+r; rowmask=floorlike[yy,X0:X1]&(~big[yy-Y0])
        fill[r]=np.median(a[yy,X0:X1][rowmask],axis=0) if rowmask.sum()>=3 else col
    f=cv2.GaussianBlur(m.astype(np.float32),(3,3),0)[...,None]
    out[y0:y1,x0:x1]=out[y0:y1,x0:x1]*(1-f)+fill*f
    print(k,int(m.sum()),col.astype(int).tolist())
out=np.clip(out,0,255).astype(np.uint8)
# move sack sprite to walking kid
m,(x0,y0,x1,y1)=keep['mid_grey_R']
spr=a[y0:y1,x0:x1].copy(); tanspr=tan[y0:y1,x0:x1]
spm=m & cv2.dilate(tanspr.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
dx,dy=47,-9
roi=out[y0+dy:y1+dy,x0+dx:x1+dx].astype(np.float32)
f=cv2.GaussianBlur(spm.astype(np.float32),(3,3),0)[...,None]
out[y0+dy:y1+dy,x0+dx:x1+dx]=(roi*(1-f)+spr.astype(np.float32)*f).astype(np.uint8)
cv2.imwrite('s42p01_rt.png',out)
I=Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB))
I.crop((430,340,650,480)).resize((1100,700),Image.LANCZOS).save('s42rt_mid.jpg',quality=92)
I.crop((720,420,980,475)).resize((1300,275),Image.LANCZOS).save('s42rt_rlow.jpg',quality=92)
I.crop((330,250,1024,572)).save('s42rt_disp.jpg',quality=92)
