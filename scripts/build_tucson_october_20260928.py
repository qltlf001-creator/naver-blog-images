from PIL import Image, ImageDraw, ImageFont
import os, random

OUT='2026-09/tucson-october-20260928'
os.makedirs(OUT, exist_ok=True)
W,H=1600,900
FONT_B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def f(path,size): return ImageFont.truetype(path,size,index=0)
FB=f(FONT_B,72); FXL=f(FONT_B,118); FL=f(FONT_B,88); FM=f(FONT_B,46); FS=f(FONT_R,32); FT=f(FONT_B,28); FSS=f(FONT_R,25)

def bg(base,seed,accent):
    random.seed(seed)
    im=Image.new('RGB',(W,H),base)
    d=ImageDraw.Draw(im,'RGBA')
    # layered metallic planes + fine dot texture; no vehicle likeness is depicted
    for i in range(22):
        x0=random.randint(-220,1400); y0=random.randint(-100,820)
        ww=random.randint(260,680); hh=random.randint(80,260)
        a=random.randint(15,38)
        d.polygon([(x0,y0),(x0+ww,y0-60),(x0+ww+120,y0+hh),(x0+100,y0+hh+60)],fill=(*accent,a))
    for i in range(23000):
        x=random.randrange(W); y=random.randrange(H)
        v=random.randint(10,30)
        d.point((x,y),fill=(255,255,255,v))
    return im

def pill(d,xy,text,fill=(255,255,255,28),outline=(255,255,255,70),font=FT,fg=(245,245,245,255)):
    x,y=xy
    box=d.textbbox((0,0),text,font=font); tw,th=box[2]-box[0],box[3]-box[1]
    d.rounded_rectangle((x,y,x+tw+44,y+th+26),radius=23,fill=fill,outline=outline,width=2)
    d.text((x+22,y+10),text,font=font,fill=fg)
    return x+tw+44

def footer(d):
    d.text((100,835),'현대자동차 공식 발표 기반',font=FSS,fill=(210,214,217,230))
    d.text((1375,835),'2026.09',font=FSS,fill=(210,214,217,180))

def save(im,name):
    im.save(os.path.join(OUT,name),quality=91,subsampling=0,optimize=True)

# 01 HOMEFEED HERO
im=bg((23,28,31),11,(122,95,64)); d=ImageDraw.Draw(im,'RGBA')
d.text((100,92),'디 올 뉴 투싼',font=FB,fill=(255,255,255,255))
d.text((100,200),'10월 가격 공개',font=FXL,fill=(255,231,194,255))
d.text((100,345),'기다릴 가치가 갈리는 순간',font=FL,fill=(255,255,255,255))
x=pill(d,(100,540),'6년 만의 풀체인지'); pill(d,(x+18,540),'가격은 아직 미공개',fill=(172,70,50,55),outline=(236,159,143,110))
d.rounded_rectangle((100,640,1500,785),radius=24,fill=(8,11,13,150),outline=(255,255,255,38),width=2)
d.text((135,662),'핵심은 출시 여부가 아니라',font=FM,fill=(242,244,245,255))
d.text((135,720),'신형 가격표와 현행 2,844만원의 간격',font=FM,fill=(255,231,194,255))
footer(d); save(im,'01-homefeed-tucson-october.jpg')

# 02 PACKAGING
im=bg((22,35,42),22,(63,133,160)); d=ImageDraw.Draw(im,'RGBA')
d.text((100,90),'차체는 커졌습니다',font=FB,fill=(255,255,255,255))
d.text((100,185),'그런데 숫자보다 중요한 건 2열 체감',font=FM,fill=(206,231,240,255))
metrics=[('4,700mm','전장','+60mm'),('2,785mm','휠베이스','+30mm'),('83°','2열 도어','기존 73°')]; xs=[100,590,1080]
for (val,label,delta),x in zip(metrics,xs):
    d.rounded_rectangle((x,320,x+400,660),radius=28,fill=(255,255,255,18),outline=(145,210,235,90),width=2)
    d.text((x+30,360),label,font=FT,fill=(173,211,226,255)); d.text((x+30,435),val,font=FL,fill=(255,255,255,255)); d.text((x+30,565),delta,font=FM,fill=(135,220,187,255))
d.text((100,712),'카시트·부모님 승하차처럼 2열 사용성은',font=FM,fill=(238,243,245,255))
d.text((100,770),'제원표보다 먼저 체감될 수 있습니다.',font=FM,fill=(173,225,206,255))
footer(d); save(im,'02-space-packaging.jpg')

# 03 POWERTRAIN
im=bg((28,31,40),33,(103,85,160)); d=ImageDraw.Draw(im,'RGBA')
d.text((100,88),'파워트레인 변화',font=FB,fill=(255,255,255,255))
d.text((100,190),'가솔린은 8단 자동변속기 · 하이브리드는 245PS',font=FM,fill=(221,215,245,255))
for x,title in [(100,'1.6 터보 가솔린'),(835,'1.6 터보 하이브리드')]:
    d.rounded_rectangle((x,310,x+665,705),radius=30,fill=(255,255,255,20),outline=(188,176,236,80),width=2); d.text((x+38,350),title,font=FM,fill=(220,215,246,255))
d.text((140,445),'193PS',font=FXL,fill=(255,255,255,255)); d.text((140,590),'8단 자동변속기',font=FM,fill=(132,205,245,255))
d.text((875,430),'245PS',font=FXL,fill=(255,255,255,255)); d.text((875,555),'17.4km/L',font=f(FONT_B,78),fill=(148,224,183,255)); d.text((875,645),'17인치 · 2WD 기준',font=FS,fill=(210,214,220,255))
footer(d); save(im,'03-powertrain.jpg')

# 04 DIGITAL
im=bg((24,36,34),44,(72,145,120)); d=ImageDraw.Draw(im,'RGBA')
d.text((100,88),'화면 크기보다 큰 변화',font=FB,fill=(255,255,255,255))
d.text((100,190),'투싼에도 “소프트웨어 중심 차량” 경험이 내려옵니다',font=FM,fill=(206,239,226,255))
items=[('17 / 12.9인치','센터 디스플레이'),('Pleos Connect','현대차 차세대 인포테인먼트'),('Gleo AI','생성형 AI 에이전트')]
for i,(a,b) in enumerate(items):
    y=315+i*150; d.rounded_rectangle((100,y,1500,y+118),radius=22,fill=(255,255,255,18),outline=(143,219,190,70),width=2); d.text((140,y+22),a,font=FM,fill=(151,229,198,255)); d.text((620,y+30),b,font=FM,fill=(248,249,249,255))
d.text((100,790),'새 기능의 숫자보다 실제 반응속도·조작 동선·업데이트 안정성이 구매 후 만족도를 가릅니다.',font=FS,fill=(230,236,233,255))
footer(d); save(im,'04-digital-safety.jpg')

# 05 PRICE DECISION
im=bg((38,30,26),55,(153,110,72)); d=ImageDraw.Draw(im,'RGBA')
d.text((100,88),'결국 10월에 볼 숫자',font=FB,fill=(255,255,255,255))
d.text((100,188),'245마력보다 먼저 “가격표 첫 줄”입니다',font=FM,fill=(248,219,190,255))
for i,(a,b) in enumerate([('2,844만원~','현행 투싼 가솔린'),('3,318만원~','현행 투싼 하이브리드')]):
    x=100+i*735; d.rounded_rectangle((x,330,x+665,610),radius=28,fill=(255,255,255,20),outline=(238,193,151,80),width=2); d.text((x+38,375),b,font=FT,fill=(230,204,181,255)); d.text((x+38,455),a,font=FL,fill=(255,255,255,255))
d.rounded_rectangle((100,665,1500,800),radius=22,fill=(126,58,38,75),outline=(238,160,132,100),width=2)
d.text((140,690),'신형은 10월 중 가격 공개 후 국내 판매 예정',font=FM,fill=(255,243,236,255)); d.text((140,748),'기다릴지 말지는 가격표를 본 뒤 계산해도 늦지 않습니다.',font=FS,fill=(248,219,190,255))
footer(d); save(im,'05-price-decision.jpg')

print('generated', sorted(os.listdir(OUT)))
