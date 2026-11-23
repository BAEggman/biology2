import numpy as np, cv2
from PIL import Image
a=np.array(Image.open('sp/navy.png')).astype(float)
rgb=a[...,:3]; al=a[...,3]
hsv=cv2.cvtColor(rgb.astype(np.uint8),cv2.COLOR_RGB2HSV).astype(int)
H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
h,w=al.shape
ring=np.zeros_like(al,bool); ring[118:160,:]=True
white=(V>190)&(S<45)&~ring
lightblue=(H>=90)&(H<=135)&(V>185)&~ring
al[white|lightblue]=0
# remove bottom stray (rows > h-18 near center)
stray=(H>=90)&(H<=135)&(V>140); stray[:h-30,:]=False; al[stray]=0
a[...,3]=al
Image.fromarray(a.astype(np.uint8)).save('sp/navy_c.png')
# sky recolor: straw pixels = blue hue & S>40
straw=(H>=90)&(H<=135)&(S>40)&(V>=48)
outl=(V<48)
L=V.astype(float)
lo,hi=np.percentile(L[straw&(al>200)],5),np.percentile(L[straw&(al>200)],97)
t=np.clip((L-lo)/(hi-lo),0,1)[...,None]
dark=np.array([96,150,205.]); light=np.array([200,229,248.])
sky=rgb.copy(); sky[straw]=(dark+(light-dark)*t)[straw]; sky[outl]=np.minimum(sky[outl],[30,40,60])
b=a.copy(); b[...,:3]=sky
Image.fromarray(b.astype(np.uint8)).transpose(Image.FLIP_LEFT_RIGHT).save('sp/sky_c.png')
for n in ('navy_c','sky_c'):
    im=Image.open(f'sp/{n}.png'); v=Image.new('RGBA',im.size,(181,135,90,255)); v.alpha_composite(im); v.convert('RGB').save(f'sp/{n}_v.png')
c=Image.new('RGB',(w*2+10,h),'white'); c.paste(Image.open('sp/navy_c_v.png'),(0,0)); c.paste(Image.open('sp/sky_c_v.png'),(w+10,0)); c.resize((c.width*2,c.height*2)).save('sp/pair.png')
print(lo,hi)
