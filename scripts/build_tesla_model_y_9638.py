from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT='2026-09/tesla-model-y-9638'
os.makedirs(OUT, exist_ok=True)
W,H=1200,1500
FONT_B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

RED=(222,32,44)
INK=(18,18,22)
MUTED=(101,104,112)
OFF=(247,247,245)
WHITE=(255,255,255)


def font(sz,b=True): return ImageFont.truetype(FONT_B if b else FONT_R, sz)

def rr(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

def shadow_card(base, xy, r=34, fill=WHITE, blur=28, off=(0,14), alpha=38):
    x0,y0,x1,y1=xy
    sh=Image.new('RGBA', base.size, (0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0+off[0],y0+off[1],x1+off[0],y1+off[1]), radius=r, fill=(0,0,0,alpha))
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); base.alpha_composite(sh)
    d=ImageDraw.Draw(base); d.rounded_rectangle(xy, radius=r, fill=fill)


def fit_text(d, text, max_w, start, minsz=32, b=True):
    sz=start
    while sz>=minsz:
        f=font(sz,b)
        box=d.textbbox((0,0),text,font=f)
        if box[2]-box[0] <= max_w: return f
        sz-=2
    return font(minsz,b)

def label(d, x,y,text, fill=RED, fg=WHITE):
    f=font(30,True); box=d.textbbox((0,0),text,font=f); w=box[2]-box[0]
    rr(d,(x,y,x+w+42,y+58),29,fill)
    d.text((x+21,y+10),text,font=f,fill=fg)

def save(im,name):
    p=os.path.join(OUT,name); im.convert('RGB').save(p,optimize=True); print(p)

# 1 HERO
im=Image.new('RGBA',(W,H),OFF+(255,)); d=ImageDraw.Draw(im)
poly=[(0,0),(W,0),(W,430),(760,600),(0,500)]; d.polygon(poly,fill=(24,25,29))
d.polygon([(760,600),(W,430),(W,830),(900,930)],fill=RED)
label(d,76,82,'2026년 8월 국내 판매 1위',RED,WHITE)
d.text((76,195),'TESLA  MODEL Y',font=font(42,True),fill=(230,230,232))
d.text((76,275),'9,638대',font=font(128,True),fill=WHITE)
d.text((80,405),'쏘렌토까지 제쳤다',font=font(52,True),fill=WHITE)
pts=[(170,865),(250,790),(410,740),(660,730),(820,770),(935,835),(1000,855)]
d.line(pts,fill=(90,92,100),width=10,joint='curve')
d.line([(170,865),(1020,865)],fill=(120,122,130),width=6)
for cx in (350,850):
    d.ellipse((cx-70,795,cx+70,935),fill=(35,36,41)); d.ellipse((cx-34,831,cx+34,899),fill=(215,216,220))
shadow_card(im,(76,1010,1124,1400),36,WHITE)
d=ImageDraw.Draw(im)
d.text((126,1068),'왜 지금 더 주목받나',font=font(38,True),fill=INK)
items=[('01','국내 전체 판매 1위'),('02','RWD 시작가 4,999만원'),('03','수입차 EV 비중 50.9%')]
y=1148
for n,t in items:
    d.text((126,y),n,font=font(30,True),fill=RED)
    d.text((210,y-2),t,font=font(34,True),fill=INK); y+=78
save(im,'01-homefeed.png')

# 2 SALES RANKING
im=Image.new('RGBA',(W,H),(252,251,248,255)); d=ImageDraw.Draw(im)
label(d,72,72,'판매량 한눈에',INK,WHITE)
d.text((72,168),'모델 Y가 얼마나 앞섰나',font=fit_text(d,'모델 Y가 얼마나 앞섰나',1056,62),fill=INK)
d.text((72,250),'2026년 8월 국내 내수 판매 상위 3개 모델',font=font(30,False),fill=MUTED)
vals=[('1','테슬라 모델 Y',9638,RED),('2','기아 쏘렌토',6397,(45,48,58)),('3','현대 그랜저',5931,(92,95,104))]
maxv=10000; y=380
for rank,name,v,c in vals:
    shadow_card(im,(72,y,1128,y+255),32,WHITE,blur=18,off=(0,10),alpha=28); d=ImageDraw.Draw(im)
    d.text((112,y+54),rank,font=font(38,True),fill=c)
    d.text((182,y+48),name,font=font(40,True),fill=INK)
    d.text((930,y+42),f'{v:,}',font=font(44,True),fill=c,anchor='ra')
    bx0,by0,bx1=182,y+145,1032
    rr(d,(bx0,by0,bx1,by0+38),19,(232,233,235))
    bw=int((bx1-bx0)*v/maxv); rr(d,(bx0,by0,bx0+bw,by0+38),19,c)
    y+=292
rr(d,(72,1270,1128,1415),32,(24,25,29))
d.text((112,1305),'모델 Y - 쏘렌토',font=font(30,False),fill=(205,206,210))
d.text((112,1352),'+3,241대',font=font(48,True),fill=WHITE)
d.text((570,1362),'단순한 박빙이 아니었다',font=font(34,True),fill=(255,101,110))
save(im,'02-sales-ranking.png')

# 3 PRICE
im=Image.new('RGBA',(W,H),(18,19,23,255)); d=ImageDraw.Draw(im)
label(d,72,72,'가격 포인트',RED,WHITE)
d.text((72,178),'4,999만원',font=font(112,True),fill=WHITE)
d.text((76,315),'Premium RWD 시작가',font=font(36,False),fill=(190,192,200))
d.line((72,410,1128,410),fill=(65,66,73),width=2)
cards=[('Premium RWD','4,999만원','진입 트림'),('Long Range AWD','6,699만원','장거리·AWD'),('Model Y L','7,299만원','6인승')]
y=475
for i,(name,price,desc) in enumerate(cards):
    fill=(31,32,38) if i else (47,20,24)
    rr(d,(72,y,1128,y+225),30,fill)
    d.text((112,y+42),name,font=font(34,True),fill=(235,235,239))
    d.text((112,y+104),price,font=font(58,True),fill=WHITE if i else (255,114,122))
    d.text((880,y+118),desc,font=font(28,False),fill=(180,182,190))
    y+=252
rr(d,(72,1250,1128,1415),32,(245,245,242))
d.text((112,1292),'핵심',font=font(28,True),fill=RED)
d.text((112,1340),'5천만원 안팎 SUV 선택지에 들어왔다',font=font(39,True),fill=INK)
save(im,'03-price-point.png')

# 4 RANGE
im=Image.new('RGBA',(W,H),(247,248,250,255)); d=ImageDraw.Draw(im)
label(d,72,72,'1회 충전 주행거리',INK,WHITE)
d.text((72,175),'400 → 543km',font=font(94,True),fill=INK)
d.text((74,298),'트림에 따라 달라지는 정부 공인 복합 주행거리',font=font(31,False),fill=MUTED)
x=270; d.line((x,450,x,1270),fill=(208,210,215),width=10)
for yv in range(480,1240,90): d.line((x,yv,x,yv+42),fill=WHITE,width=6)
rows=[('Premium RWD','400km',520,RED),('Long Range AWD','505km',805,(46,49,58)),('Model Y L','543km',1090,(88,91,100))]
for name,km,y,c in rows:
    d.ellipse((x-24,y-24,x+24,y+24),fill=c)
    rr(d,(355,y-78,1100,y+88),30,WHITE,outline=(227,228,232),width=2)
    d.text((405,y-48),name,font=font(32,True),fill=INK)
    d.text((1035,y-50),km,font=font(52,True),fill=c,anchor='ra')
    d.text((405,y+18),'정부 공인 복합 기준',font=font(25,False),fill=MUTED)
rr(d,(72,1320,1128,1430),28,(24,25,29))
d.text((112,1352),'※ 실제 주행거리는 기온·속도·적재·도로 조건에 따라 달라질 수 있음',font=font(25,False),fill=(225,226,230))
save(im,'04-range.png')

# 5 MARKET
im=Image.new('RGBA',(W,H),(253,252,249,255)); d=ImageDraw.Draw(im)
label(d,72,72,'시장 변화',RED,WHITE)
d.text((72,176),'수입차 2대 중 1대가 EV',font=fit_text(d,'수입차 2대 중 1대가 EV',1056,64),fill=INK)
d.text((72,265),'2026년 8월 수입 승용차 연료별 등록 비중',font=font(30,False),fill=MUTED)
cx,cy=380,730; R=245; r=155
bbox=(cx-R,cy-R,cx+R,cy+R)
d.pieslice(bbox,-90,-90+360*0.509,fill=RED)
d.pieslice(bbox,-90+360*0.509,-90+360*(0.509+0.4),fill=(45,48,58))
d.pieslice(bbox,-90+360*(0.909),270,fill=(191,193,198))
d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(253,252,249))
d.text((cx,cy-48),'50.9%',font=font(70,True),fill=INK,anchor='ma')
d.text((cx,cy+42),'전기차',font=font(30,True),fill=RED,anchor='ma')
legend=[('EV','15,183대','50.9%',RED),('하이브리드','11,923대','40.0%',(45,48,58)),('가솔린·디젤','2,711대','9.1%',(160,162,169))]
y=510
for name,count,pct,c in legend:
    d.ellipse((730,y+10,754,y+34),fill=c)
    d.text((780,y),name,font=font(32,True),fill=INK)
    d.text((780,y+48),count,font=font(28,False),fill=MUTED)
    d.text((1080,y+12),pct,font=font(36,True),fill=c,anchor='ra')
    y+=150
rr(d,(72,1110,1128,1405),34,(24,25,29))
d.text((116,1160),'테슬라 8월 국내 등록',font=font(31,False),fill=(197,198,203))
d.text((116,1220),'10,400대',font=font(72,True),fill=WHITE)
d.text((116,1320),'7개월 연속 수입차 브랜드 1위',font=font(34,True),fill=(255,100,110))
save(im,'05-import-ev-share.png')
