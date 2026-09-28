#!/usr/bin/env python3
"""GitHub Actions relay: five completed Dropbox originals to main, byte-for-byte.

Install as .github/scripts/github_dropbox_relay.py in the image repository,
alongside the workflow in TEMPLATES/GITHUB_DROPBOX_RELAY_WORKFLOW_V1.yml.
Inputs arrive as one JSON workflow_dispatch string in RELAY_PAYLOAD. Never log it.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

REPO = 'qltlf001-creator/naver-blog-images'
MAX_BYTES = 32 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dropbox_host(url):
    parsed = urlparse(url)
    host = (parsed.hostname or '').lower()
    return parsed.scheme == 'https' and (host == 'dropbox.com' or host.endswith('.dropbox.com') or host == 'dropboxusercontent.com' or host.endswith('.dropboxusercontent.com'))


def payload_assets(payload):
    require(isinstance(payload, dict) and set(payload) == {'directory_token', 'assets'}, 'payload must contain directory_token and assets only')
    token = payload['directory_token']
    require(isinstance(token, str) and re.fullmatch(r'[A-Za-z0-9._-]+', token) and token not in {'.', '..'}, 'invalid directory_token')
    assets = payload['assets']
    require(isinstance(assets, list) and len(assets) == 5, 'exactly five assets required')
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
    return assets


def download(item):
    req = Request(item['source_url'], headers={'User-Agent': 'NaverBlogRelay/1.0'})
    with urlopen(req, timeout=60) as response:
        require(dropbox_host(response.geturl()), 'Dropbox download redirected outside Dropbox')
        data = response.read(item['dropbox_size'] + 1)
    require(len(data) == item['dropbox_size'], 'Dropbox size does not match completed receipt')
    require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Dropbox bytes differ from authoritative original SHA-256')
    suffix = Path(item['target_path']).suffix.lower()
    require(data.startswith(b'\x89PNG\r\n\x1a\n') if suffix == '.png' else data.startswith(b'\xff\xd8\xff'), 'file bytes do not match JPG/PNG format')
    return data


def git(*args):
    return subprocess.run(['git', *args], check=True, text=True, capture_output=True).stdout.strip()


def fetch_main_metadata(item, data, token):
    api = f'https://api.github.com/repos/{REPO}/contents/{quote(item["target_path"], safe="/")}?ref=main'
    headers = {'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {token}', 'User-Agent': 'NaverBlogRelay/1.0'}
    with urlopen(Request(api, headers=headers), timeout=30) as response:
        meta = json.load(response)
    expected_url = f'https://raw.githubusercontent.com/{REPO}/main/{item["target_path"]}'
    require(meta.get('download_url') == expected_url, 'main contents download_url is unexpected')
    require(meta.get('size') == len(data), 'main contents size differs from original')
    blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    require(meta.get('sha') == blob, 'main contents Git blob SHA differs from original')
    with urlopen(Request(expected_url, headers={'User-Agent': 'NaverBlogRelay/1.0'}), timeout=30) as response:
        remote = response.read(len(data) + 1)
    require(hashlib.sha256(remote).hexdigest() == item['sha256'], 'main raw bytes SHA-256 differs from original')
    return {'target_path': item['target_path'], 'download_url': meta['download_url'], 'sha256': item['sha256'], 'github_blob_sha': blob}


def main():
    require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'wrong image repository')
    require(git('branch', '--show-current') == 'main', 'checkout must be on main')
    require(bool(os.environ.get('GH_TOKEN')), 'GH_TOKEN required')
    assets = payload_assets(json.loads(os.environ['RELAY_PAYLOAD']))
    verified = [(item, download(item)) for item in assets]
    for item, data in verified:
        path = Path(item['target_path'])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('add', '--', *(item['target_path'] for item, _ in verified))
    changed = subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode
    require(changed in (0, 1), 'git diff failed')
    if changed:
        git('commit', '-m', 'Publish five verified Naver blog assets')
        git('push', 'origin', 'HEAD:main')
        print('RELAY_COMMIT=SUCCESS')
    else:
        print('RELAY_COMMIT=NOOP_SUCCESS')
    records = [fetch_main_metadata(item, data, os.environ['GH_TOKEN']) for item, data in verified]
    receipt = {'schema': 'NAVER_GITHUB_MAIN_RELAY_RECEIPT_V1', 'publication_branch': 'main', 'github_main_metadata_count': len(records), 'assets': records}
    path = Path(os.environ.get('RELAY_RECEIPT_PATH', 'github_main_receipt.json'))
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('GITHUB_MAIN_METADATA_COUNT=5')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print('RELAY_FAILED:', type(exc).__name__, str(exc) if isinstance(exc, ValueError) else 'check workflow credentials and network', file=sys.stderr)
        sys.exit(1)
