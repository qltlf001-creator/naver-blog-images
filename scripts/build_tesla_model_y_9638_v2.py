from PIL import Image, ImageDraw, ImageFont
import os

OUT='2026-09/tesla-model-y-9638-v2'
os.makedirs(OUT, exist_ok=True)
W=1200
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def font(sz,bold=False): return ImageFont.truetype(BOLD if bold else REG, sz)
def rr(draw, box, r, fill, outline=None, width=1): draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)
def grad(w,h,c1,c2):
    im=Image.new('RGB',(w,h),c1); p=im.load()
    for y in range(h):
        t=y/(h-1); c=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
        for x in range(w): p[x,y]=c
    return im

def add_brand(draw, y=42, dark=True):
    col=(230,233,240) if dark else (80,86,98)
    draw.text((64,y),'AUTOMOTIVE ISSUE · 2026.09',font=font(22,True),fill=col)

def save(im,name): im.save(os.path.join(OUT,name), optimize=True)

# 1) HOMEFEED
im=grad(W,675,(9,13,22),(31,42,61)); d=ImageDraw.Draw(im)
for i in range(9):
    x0=660+i*70; d.polygon([(x0,675),(x0+28,675),(1110+i*12,360),(1097+i*12,360)], fill=(235,240,248))
rr(d,(760,105,1130,560),30,(15,21,32),outline=(78,91,113),width=2)
d.text((800,145),'AUGUST SALES',font=font(24,True),fill=(161,175,197))
d.text((800,185),'1위',font=font(72,True),fill=(255,79,79))
d.text((800,275),'9,638',font=font(88,True),fill=(255,255,255))
d.text((800,380),'대',font=font(36,True),fill=(210,215,226))
labels=[('모델 Y',9638,(244,65,70)),('쏘렌토',6397,(112,130,156)),('그랜저',5931,(86,103,128))]
for i,(lab,val,col) in enumerate(labels):
    y=445+i*36; d.text((800,y),lab,font=font(19,True),fill=(230,233,240)); bw=int(210*val/9638); rr(d,(900,y+4,900+bw,y+23),9,col)
add_brand(d)
d.text((64,108),'테슬라 모델 Y',font=font(55,True),fill=(255,255,255))
d.text((64,180),'9,638대',font=font(108,True),fill=(255,80,80))
d.text((64,305),'쏘렌토까지 제쳤다',font=font(50,True),fill=(255,255,255))
d.text((64,373),'한국서 왜 이렇게 팔릴까?',font=font(40,True),fill=(234,190,84))
rr(d,(64,472,660,584),24,(244,247,252)); d.text((92,495),'8월 국내 전체 판매 1위',font=font(29,True),fill=(21,29,42)); d.text((92,538),'쏘렌토보다 3,241대 더 판매',font=font(26,True),fill=(181,48,51))
d.text((64,624),'판매량·가격·주행거리·전기차 시장 흐름을 함께 봅니다.',font=font(21),fill=(186,194,208))
save(im,'01-homefeed.png')

# 2) SALES RANKING
im=grad(W,820,(245,248,252),(228,235,244)); d=ImageDraw.Draw(im); add_brand(d,42,False)
d.text((64,90),'8월 국내 자동차 판매 TOP 5',font=font(48,True),fill=(22,31,45)); d.text((64,158),'모델 Y는 수입차 1위를 넘어 전체 내수 판매 1위에 올랐습니다.',font=font(24),fill=(84,94,110))
vals=[('테슬라 모델 Y',9638,(222,54,62)),('기아 쏘렌토',6397,(48,93,142)),('현대 그랜저',5931,(70,108,154)),('기아 카니발',4186,(117,139,166)),('기아 스포티지',3874,(140,159,181))]
for i,(lab,val,col) in enumerate(vals):
    y=248+i*98; rr(d,(43,y-29,98,y+26),18,col); d.text((70,y-2),f'{i+1}',font=font(30,True),fill=(255,255,255),anchor='mm'); d.text((125,y-16),lab,font=font(28,True),fill=(25,33,45)); rr(d,(125,y+26,1020,y+58),16,(212,220,231)); bw=int(895*val/10000); rr(d,(125,y+26,125+bw,y+58),16,col); d.text((1055,y+8),f'{val:,}대',font=font(28,True),fill=(25,33,45),anchor='ra')
rr(d,(720,694,1130,770),22,(255,255,255),outline=(209,216,226),width=2); d.text((748,712),'모델 Y − 쏘렌토',font=font(21,True),fill=(82,90,102)); d.text((748,741),'격차 3,241대',font=font(31,True),fill=(190,45,50)); d.text((64,772),'자료: 산업통상부 2026년 8월 자동차산업 동향',font=font(17),fill=(103,112,126))
save(im,'02-sales-ranking.png')

# 3) PRICE
im=grad(W,820,(15,20,29),(33,39,49)); d=ImageDraw.Draw(im); add_brand(d,42,True)
d.text((64,92),'4,999만원이 만든 가격 포지션',font=font(48,True),fill=(255,255,255)); d.text((64,160),'5천만원 안팎 SUV를 찾는 소비자에게 모델 Y가 현실적인 비교 후보가 됐습니다.',font=font(23),fill=(190,198,211))
rr(d,(64,230,1136,300),26,(247,248,250)); d.text((92,247),'5,000만원 문턱',font=font(27,True),fill=(38,46,58)); d.line((315,265,1075,265),fill=(194,200,210),width=5); d.ellipse((510,249,542,281),fill=(224,57,63)); d.text((526,312),'Premium RWD 4,999만원',font=font(22,True),fill=(244,92,96),anchor='ma')
cards=[('Premium RWD','4,999만원','5인승 · RWD'),('Premium Long Range AWD','6,699만원','5인승 · AWD'),('Model Y L','7,299만원','6인승 · AWD')]
for idx,(name,price,sub) in enumerate(cards):
    x=[64,421,778][idx]; rr(d,(x,390,x+322,650),28,(246,248,251),outline=(92,102,118),width=2); d.text((x+28,425),name,font=font(22,True),fill=(61,69,82)); d.text((x+28,490),price,font=font(47,True),fill=(204,48,55) if idx==0 else (22,31,44)); d.text((x+28,565),sub,font=font(22),fill=(103,111,124))
    if idx==0: rr(d,(x+28,600,x+190,632),14,(231,66,72)); d.text((x+109,615),'진입 가격',font=font(18,True),fill=(255,255,255),anchor='mm')
d.text((64,714),'※ 표시 가격은 2026년형 기준이며 세금·프로모션·보조금 적용 여부에 따라 실제 구매가는 달라질 수 있습니다.',font=font(17),fill=(174,181,194)); d.text((64,758),'가격 확인: 네이버 자동차·다나와 자동차 / 주행거리: Tesla Korea 정부 공인 연비',font=font(17),fill=(174,181,194))
save(im,'03-price-position.png')

# 4) RANGE
im=grad(W,820,(239,246,250),(211,228,239)); d=ImageDraw.Draw(im); add_brand(d,42,False)
d.text((64,94),'1회 충전, 얼마나 갈 수 있나',font=font(48,True),fill=(22,31,45)); d.text((64,160),'정부 공인 복합 주행거리 기준으로 400km에서 543km까지 확보했습니다.',font=font(24),fill=(75,88,106))
for i in range(9):
    y=700+i*11; d.line((0,y,1200,y-160),fill=(170-i*6,180-i*5,188-i*4),width=5)
ranges=[('Premium RWD',400,(43,112,181)),('Premium Long Range AWD',505,(38,137,126)),('Model Y L',543,(191,117,35))]
for i,(name,val,col) in enumerate(ranges):
    x=[64,421,778][i]; rr(d,(x,260,x+322,625),28,(255,255,255),outline=(195,207,219),width=2); d.text((x+161,305),name,font=font(21,True),fill=(57,67,80),anchor='ma'); box=(x+65,355,x+257,547); d.arc(box,150,390,fill=(214,221,229),width=24); d.arc(box,150,150+240*val/600,fill=col,width=24); d.text((x+161,426),f'{val}',font=font(60,True),fill=(24,33,45),anchor='mm'); d.text((x+161,482),'km',font=font(25,True),fill=col,anchor='mm'); d.text((x+161,572),'복합 기준',font=font(20),fill=(105,115,129),anchor='mm')
rr(d,(64,665,1136,750),22,(28,38,52)); d.text((92,687),'실주행거리는 기온·속도·도로 상태·냉난방 사용·적재량에 따라 달라집니다.',font=font(22,True),fill=(255,255,255)); d.text((64,775),'자료: Tesla Korea 정부 공인 표준 연비 및 등급',font=font(17),fill=(87,98,113))
save(im,'04-certified-range.png')

# 5) IMPORT EV SHARE
im=grad(W,820,(247,248,250),(232,236,242)); d=ImageDraw.Draw(im); add_brand(d,42,False)
d.text((64,94),'수입차 시장, 전기차가 절반을 넘었다',font=font(48,True),fill=(22,31,45)); d.text((64,160),'2026년 8월 수입 승용차 등록에서 전기차는 15,183대로 약 50.9%를 차지했습니다.',font=font(23),fill=(80,90,104))
rr(d,(64,230,440,600),32,(19,28,41)); d.text((105,275),'전기차',font=font(29,True),fill=(179,189,203)); d.text((105,340),'50.9%',font=font(78,True),fill=(66,159,255)); d.text((105,440),'15,183대',font=font(34,True),fill=(255,255,255)); d.text((105,500),'수입 승용차 등록',font=font(22),fill=(172,182,197))
items=[('전기차',50.9,(52,145,238),'15,183대'),('하이브리드',40.0,(54,171,124),'약 40.0%'),('가솔린',8.5,(204,94,78),'약 8.5%')]
for i,(lab,pct,col,sub) in enumerate(items):
    y=285+i*118; d.text((500,y),lab,font=font(27,True),fill=(33,42,55)); d.text((1060,y),f'{pct:.1f}%',font=font(28,True),fill=col,anchor='ra'); rr(d,(500,y+45,1085,y+79),17,(208,215,225)); rr(d,(500,y+45,500+int(585*pct/55),y+79),17,col); d.text((500,y+87),sub,font=font(18),fill=(103,112,126))
rr(d,(64,650,1136,736),22,(255,255,255),outline=(206,212,222),width=2); d.text((92,672),'해석 포인트',font=font(22,True),fill=(196,52,57)); d.text((255,672),'모델 Y 판매 강세는 한 차종의 현상만이 아니라, 수입차 전동화 흐름과 겹쳐 있습니다.',font=font(21,True),fill=(42,51,64)); d.text((64,775),'자료: 한국수입자동차협회(KAIDA) 집계 보도 · 2026년 8월',font=font(17),fill=(103,112,126))
save(im,'05-import-ev-share.png')
