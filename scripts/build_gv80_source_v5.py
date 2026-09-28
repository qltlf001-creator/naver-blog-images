from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageColor
from pathlib import Path
import os, math

W,H=1600,900
OUT=Path(os.environ.get('GV80_OUT','_staging/gv80-source-v5-generated')); OUT.mkdir(parents=True,exist_ok=True)
BASE=Path(os.environ.get('GV80_BASE','/tmp/gv80-base.jpg'))
FONT_B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if not Path(FONT_R).exists(): FONT_R='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if not Path(FONT_B).exists(): FONT_B='/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'

def font(sz,bold=False): return ImageFont.truetype(FONT_B if bold else FONT_R, sz)

def fit_crop(im):
    im=im.convert('RGB')
    r=max(W/im.width,H/im.height)
    nw,nh=round(im.width*r),round(im.height*r)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    x=(nw-W)//2; y=(nh-H)//2
    return im.crop((x,y,x+W,y+H))

def emerald_tint(im, strength=.28):
    overlay=Image.new('RGB', im.size, '#073a35')
    return Image.blend(im, overlay, strength)

def rr(d, box, radius, fill, outline=None, width=1): d.rounded_rectangle(box,radius,fill=fill,outline=outline,width=width)
def line(d, xy, fill, width=4): d.line(xy,fill=fill,width=width)

def add_label(d, xy, text, fg='#F5D99B', bg=(8,26,28,220), fs=28):
    f=font(fs,True); x,y=xy; b=d.textbbox((0,0),text,font=f); tw=b[2]-b[0]; th=b[3]-b[1]
    rr(d,(x,y,x+tw+36,y+th+22),22,bg,outline='#A98242',width=2); d.text((x+18,y+7),text,font=f,fill=fg)

def shadow_text(d, xy, text, f, fill='white', shadow=(0,0,0,170), offset=3, anchor=None):
    x,y=xy; d.text((x+offset,y+offset),text,font=f,fill=shadow,anchor=anchor); d.text((x,y),text,font=f,fill=fill,anchor=anchor)

def save(im,name,q=92):
    p=OUT/name; im.convert('RGB').save(p,'JPEG',quality=q,optimize=True,progressive=True,subsampling=1)
    print(name, p.stat().st_size)

base=fit_crop(Image.open(BASE)); base=emerald_tint(base,.22)

im=base.copy(); ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
for x in range(W):
    a=max(0,int(185*(1-x/1050)))
    d.rectangle((x,0,x+1,H),fill=(0,0,0,a))
for y in range(300):
    a=int(80*(1-y/300)); d.rectangle((0,y,W,y+1),fill=(0,0,0,a))
add_label(d,(72,58),'2026.09 최신 공식 흐름',fs=26)
shadow_text(d,(74,168),'GV80 하이브리드',font(72,True),'#FFF8E7')
shadow_text(d,(76,258),'출시일 · 가격 · 연비 · 제원',font(40,True),'white')
rr(d,(72,350,620,490),30,(6,23,26,225),outline='#CBA15A',width=2)
d.text((104,374),'10월 출시 흐름',font=font(42,True),fill='#F5D99B')
d.text((104,435),'지금 확인할 것만 압축 정리',font=font(28),fill='white')
rr(d,(72,790,645,842),18,(0,0,0,155))
d.text((96,800),'에디토리얼 제작 이미지 · 공식 차량 사진 아님',font=font(20),fill='#E7E7E7')
im=Image.alpha_composite(im.convert('RGBA'),ov)
save(im,'01-homefeed.jpg',94)

bg=base.filter(ImageFilter.GaussianBlur(8)); bg=ImageEnhance.Brightness(bg).enhance(.34)

def info_canvas(title,kicker):
    im=bg.copy().convert('RGBA'); ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rectangle((0,0,W,H),fill=(3,14,16,95))
    d.text((70,52),kicker,font=font(24,True),fill='#D4A95E')
    d.text((70,94),title,font=font(52,True),fill='white')
    d.line((70,174,1530,174),fill='#9F824E',width=2)
    return im,ov,d

im,ov,d=info_canvas('출시일은 어떻게 읽어야 하나','QUICK UNDERSTAND 01')
line(d,(150,405,1450,405),'#5F6B72',8)
points=[(240,'8월','차세대 하이브리드\n시스템 공개'),(800,'9월 22일','공식 자료에서\n“다음달 출시”'),(1360,'10월','최신 기준\n출시 흐름')]
for i,(x,top,bot) in enumerate(points):
    fill='#D4A95E' if i==2 else '#D9E1E5'
    d.ellipse((x-21,384,x+21,426),fill=fill,outline='white',width=3)
    d.text((x,300),top,font=font(34,True),fill=fill,anchor='mm')
    for j,ln in enumerate(bot.split('\n')): d.text((x,455+j*42),ln,font=font(26,True if i==2 else False),fill='white',anchor='ma')
rr(d,(190,650,1410,800),30,(6,26,29,235),outline='#A98242',width=2)
d.text((240,683),'결론',font=font(24,True),fill='#D4A95E')
d.text((240,724),'정확한 날짜는 미공개 · 최신 공식 표현은 10월 출시 흐름',font=font(34,True),fill='white')
im=Image.alpha_composite(im,ov); save(im,'02-launch.jpg',93)

im,ov,d=info_canvas('가격은 “예상가”보다 차액을 봐야 한다','EXPLAIN 02')
rr(d,(90,240,760,690),36,(8,25,27,235),outline='#7A858A',width=2)
d.text((130,280),'현재 GV80 2.5T 기준',font=font(27,True),fill='#CFD8DC')
d.text((130,350),'6,886',font=font(92,True),fill='white')
d.text((510,405),'만원',font=font(34,True),fill='#CFD8DC')
d.text((130,500),'공식 BTO 기본가 기준',font=font(26),fill='#BEC7CC')
d.text((130,555),'※ 하이브리드 최종 가격은 아직 미공개',font=font(24,True),fill='#F5D99B')
shadow_text(d,(805,432),'→',font(72,True),'#D4A95E')
rr(d,(910,240,1510,690),36,(30,23,11,235),outline='#CBA15A',width=3)
d.text((955,280),'구매 판단 포인트',font=font(28,True),fill='#F5D99B')
d.text((955,350),'하이브리드',font=font(48,True),fill='white')
d.text((955,414),'추가금',font=font(72,True),fill='#F5D99B')
for j,t in enumerate(['기본 사양 차이','연료비 절감 폭','출고 시점']): d.text((960,530+j*48),'• '+t,font=font(25),fill='white')
im=Image.alpha_composite(im,ov); save(im,'03-price.jpg',93)

im,ov,d=info_canvas('“약 25% 이상 개선”을 그대로 km/L로 바꾸면 안 된다','DEEPEN 03')
rr(d,(90,245,650,710),40,(26,20,9,235),outline='#CBA15A',width=3)
d.text((370,345),'약',font=font(34,True),fill='#F5D99B',anchor='mm')
d.text((370,470),'25%+',font=font(112,True),fill='#FFF4D6',anchor='mm')
d.text((370,585),'연비 개선',font=font(38,True),fill='white',anchor='mm')
d.text((370,645),'제네시스 연구소 자체 측정',font=font(21),fill='#D9D9D9',anchor='mm')
labels=[('현재','연구소 측정치'),('출시 전','정부 인증'),('최종','공인연비 확인')]
for i,(a,b) in enumerate(labels):
    y=272+i*150
    rr(d,(760,y,1470,y+112),24,(8,27,30,230),outline='#53656A',width=2)
    d.text((800,y+20),a,font=font(24,True),fill='#D4A95E')
    d.text((1000,y+20),b,font=font(30,True),fill='white')
    if i<2: d.text((1115,y+118),'↓',font=font(30,True),fill='#D4A95E',anchor='ma')
rr(d,(760,735,1470,810),24,(8,27,30,235))
d.text((800,752),'핵심: 최종 km/L 숫자는 출시 직전 다시 확인',font=font(28,True),fill='white')
im=Image.alpha_composite(im,ov); save(im,'04-efficiency.jpg',93)

im,ov,d=info_canvas('숫자 네 개만 기억하면 제원이 보인다','REMEMBER / SAVE 04')
cards=[('2.5T','터보 하이브리드'),('352 PS','합산 최고출력'),('54.0','kgf·m 합산 토크'),('약 7.1초','0→100 km/h 연구소')]
positions=[(90,240,770,450),(830,240,1510,450),(90,500,770,710),(830,500,1510,710)]
for (v,l),box in zip(cards,positions):
    rr(d,box,30,(8,26,29,235),outline='#866F46',width=2)
    x1,y1,x2,y2=box
    d.text((x1+38,y1+32),v,font=font(58,True),fill='#FFF2D1')
    d.text((x1+38,y1+126),l,font=font(26,True),fill='white')
rr(d,(90,760,1510,830),24,(32,24,10,230),outline='#CBA15A',width=2)
d.text((800,793),'효율형만이 아니라 성능·정숙성까지 함께 노리는 방향',font=font(29,True),fill='#F7E9C7',anchor='mm')
im=Image.alpha_composite(im,ov); save(im,'05-specs.jpg',93)
