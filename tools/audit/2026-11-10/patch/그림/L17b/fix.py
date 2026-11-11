import numpy as np, cv2
from PIL import Image
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
a=Image.open(SP+'/L17b/r1/final_v1.png').convert('RGB')
A=np.array(a)
X0,X1,Y0,Y1=1130,1215,684,762
sub=A[Y0:Y1,X0:X1].astype(np.int32)
floor=np.array([163,163,140])  # rough; deviation measured per-pixel against local median instead
med=np.median(sub.reshape(-1,3),axis=0)
dev=np.abs(sub-med).max(axis=2)
m=(dev>14).astype(np.uint8)
# keep only the rope component(s): the diagonal band; drop nothing else inside the window that is not near it
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
# exclude the two scuff strokes at the far left (x<1140) -> not part of the rope
m[:, :1140-X0]=0
mask=np.zeros(A.shape[:2],np.uint8); mask[Y0:Y1,X0:X1]=m
# pale specks left of the old rope end (halo)
sp=np.zeros(A.shape[:2],np.uint8)
reg=A[715:760,1128:1146].astype(int)
sp[715:760,1128:1146]=(reg.mean(axis=2)-med.mean())>12
sp=cv2.dilate(sp,np.ones((3,3),np.uint8)); sp[:, :1128]=0
mask=np.maximum(mask,sp)
out=cv2.inpaint(A,mask,6,cv2.INPAINT_TELEA)
# flat floor: remove inpaint smear by blending toward a smooth fill sampled from the ring around the mask
Image.fromarray(out).save(SP+'/picfix/L17b/final_new.png')
np.save(SP+'/picfix/L17b/tmp_mask.npy',mask)
