#!/usr/bin/env python3
"""Secure Dropbox -> GitHub relay with encrypted queue automation.

Bootstrap mode (one time): if no valid payload/queue and no relay key exists,
generate a public certificate committed to main and place the private key only in
an Actions artifact payload. Normal mode decrypts a queued CMS payload, downloads
five Dropbox originals, verifies bytes, publishes to main, and verifies raw URLs.
"""

import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile

REPO = 'qltlf001-creator/naver-blog-images'
MAX_BYTES = 32 * 1024 * 1024
RELAY_DIR = Path('.github/relay')
QUEUE_DIR = RELAY_DIR / 'queue'
PUBLIC_CERT = RELAY_DIR / 'public.crt'
BOOTSTRAP = RELAY_DIR / 'bootstrap.json'
PROCESSED = RELAY_DIR / 'processed.json'
RECEIPT = Path(os.environ.get('RELAY_RECEIPT_PATH', 'github_main_receipt.json'))
KEY_BUNDLE = Path('relay_key_bundle.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dropbox_host(url):
    parsed = urlparse(url)
    host = (parsed.hostname or '').lower()
    return parsed.scheme == 'https' and (
        host == 'dropbox.com' or host.endswith('.dropbox.com') or
        host == 'dropboxusercontent.com' or host.endswith('.dropboxusercontent.com')
    )


def git(*args):
    return subprocess.run(['git', *args], check=True, text=True, capture_output=True).stdout.strip()


def git_identity():
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')


def commit_push(paths, message):
    git_identity()
    git('add', '--', *[str(p) for p in paths])
    changed = subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode
    require(changed in (0, 1), 'git diff failed')
    if not changed:
        return 'NOOP_SUCCESS'
    git('commit', '-m', message)
    git('push', 'origin', 'HEAD:main')
    return 'SUCCESS'


def gh_headers():
    token = os.environ.get('GH_TOKEN', '')
    require(bool(token), 'GH_TOKEN required')
    return {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'User-Agent': 'NaverBlogRelay/2.0',
        'X-GitHub-Api-Version': '2022-11-28',
    }


def gh_json(url):
    with urlopen(Request(url, headers=gh_headers()), timeout=30) as response:
        return json.load(response)


def artifact_zip(run_id, artifact_name):
    listing = gh_json(f'https://api.github.com/repos/{REPO}/actions/runs/{run_id}/artifacts?per_page=100')
    for artifact in listing.get('artifacts', []):
        if artifact.get('name') == artifact_name and not artifact.get('expired'):
            target = Path('/tmp/naver-relay-key-artifact.zip')
            token = os.environ.get('GH_TOKEN', '')
            subprocess.run([
                'curl', '-fL', '--retry', '2', '--silent', '--show-error',
                '-H', f'Authorization: Bearer {token}',
                '-H', 'Accept: application/vnd.github+json',
                '-H', 'X-GitHub-Api-Version: 2022-11-28',
                artifact['archive_download_url'], '-o', str(target)
            ], check=True)
            return target.read_bytes()
    return None


def decode_key_bundle(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        candidates = [n for n in archive.namelist() if n.endswith('.json')]
        require(bool(candidates), 'relay key artifact has no JSON bundle')
        for name in candidates:
            try:
                data = json.loads(archive.read(name).decode('utf-8'))
            except Exception:
                continue
            key = data.get('relay_private_key_b64')
            if key:
                return base64.b64decode(key)
    raise ValueError('relay private key missing from artifact')


def load_private_key():
    require(BOOTSTRAP.exists(), 'relay bootstrap metadata missing')
    config = json.loads(BOOTSTRAP.read_text(encoding='utf-8'))
    records = config.get('key_artifacts', [])
    require(isinstance(records, list) and records, 'relay key artifact list missing')
    for record in records:
        try:
            run_id = int(record['run_id'])
            name = str(record['name'])
            blob = artifact_zip(run_id, name)
            if blob:
                return decode_key_bundle(blob), config
        except Exception:
            continue
    raise ValueError('no usable relay key artifact; bootstrap recovery required')


def write_key_bundle(private_key):
    payload = {
        'schema': 'NAVER_RELAY_KEY_BUNDLE_V1',
        'relay_private_key_b64': base64.b64encode(private_key).decode('ascii'),
        'public_cert_sha256': hashlib.sha256(PUBLIC_CERT.read_bytes()).hexdigest(),
    }
    KEY_BUNDLE.write_text(json.dumps(payload, ensure_ascii=False) + '\n', encoding='utf-8')


def bootstrap():
    RELAY_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    require(not PUBLIC_CERT.exists() and not BOOTSTRAP.exists(), 'relay already bootstrapped')
    private_path = Path('/tmp/naver-relay-private.pem')
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:3072', '-sha256', '-days', '3650', '-nodes',
        '-subj', '/CN=NaverBlogRelay', '-keyout', str(private_path), '-out', str(PUBLIC_CERT)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    private_key = private_path.read_bytes()
    run_id = int(os.environ['GITHUB_RUN_ID'])
    config = {
        'schema': 'NAVER_RELAY_BOOTSTRAP_V1',
        'key_artifacts': [{'run_id': run_id, 'name': 'github-main-receipt'}],
    }
    BOOTSTRAP.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    RECEIPT.write_text(json.dumps({
        'schema': 'NAVER_RELAY_BOOTSTRAP_ARTIFACT_V1',
        'relay_private_key_b64': base64.b64encode(private_key).decode('ascii'),
        'public_cert_sha256': hashlib.sha256(PUBLIC_CERT.read_bytes()).hexdigest(),
    }, ensure_ascii=False) + '\n', encoding='utf-8')
    result = commit_push([PUBLIC_CERT, BOOTSTRAP], 'Bootstrap secure Naver Dropbox relay')
    print(f'RELAY_BOOTSTRAP={result}')


def processed_paths():
    if not PROCESSED.exists():
        return []
    data = json.loads(PROCESSED.read_text(encoding='utf-8'))
    value = data.get('processed', [])
    return value if isinstance(value, list) else []


def find_unprocessed_queue():
    if not QUEUE_DIR.exists():
        return None
    done = set(processed_paths())
    pending = [p for p in sorted(QUEUE_DIR.glob('*.payload')) if str(p) not in done]
    require(len(pending) <= 1, 'multiple unprocessed relay queue files')
    return pending[0] if pending else None


def relay_queue_text(path):
    raw = path.read_text(encoding='ascii').strip()
    if re.fullmatch(r'blob:[0-9a-f]{40}', raw):
        blob_sha = raw.split(':', 1)[1]
        record = gh_json(f'https://api.github.com/repos/{REPO}/git/blobs/{blob_sha}')
        require(record.get('encoding') == 'base64', 'relay blob encoding must be base64')
        try:
            raw = base64.b64decode(record.get('content', '')).decode('ascii').strip()
        except Exception as exc:
            raise ValueError('relay blob content is invalid') from exc
    return raw


def decrypt_queue(path):
    private_key, config = load_private_key()
    require(PUBLIC_CERT.exists(), 'relay public certificate missing')
    cms_path = Path('/tmp/naver-relay-payload.cms')
    key_path = Path('/tmp/naver-relay-private.pem')
    out_path = Path('/tmp/naver-relay-payload.json')
    try:
        cms_path.write_bytes(base64.b64decode(relay_queue_text(path), validate=True))
    except Exception as exc:
        raise ValueError('encrypted relay queue is invalid') from exc
    key_path.write_bytes(private_key)
    subprocess.run([
        'openssl', 'cms', '-decrypt', '-binary', '-inform', 'DER',
        '-in', str(cms_path), '-recip', str(PUBLIC_CERT), '-inkey', str(key_path), '-out', str(out_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    payload = json.loads(out_path.read_text(encoding='utf-8'))
    return payload, private_key, config


def payload_assets(payload):
    require(isinstance(payload, dict) and set(payload) == {'directory_token', 'assets'}, 'payload must contain directory_token and assets only')
    token = payload['directory_token']
    require(isinstance(token, str) and re.fullmatch(r'[A-Za-z0-9._-]+', token) and token not in {'.', '..'}, 'invalid directory_token')
    assets = payload['assets']
    require(isinstance(assets, list) and len(assets) in (4, 5), 'four or five assets required')
    seen = set()
    for index, item in enumerate(assets, 1):
        require(isinstance(item, dict), f'asset {index}: object required')
        require(item.get('dropbox_upload_status') == 'completed', f'asset {index}: Dropbox upload not completed')
        require(bool(re.fullmatch(r'id:[A-Za-z0-9_-]+', str(item.get('dropbox_file_id', '')))), f'asset {index}: Dropbox file ID missing')
        require(dropbox_host(str(item.get('source_url', ''))), f'asset {index}: Dropbox HTTPS source URL required')
        require(bool(re.fullmatch(r'[a-f0-9]{64}', str(item.get('sha256', '')))), f'asset {index}: SHA-256 required')
        size = item.get('dropbox_size')
        require(type(size) is int and 0 < size <= MAX_BYTES, f'asset {index}: invalid Dropbox size')
        target = item.get('target_path')
        require(isinstance(target, str) and re.fullmatch(rf'{re.escape(token)}/[A-Za-z0-9._-]+\.(?:jpg|jpeg|png)', target, re.I), f'asset {index}: unsafe target path')
        require(target not in seen and Path(target).name.startswith(f'{index:02d}-'), f'asset {index}: duplicate or out-of-order target')
        seen.add(target)
    return token, assets


def download(item):
    req = Request(item['source_url'], headers={'User-Agent': 'NaverBlogRelay/2.0'})
    with urlopen(req, timeout=60) as response:
        require(dropbox_host(response.geturl()), 'Dropbox download redirected outside Dropbox')
        data = response.read(item['dropbox_size'] + 1)
    require(len(data) == item['dropbox_size'], 'Dropbox size does not match completed receipt')
    require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Dropbox bytes differ from authoritative original SHA-256')
    suffix = Path(item['target_path']).suffix.lower()
    require(data.startswith(b'\x89PNG\r\n\x1a\n') if suffix == '.png' else data.startswith(b'\xff\xd8\xff'), 'file bytes do not match JPG/PNG format')
    return data


def fetch_main_metadata(item, data):
    api = f'https://api.github.com/repos/{REPO}/contents/{quote(item["target_path"], safe="/")}?ref=main'
    meta = gh_json(api)
    expected_url = f'https://raw.githubusercontent.com/{REPO}/main/{item["target_path"]}'
    require(meta.get('download_url') == expected_url, 'main contents download_url is unexpected')
    require(meta.get('size') == len(data), 'main contents size differs from original')
    blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    require(meta.get('sha') == blob, 'main contents Git blob SHA differs from original')
    with urlopen(Request(expected_url, headers={'User-Agent': 'NaverBlogRelay/2.0'}), timeout=30) as response:
        remote = response.read(len(data) + 1)
    require(hashlib.sha256(remote).hexdigest() == item['sha256'], 'main raw bytes SHA-256 differs from original')
    return {'target_path': item['target_path'], 'download_url': meta['download_url'], 'sha256': item['sha256'], 'github_blob_sha': blob}


def update_bootstrap(config, private_key):
    current = {'run_id': int(os.environ['GITHUB_RUN_ID']), 'name': 'relay-key-bundle'}
    records = [current]
    for item in config.get('key_artifacts', []):
        if item not in records:
            records.append(item)
    config['key_artifacts'] = records[:4]
    BOOTSTRAP.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_key_bundle(private_key)


def main():
    require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'wrong image repository')
    require(git('branch', '--show-current') == 'main', 'checkout must be on main')
    gh_headers()

    raw = os.environ.get('RELAY_PAYLOAD', '').strip()
    payload = None
    queue_path = find_unprocessed_queue()
    private_key = None
    config = None

    if raw:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = None

    if payload is None and queue_path is not None:
        payload, private_key, config = decrypt_queue(queue_path)

    if payload is None:
        if not PUBLIC_CERT.exists() and not BOOTSTRAP.exists():
            bootstrap()
            return
        raise ValueError('no valid relay payload or unprocessed encrypted queue')

    token, assets = payload_assets(payload)
    verified = [(item, download(item)) for item in assets]
    for item, data in verified:
        path = Path(item['target_path'])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    commit_paths = [Path(item['target_path']) for item, _ in verified]
    if queue_path is not None:
        done = processed_paths()
        if str(queue_path) not in done:
            done.append(str(queue_path))
        PROCESSED.parent.mkdir(parents=True, exist_ok=True)
        PROCESSED.write_text(json.dumps({'schema': 'NAVER_RELAY_PROCESSED_V1', 'processed': done}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        commit_paths.append(PROCESSED)
        require(private_key is not None and config is not None, 'relay key state missing')
        update_bootstrap(config, private_key)
        commit_paths.append(BOOTSTRAP)

    result = commit_push(commit_paths, f'Publish {len(verified)} verified Naver blog assets')
    print(f'RELAY_COMMIT={result}')

    records = [fetch_main_metadata(item, data) for item, data in verified]
    receipt = {
        'schema': 'NAVER_GITHUB_MAIN_RELAY_RECEIPT_V2',
        'publication_branch': 'main',
        'directory_token': token,
        'github_main_metadata_count': len(records),
        'assets': records,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'GITHUB_MAIN_METADATA_COUNT={len(records)}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        if isinstance(exc, ValueError):
            detail = str(exc)
        else:
            detail = 'check workflow credentials, relay key artifact, and network'
        print('RELAY_FAILED:', type(exc).__name__, detail, file=sys.stderr)
        sys.exit(1)
