import numpy as np, cv2
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
im=cv2.imread(SP+'/L36b/r1/final_v1.png')
out=im.copy()
Y0,Y1=719,782
X0,X1=1100,1240
def line_x(y): # black outline left edge in lower segment (measured)
    return 1143+(y-720)*0.58
H=Y1-Y0
mapx=np.tile(np.arange(X0,X1,dtype=np.float32),(H,1))
mapy=np.tile(np.arange(Y0,Y1,dtype=np.float32)[:,None],(1,X1-X0))
for i,y in enumerate(range(Y0,Y1)):
    t=min(1,max(0,(y-720)/(778-720)))
    s=12.0*(1-t)*(1-t*0.0)
    if y<720: s=0
    x0=line_x(y)+ s  # where line lands after shift
    xs=np.arange(X0,X1,dtype=np.float32)
    # weight: 1 around line, ramps to 0
    w=np.interp(xs,[x0-30,x0-8,x0+14,x0+48],[0,1,1,0])
    mapx[i]=xs-s*w
mapy=mapy.astype(np.float32)
patch=cv2.remap(im,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
# rows 720+ replaced
out[Y0:Y1,X0:X1]=patch
# seam rows 719-721: interpolate between rows 718 and 722 (removes the white blip)
for yy in (719,720,721):
    t=(yy-718)/4.0
    out[yy,X0:X1]=((1-t)*out[718,X0:X1].astype(np.float32)+t*out[722,X0:X1].astype(np.float32)).astype(np.uint8)
cv2.imwrite(SP+'/picfix/L36b/final_new.png',out)
