from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path('2026-09/g80-gv70-fuel-line-recall')
OUT.mkdir(parents=True, exist_ok=True)
REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
W, H = 1200, 900

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size, index=1)

def rr(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def label(draw, text, x, y, fill):
    ft = font(28, True)
    b = draw.textbbox((0, 0), text, font=ft)
    rr(draw, (x, y, x + b[2] - b[0] + 32, y + 50), 25, fill)
    draw.text((x + 16, y + 8), text, font=ft, fill='white')

# 01 homefeed
im = Image.new('RGB', (W, H), (19, 22, 28)); d = ImageDraw.Draw(im)
for i in range(H):
    t = i / H
    c = (19 + int(10*t), 22 + int(8*t), 28 + int(10*t))
    d.line((0, i, W, i), fill=c)
d.ellipse((650, -220, 1130, 260), fill=(70, 25, 30))
d.ellipse((720, -150, 1060, 190), fill=(112, 27, 31))
pts = [(100,690),(265,690),(355,610),(520,610),(610,690),(780,690),(870,610),(1030,610),(1095,645)]
d.line(pts, fill=(177,184,195), width=18, joint='curve')
for x,y in [(355,610),(610,690),(870,610)]:
    d.ellipse((x-26,y-26,x+26,y+26), fill=(177,184,195), outline=(238,240,243), width=4)
cx, cy = 950, 505
d.polygon([(cx,cy-75),(cx-62,cy+28),(cx+62,cy+28)], fill=(183,35,35))
d.ellipse((cx-60,cy-20,cx+60,cy+100), fill=(183,35,35))
label(d, '중대리콜 · 화재위험', 90, 84, (177,35,35))
d.text((90,170), '제네시스 G80 · GV70', font=font(68,True), fill=(248,249,251))
d.text((90,262), '2.2 디젤 연료라인 리콜', font=font(59,True), fill=(248,249,251))
d.text((90,365), '10,566대', font=font(96,True), fill=(241,184,63))
d.text((90,485), '2026. 9. 21 시작', font=font(40,True), fill=(208,214,222))
d.text((90,545), '저압연료라인 누유 → 시동 꺼짐·화재 가능성', font=font(34), fill=(208,214,222))
d.text((90,806), '차량번호·차대번호로 대상 여부 확인', font=font(30,True), fill=(241,243,246))
im.save(OUT/'01-homefeed.jpg', quality=88, optimize=True, progressive=True)

# 02 target period
im = Image.new('RGB', (W, H), (248,247,244)); d = ImageDraw.Draw(im)
d.text((72,64), '누가 이번 리콜 대상인가', font=font(52,True), fill=(25,25,25))
d.text((72,132), '차명보다 엔진과 생산기간을 먼저 확인', font=font(30), fill=(92,92,92))
cards = [('G80 (RG3)','2.2 디젤','2020.03.10','2021.12.30'), ('GV70 (JK)','2.2 디젤','2020.07.29','2024.05.02')]
for (name,eng,s,e), y in zip(cards, [235,500]):
    rr(d,(72,y,1128,y+210),28,(255,255,255),outline=(222,218,210),width=2)
    label(d,eng,96,y+24,(40,100,199))
    d.text((96,y+88),name,font=font(44,True),fill=(28,28,28))
    d.text((545,y+58),s,font=font(38,True),fill=(30,30,30))
    d.text((800,y+58),'→',font=font(36,True),fill=(155,155,155))
    d.text((865,y+58),e,font=font(38,True),fill=(30,30,30))
    d.text((545,y+121),'생산기간 기준',font=font(28),fill=(110,110,110))
rr(d,(72,760,1128,838),18,(236,240,247))
d.text((98,778),'등록연도만으로 확정하지 말고 최종 대상은 리콜센터 조회로 확인',font=font(29,True),fill=(40,72,128))
im.save(OUT/'02-target-period.jpg',quality=88,optimize=True,progressive=True)

# 03 mechanism
im = Image.new('RGB',(W,H),(250,250,250)); d = ImageDraw.Draw(im)
d.text((70,62),'왜 화재위험까지 이어질까',font=font(52,True),fill=(28,28,28))
d.text((70,132),'공식 결함 설명을 흐름으로 보면 이렇게 연결됩니다',font=font(29),fill=(95,95,95))
steps=[('외기온 변화','호스 수축·팽창'),('체결부 변화','클램프 체결력 저하'),('연료 누유','저압연료라인에서 누유 가능'),('결과','주행 중 시동 꺼짐 · 화재 가능성')]
cols=[(57,140,205),(170,115,40),(165,62,62),(174,35,35)]
y=235
for i,(a,b) in enumerate(steps):
    rr(d,(100,y,1100,y+118),26,(255,255,255),outline=(225,225,225),width=2)
    d.ellipse((126,y+26,188,y+88),fill=cols[i])
    d.text((157,y+57),str(i+1),font=font(27,True),fill='white',anchor='mm')
    d.text((220,y+23),a,font=font(34,True),fill=(36,36,36))
    d.text((220,y+66),b,font=font(28),fill=(88,88,88))
    if i < 3:
        d.line((600,y+118,600,y+146),fill=(170,170,170),width=5)
        d.polygon([(590,y+139),(610,y+139),(600,y+153)],fill=(170,170,170))
    y += 154
rr(d,(100,830,1100,878),16,(255,239,236))
d.text((126,839),'중대리콜 분류: “화재위험”',font=font(28,True),fill=(155,30,30))
im.save(OUT/'03-mechanism.jpg',quality=88,optimize=True,progressive=True)

# 04 August vs September
im = Image.new('RGB',(W,H),(248,248,248)); d = ImageDraw.Draw(im)
d.text((70,58),'8월 리콜과 이번 9월 리콜은 별개',font=font(48,True),fill=(28,28,28))
d.text((70,125),'차종명이 겹쳐도 엔진·결함부품·대상 범위가 다릅니다',font=font(29),fill=(92,92,92))
for x,title,color in [(70,'8월 12일 시작',(73,90,120)),(625,'9월 21일 시작',(166,44,44))]:
    rr(d,(x,215,x+505,730),30,(255,255,255),outline=(220,220,220),width=2)
    rr(d,(x+24,240,x+481,308),18,color)
    d.text((x+252,274),title,font=font(31,True),fill='white',anchor='mm')
left=[('대상','G80·G90·GV70·GV80·그랜저'),('엔진','람다3 3.5 가솔린 일부'),('부품','크로스오버파이프 너트'),('규모','127,059대'),('조치','너트 재조임·누유 시 교환')]
right=[('대상','G80·GV70'),('엔진','2.2 디젤 일부'),('부품','저압연료라인 어셈블리'),('규모','10,566대'),('조치','개선품 교환·점검')]
for x,items,kfill in [(98,left,(76,88,108)),(653,right,(152,48,48))]:
    y=340
    for k,v in items:
        d.text((x,y),k,font=font(25,True),fill=kfill)
        d.text((x+112,y),v,font=font(25),fill=(45,45,45))
        y += 73
rr(d,(70,774,1130,850),18,(239,243,248))
d.text((95,791),'한 번 리콜받았더라도 “현재 미조치 리콜”이 또 있는지 차량별 조회 필요',font=font(28,True),fill=(45,72,115))
im.save(OUT/'04-aug-vs-sep.jpg',quality=88,optimize=True,progressive=True)

# 05 action
im = Image.new('RGB',(W,H),(247,247,245)); d = ImageDraw.Draw(im)
d.text((70,60),'대상이라면 이렇게 움직이면 됩니다',font=font(50,True),fill=(28,28,28))
d.text((70,128),'확인 → 예약 → 무상 조치 순서로 간단합니다',font=font(29),fill=(92,92,92))
steps=[('1','대상 조회','자동차리콜센터에서 차량번호 또는 차대번호로 확인'),('2','서비스 예약','현대차 하이테크센터·전국 지정 서비스협력사'),('3','무상 조치','개선된 저압연료라인 교환, 점검 후 관련 부품 추가 교환 가능')]
y=230
for n,t,desc in steps:
    d.ellipse((78,y,158,y+80),fill=(39,98,195))
    d.text((118,y+40),n,font=font(34,True),fill='white',anchor='mm')
    d.text((190,y-2),t,font=font(37,True),fill=(32,32,32))
    d.text((190,y+50),desc,font=font(27),fill=(88,88,88))
    if n != '3': d.line((118,y+94,118,y+145),fill=(173,173,173),width=5)
    y += 190
rr(d,(70,770,1130,858),18,(255,241,238),outline=(232,205,200),width=2)
d.text((95,789),'작업시간 약 1시간 이상 · 비용 전액 무상 · 중대리콜은 장기 미조치 주의',font=font(27,True),fill=(151,44,44))
im.save(OUT/'05-action.jpg',quality=88,optimize=True,progressive=True)

print('generated', [p.name for p in sorted(OUT.glob('*.jpg'))])
