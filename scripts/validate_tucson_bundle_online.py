from pathlib import Path
from io import BytesIO
from PIL import Image
import hashlib, json, re, urllib.parse, urllib.request, sys

BASE = 'https://raw.githubusercontent.com/qltlf001-creator/naver-blog-images/main/'
REL = '2026-09/tucson-october-20260928/'
DIR = Path(REL)
ARTICLE = DIR / 'article.html'
PREVIEW = DIR / 'article.preview.html'
MANIFEST = DIR / 'asset_identity.json'
REPORT = DIR / 'validation_report.txt'
FILES = [
    ('01-homefeed', '01-homefeed-tucson-october.jpg'),
    ('02-space', '02-space-packaging.jpg'),
    ('03-powertrain', '03-powertrain.jpg'),
    ('04-digital-safety', '04-digital-safety.jpg'),
    ('05-price-decision', '05-price-decision.jpg'),
]
errors=[]; lines=[]

def ck(cond,msg):
    lines.append(('PASS' if cond else 'FAIL')+': '+msg)
    if not cond: errors.append(msg)

def sha256(data): return hashlib.sha256(data).hexdigest()

def get(url, accept=None):
    headers={'User-Agent':'NAVER-GOLDEN-LOCK/1.0'}
    if accept: headers['Accept']=accept
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read(), dict(r.headers.items())

ck(ARTICLE.is_file(),'article HTML exists')
ck(PREVIEW.is_file(),'independent preview HTML exists')
if not ARTICLE.is_file() or not PREVIEW.is_file():
    REPORT.write_text('\n'.join(lines)+'\nCONVERGENCE_PASS=NO\n',encoding='utf-8'); sys.exit(1)

ab=ARTICLE.read_bytes(); article=ab.decode('utf-8'); preview=PREVIEW.read_text(encoding='utf-8')
article_sha=sha256(ab)
ck(f'name="naver-article-sha256" content="{article_sha}"' in preview,'preview SHA-256 binding matches article bytes')
for token in ['id="copyBodyBtn"','id="selectBodyBtn"','id="copyTitleBtn"','selectNodeContents(article)',"execCommand('copy')"]:
    ck(token in preview,f'preview copy contract token present: {token}')
ck('max-width:760px' in article.replace(' ',''),'article 760px profile')
ck('font-size:17px' in article.replace(' ',''),'article 17px profile')
ck('line-height:1.9' in article.replace(' ',''),'article 1.9 line-height profile')
ck(len(re.findall(r'<blockquote\b',article,re.I)) in (3,4,5),'blockquote count 3-5')
ck(len(re.findall(r'<table\b',article,re.I))==0,'no table callouts')

html_urls=re.findall(r'<img\b[^>]*src=["\']([^"\']+)["\']',article,re.I|re.S)
ck(len(html_urls)==5,f'article exactly five image URLs: {len(html_urls)}')
assets=[]
for idx,(role,name) in enumerate(FILES,1):
    p=DIR/name
    url=BASE+REL+name
    ck(p.is_file(),f'asset {idx} authoritative original exists: {p}')
    if not p.is_file(): continue
    local=p.read_bytes(); local_sha=sha256(local)
    ck(len(local)>=120000,f'asset {idx} local bytes >=120KB: {len(local)}')
    im=Image.open(BytesIO(local)); w,h=im.size
    ck(w>=1200 and h>=675,f'asset {idx} local dimensions >=1200x675: {w}x{h}')
    ck(1.55 <= w/h <= 1.90,f'asset {idx} premium wide ratio: {w/h:.3f}')
    api='https://api.github.com/repos/qltlf001-creator/naver-blog-images/contents/'+urllib.parse.quote(REL+name,safe='/')+'?ref=main'
    try:
        meta_raw,_=get(api,'application/vnd.github+json'); meta=json.loads(meta_raw.decode('utf-8'))
        ck(meta.get('download_url')==url,f'asset {idx} metadata download_url equals HTML URL')
        ck(meta.get('size')==len(local),f'asset {idx} metadata size equals local bytes')
        blob=str(meta.get('sha',''))
        ck(bool(re.fullmatch(r'[0-9a-f]{40}',blob)),f'asset {idx} Git blob SHA resolved')
        remote,headers=get(url); remote_sha=sha256(remote)
        ck(remote_sha==local_sha,f'asset {idx} raw SHA-256 equals authoritative original')
        ck(len(remote)==len(local),f'asset {idx} raw byte length equals original')
        ctype=headers.get('Content-Type','') or headers.get('content-type','')
        ck(ctype.startswith('image/'),f'asset {idx} raw content-type image/*')
        assets.append({'role':role,'authoritative_original':name,'sha256':local_sha,'download_url':url,'github_blob_sha':blob,'size':len(local),'width':w,'height':h})
    except Exception as e:
        ck(False,f'asset {idx} remote identity check failed: {e}')

expected=[BASE+REL+n for _,n in FILES]
ck(html_urls==expected,'HTML img src order exactly equals verified asset sequence')
ck(len(assets)==5,'five identity-verified assets resolved')
manifest={'schema':'NAVER_ASSET_IDENTITY_MANIFEST_V1','article_sha256':article_sha,'assets':assets}
MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if errors:
    lines += ['', 'GOLDEN_SOURCE_LOCK=PASS / EXTERNAL_ENFORCEMENT_LOCK=FAIL / GOLDEN_RESULT=FAIL', 'ASSET_IDENTITY_PASS=NO / PREVIEW_BINDING_PASS=YES / CONVERGENCE_PASS=NO', f'FAIL_COUNT={len(errors)}']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines)); sys.exit(1)
lines += ['', 'GOLDEN_SOURCE_LOCK=PASS / EXTERNAL_ENFORCEMENT_LOCK=PASS / GOLDEN_RESULT=PASS', 'ASSET_IDENTITY_PASS=YES / PREVIEW_BINDING_PASS=YES / CONVERGENCE_PASS=YES']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines))
