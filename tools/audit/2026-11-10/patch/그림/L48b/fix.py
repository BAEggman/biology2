import numpy as np, cv2
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
A=np.array(Image.open(SP+'/L48b/r1/final_v1.png').convert('RGB'))
out=A.copy()
H,W=A.shape[:2]
S=4
def poly_mask(pts,box):
    x0,y0,x1,y1=box
    m=Image.new('L',(x1-x0,y1-y0),0)
    ImageDraw.Draw(m).polygon([(x-x0,y-y0) for x,y in pts],fill=255)
    return np.array(m)>0
def ellipse_mask(cx,cy,rx,ry,box,feather=1.0):
    x0,y0,x1,y1=box
    yy,xx=np.mgrid[y0:y1,x0:x1]
    d=np.sqrt(((xx+0.5-cx)/rx)**2+((yy+0.5-cy)/ry)**2)
    return np.clip((1.0-d)*min(rx,ry)/feather+0.5,0,1)
def draw_patch(base,box,fn):
    """supersample box region 4x, let fn(draw,P) paint on it, downsample, return patch"""
    x0,y0,x1,y1=box
    p=Image.fromarray(base[y0:y1,x0:x1]).resize(((x1-x0)*S,(y1-y0)*S),Image.NEAREST)
    d=ImageDraw.Draw(p)
    P=lambda pts:[((x-x0)*S,(y-y0)*S) for x,y in pts]
    fn(d,P)
    return np.array(p.resize((x1-x0,y1-y0),Image.BOX))
def thick_line(d,P,pts,w,col):
    q=P(pts)
    d.line(q,fill=col,width=int(round(w*S)),joint='curve')
    r=w*S/2
    for (x,y) in (q[0],q[-1]):
        d.ellipse([x-r,y-r,x+r,y+r],fill=col)
BLACK=(0,0,0)

# ---- knot sprite (taken from the original lower knot, wrinkles around it removed) ----
KC=(547.4,884.0); KR=(10.6,11.4)
# =====================  BOTTOM (rope + knot + tail at y 864..925)  =====================
bx=(500,600); by=(848,950)
bbox=(bx[0],by[0],bx[1],by[1])
arch_pts=[(500,874),(505,871.5),(514,866.5),(527.5,860),(538,857.6),(559,857.6),(577,860.8),(595,868),(600,870)]
ax=np.arange(bx[0],bx[1]); archy=np.interp(ax,[p[0] for p in arch_pts],[p[1] for p in arch_pts])
sub=A[by[0]:by[1],bx[0]:bx[1]].astype(int)
yy=np.arange(by[0],by[1])[:,None]
dark=((sub.sum(2)<500)&(sub[:,:,0]<205))
below_arch=yy>(archy[None,:]+5)
inbox=(yy>=864)&(yy<=925)&((yy<=915)|(ax[None,:]<537)|(ax[None,:]>569))&(ax[None,:]>=506)&(ax[None,:]<=594)
wr=dark&below_arch&inbox
# keep the knot ellipse for the sprite: build sprite source = original with wrinkles inpainted (not knot/rope)
rope_b=poly_mask([(535,864),(561,864),(561,899),(560,915.5),(541,915.5),(541,899),(535,880)],bbox)
# rows 899..915: tail narrower, polygon above is generous enough
wr_d=cv2.dilate(wr.astype(np.uint8),np.ones((5,5),np.uint8))>0
wr_only=wr_d&~poly_mask([(534,864),(562,864),(562,916),(534,916)],bbox)
clean_for_sprite=cv2.inpaint(np.ascontiguousarray(A[by[0]:by[1],bx[0]:bx[1]]),(wr_only*255).astype(np.uint8),4,cv2.INPAINT_TELEA)
sprite_full=np.zeros((H,W,3),np.uint8); sprite_full[by[0]:by[1],bx[0]:bx[1]]=clean_for_sprite
# main fill of bottom: wrinkles inpainted, then rope band replaced by row interpolation of pink on both sides
clean_b=cv2.inpaint(np.ascontiguousarray(A[by[0]:by[1],bx[0]:bx[1]]),(wr_d*255).astype(np.uint8),4,cv2.INPAINT_TELEA)
out[by[0]:by[1],bx[0]:bx[1]]=clean_b
XL,XR=533,564
for y in range(864,928):
    l=out[y,XL].astype(float); r=out[y,XR].astype(float)
    t=((np.arange(XL+1,XR)-XL)/(XR-XL))[:,None]
    out[y,XL+1:XR]=np.round(l*(1-t)+r*t).astype(np.uint8)
# tail / V-apex rows 915..927 : rebuild
apex=(553.6,915.0)
def bottom_v(d,P):
    # pink above/outside, green inside V, black V lines
    d.polygon(P([(apex[0],apex[1]-1.0),(apex[0]+26,apex[1]+22),(apex[0]-26,apex[1]+22)]),fill=tuple(int(v) for v in A[940,553]))
    thick_line(d,P,[(537.0,929.5),(553.6,915.0),(570.0,929.5)],4.0,BLACK)
# pink for rows 915..927 inside tail area first (left/right neighbours)
for y in range(915,928):
    l=out[y,536].astype(float); r=out[y,570].astype(float)
    # only fill the tail columns that are above the V lines
    pass
# paint pink background to the tail cols above the V, then draw V
tailbox=(534,914,564,930)
tb=out[tailbox[1]:tailbox[3],tailbox[0]:tailbox[2]].copy()
pinkc=out[913,552].astype(np.uint8)
tb[:]=A[912,536:570][None,:,:] if False else tb
for y in range(tailbox[1],tailbox[3]):
    tb[y-tailbox[1]]=out[913,tailbox[0]:tailbox[2]]
out[tailbox[1]:tailbox[3],tailbox[0]:tailbox[2]]=tb
vbox=(520,908,590,945)
# restore real pixels outside tail columns for rows 928+ (not touched), V drawn on supersampled patch
patch=draw_patch(np.where(np.zeros_like(out,bool),out,A) if False else out.copy(),vbox,bottom_v)
# only replace inside tail mask area (rows <=930, cols 536..569) to leave everything else bit-exact
m=np.zeros((vbox[3]-vbox[1],vbox[2]-vbox[0]),bool)
m[(914-vbox[1]):(930-vbox[1]),(534-vbox[0]):(566-vbox[0])]=True
tmp=out[vbox[1]:vbox[3],vbox[0]:vbox[2]].copy(); tmp[m]=patch[m]
out[vbox[1]:vbox[3],vbox[0]:vbox[2]]=tmp
def paste_knot(dst,cy_new,cx_new=None,top_cut=None):
    cx_new=KC[0] if cx_new is None else cx_new
    dy=int(round(cy_new-KC[1])); dx=int(round(cx_new-KC[0]))
    box=(520,int(cy_new-16),580,int(cy_new+17))
    a=ellipse_mask(cx_new,cy_new,KR[0],KR[1],box)
    if top_cut is not None:
        rows=np.arange(box[1],box[3])[:,None]
        a=a*np.clip((rows+0.5-(cy_new-top_cut))/1.0,0,1)
    a=a[:,:,None]
    x0,y0,x1,y1=box
    srcp=sprite_full[y0-dy:y1-dy,x0-dx:x1-dx].astype(float)
    cur=dst[y0:y1,x0:x1].astype(float)
    dst[y0:y1,x0:x1]=np.round(cur*(1-a)+srcp*a).astype(np.uint8)
KNOT_BOTTOM_CY=862.0
paste_knot(out,KNOT_BOTTOM_CY)

# =====================  TOP (rope across the upper wall, y 257..338)  =====================
tbox=(500,238,620,352)
def interp1(xs,ys): 
    return lambda y: np.interp(y,xs,ys)
Lx=interp1([255,257,268,275,290,305,325,337,339],[549,549,548.5,545.5,541.5,539,537.5,537,537])
Rx=interp1([255,257,263,270,280,295,315,335,339],[572,572,571.5,568,563,559,557,555,555])
sky=tuple(int(v) for v in A[250,555])
def cy_curve(x):
    return np.interp(x,[505,515,520,525,530,533,541,550,560,570,575,580,585,590,601],[324.5,328.5,330.5,332,333,334,335.7,336.4,336.4,335.5,334.5,334,332,330.5,327])
# fill: neighbours come from a streak-free copy so the pink gradient is continued smoothly
ya,yb=255,339
cleanT=A.copy()
sm=A[270:331,500:610].astype(int)
streak=((sm.sum(2)<540)&(sm[:,:,0]<225))
streak=cv2.dilate(streak.astype(np.uint8),np.ones((5,5),np.uint8))>0
tsub=np.ascontiguousarray(A[270:331,500:610])
cleanT[270:331,500:610]=cv2.inpaint(tsub,(streak*255).astype(np.uint8),4,cv2.INPAINT_TELEA)
def vcol(src,x,yref):
    w=np.array([1,2,3,4,3,2,1],float); w/=w.sum()
    return sum(w[k]*src[yref-3+k,x].astype(float) for k in range(7))
def lerp_row(src,yref,xa,xb,xs):
    t=((xs-xa)/(xb-xa))[:,None]
    return vcol(src,xa,yref)*(1-t)+vcol(src,xb,yref)*t
# smooth pink model of the wall (plane fitted on clean pink pixels away from the rope)
_ys,_xs=np.mgrid[270:327,512:596]
_sub=A[270:327,512:596].astype(float)
_ok=(_sub[:,:,0]>238)&(_sub[:,:,1]>135)&(_sub[:,:,1]<170)&(_sub[:,:,2]>175)&~((_xs>=528)&(_xs<=566))
_X=np.c_[np.ones(_ok.sum()),_xs[_ok],_ys[_ok]]
_co=[np.linalg.lstsq(_X,_sub[:,:,c][_ok],rcond=None)[0] for c in range(3)]
def plane_fit(xs,y):
    return np.stack([_co[c][0]+_co[c][1]*xs+_co[c][2]*y for c in range(3)],1)
for y in range(ya,yb+1):
    xl=int(np.floor(Lx(y)))-6; xr=int(np.ceil(Rx(y)))+6
    xs=np.arange(xl+1,xr)
    yr=min(max(y,277),326)
    yr2=min(max(y,277),326)
    cup=(0.5*(cleanT[yr2,xs-34].astype(float)+cleanT[yr2,xs+34].astype(float))) if y<312 else cleanT[yr2,xs+34].astype(float)
    cdn=lerp_row(A,342+3,531,561,xs)
    cc=cy_curve(xs)
    for i,x in enumerate(xs):
        v=cup[i] if y<cc[i] else cdn[i]
        e=min(x-xl,xr-x)
        al=1.0 if y>=326 else float(np.clip(e/2.5,0,1))
        out[y,x]=np.round(v*al+A[y,x].astype(float)*(1-al)).astype(np.uint8)
def top_draw(d,P):
    d.polygon(P([(515.0,236.0),(556.0,276.4),(598.0,236.0)]),fill=sky)
    thick_line(d,P,[(515.0,236.0+0.0),(522.5,244.0),(556.0,276.4)],4.3,BLACK)
    thick_line(d,P,[(556.0,276.4),(590.5,244.0),(598.0,236.5)],4.3,BLACK)
    thick_line(d,P,[(520,330.5),(525,332),(530,333),(533,334),(541,335.7),(550,336.4),(560,336.4),(570,335.5),(575,334.5),(580,334),(585,332)],4.5,BLACK)
Tmask_poly=[(Lx(y)-6.5,y) for y in range(255,340,4)]+[(Rx(y)+6.5,y) for y in range(339,254,-4)]
tm=poly_mask(Tmask_poly,tbox)
tm=cv2.dilate(tm.astype(np.uint8),np.ones((3,3),np.uint8))>0
tp=draw_patch(out.copy(),tbox,top_draw)
tmp=out[tbox[1]:tbox[3],tbox[0]:tbox[2]].copy(); tmp[tm]=tp[tm]
out[tbox[1]:tbox[3],tbox[0]:tbox[2]]=tmp
KNOT_TOP_CY=345.0
paste_knot(out,KNOT_TOP_CY,548.4,top_cut=9.6)
def knot_arc(d,P):
    cx,cy=548.4,KNOT_TOP_CY
    d.arc([x for x in sum(P([(cx-KR[0]+0.8,cy-KR[1]+0.8),(cx+KR[0]-0.8,cy+KR[1]-0.8)]),())],198,342,fill=BLACK,width=int(2.4*S))
kb=(528,326,570,360)
kp=draw_patch(out.copy(),kb,knot_arc)
mm=ellipse_mask(548.4,KNOT_TOP_CY,KR[0]+0.5,KR[1]+0.5,kb)>0.0
mm&=(np.arange(kb[1],kb[3])[:,None]<KNOT_TOP_CY-4)
tmp=out[kb[1]:kb[3],kb[0]:kb[2]].copy(); tmp[mm]=kp[mm]; out[kb[1]:kb[3],kb[0]:kb[2]]=tmp
Image.fromarray(out).save(SP+'/picfix/L48b/final_new.png')
