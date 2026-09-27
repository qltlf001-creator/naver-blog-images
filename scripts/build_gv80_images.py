from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import urllib.request, io

OUT = Path('2026-09/gv80-hybrid')
OUT.mkdir(parents=True, exist_ok=True)
W,H = 1200,675
URLS = [
 'https://www.hyundaimotorgroup.com/image/upload/asset_library/MDA00000000000083126/3ae5707bc7714cdb9a68c37cfe6bde12.jpg',
 'https://www.hyundaimotorgroup.com/image/upload/asset_library/MDA00000000000083131/eeea08dfbd1b4dae914e8ad6fea0e939.jpg'
]

def font(size, bold=False):
    cands = [
      '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
      '/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf' if bold else '/usr/share/fonts/truetype/noto/NotoSansKR-Regular.ttf',
      '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    ]
    for p in cands:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def dl(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r: return Image.open(io.BytesIO(r.read())).convert('RGB')

def cover(im):
    s=max(W/im.width,H/im.height); nw,nh=int(im.width*s),int(im.height*s)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    l=(nw-W)//2; t=(nh-H)//2
    return im.crop((l,t,l+W,t+H))

def panel(base, alpha=165):
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rounded_rectangle((35,35,690,640),28,fill=(5,10,18,alpha))
    return Image.alpha_composite(base.convert('RGBA'),ov)

def txt(d,xy,s,size,bold=False,fill='white',anchor=None):
    d.text(xy,s,font=font(size,bold),fill=fill,anchor=anchor)

def save_home(im):
    b=cover(im).filter(ImageFilter.GaussianBlur(0.2)); b=panel(b,165); d=ImageDraw.Draw(b)
    gold=(238,193,98,255)
    txt(d,(70,70),'GENESIS GV80',30,True,gold)
    txt(d,(70,125),'하이브리드',70,True)
    txt(d,(70,218),'10월 국내 출시 예정',42,True)
    d.line((70,285,625,285),fill=gold,width=3)
    txt(d,(70,320),'352PS  ·  54.0kgf·m',34,True)
    txt(d,(70,372),'연비 약 25% 개선',34,True)
    txt(d,(70,465),'가격 · 연비 · 출시일 핵심정리',28,True)
    txt(d,(70,535),'공식 발표 기준',23,False,(220,220,220,255))
    b.convert('RGB').save(OUT/'01-homefeed.jpg',quality=90,optimize=True)

def save_specs(im):
    b=cover(im); b=panel(b,175); d=ImageDraw.Draw(b); gold=(238,193,98,255)
    txt(d,(70,60),'GV80 하이브리드 핵심 제원',43,True)
    rows=[('시스템 합산 최고출력','352PS'),('최대토크','54.0kgf·m'),('0→100km/h','약 7.1초'),('연비 개선','약 25% 이상')]
    y=145
    for a,v in rows:
        d.rounded_rectangle((70,y,625,y+92),18,fill=(20,25,32,220),outline=(110,100,70,255),width=2)
        txt(d,(95,y+20),a,23,False,(225,225,225,255)); txt(d,(600,y+46),v,34,True,gold,'rm')
        y+=108
    txt(d,(70,595),'※ 연구소 자체 측정 포함 · 최종 공인연비는 별도 확인 필요',20,False,(220,220,220,255))
    b.convert('RGB').save(OUT/'02-specs.jpg',quality=90,optimize=True)

def save_system(im):
    b=cover(im); ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rectangle((0,0,W,H),fill=(4,8,14,125)); b=Image.alpha_composite(b.convert('RGBA'),ov); d=ImageDraw.Draw(b); gold=(238,193,98,255)
    txt(d,(60,45),'P1 · P2 듀얼 모터 구조',47,True)
    txt(d,(60,110),'두 모터가 역할을 나눠 효율과 응답성을 끌어올립니다',26,False,(230,230,230,255))
    cards=[('P1 모터','시동 · 발전 · 토크 보조'),('P2 모터','구동 · 회생제동 담당'),('EV 모드','도심 저속구간 전기주행 확대'),('재가속','100km/h 재가속 약 18% 개선'),('배터리','수냉식 하이브리드 배터리'),('HPC','도로를 예측해 에너지 사용 최적화')]
    positions=[(60,190),(415,190),(770,190),(60,395),(415,395),(770,395)]
    for (title,desc),(x,y) in zip(cards,positions):
        d.rounded_rectangle((x,y,x+325,y+165),22,fill=(8,15,25,225),outline=gold,width=2)
        txt(d,(x+25,y+25),title,30,True,gold); txt(d,(x+25,y+82),desc,21,False)
    b.convert('RGB').save(OUT/'03-system.jpg',quality=90,optimize=True)

def save_check(im):
    b=cover(im); b=panel(b,180); d=ImageDraw.Draw(b); gold=(238,193,98,255)
    txt(d,(70,60),'출시 전 체크 포인트',48,True)
    items=[('01','공식 판매 가격'),('02','정부 공인 복합연비'),('03','트림별 기본 사양 · 옵션'),('04','계약 · 실제 출고 일정')]
    y=155
    for no,label in items:
        d.rounded_rectangle((70,y,630,y+82),18,fill=(18,23,30,225))
        txt(d,(98,y+41),no,26,True,gold,'lm'); txt(d,(165,y+41),label,28,True,'white','lm'); y+=100
    d.rounded_rectangle((70,575,630,635),15,fill=(110,20,20,225)); txt(d,(350,605),'남은 변수: 가격 · 공인연비',25,True,'white','mm')
    b.convert('RGB').save(OUT/'04-checkpoints.jpg',quality=90,optimize=True)

imgs=[]
for u in URLS:
    try: imgs.append(dl(u))
    except Exception as e: print('download failed',u,e)
if not imgs: raise SystemExit('No source image downloaded')
while len(imgs)<2: imgs.append(imgs[0].copy())
save_home(imgs[0]); save_specs(imgs[0]); save_system(imgs[1]); save_check(imgs[0])
print('generated', list(map(str,OUT.glob('*.jpg'))))
