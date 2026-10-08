# 스포츠 블로그 3편 — 이미지 승인 기록

- 기준일: 2026-10-09
- 승인 상태: **APPROVED** (원본 PNG 9개, KBO / 다저스 / 김민솔 각 3장)
- 로컬 검증: 9/9 SHA-256 및 바이트 길이 일치
- 본문 3개 및 이미지 배치표: 로컬 발행 패키지 작성 완료
- 원격 GitHub 이미지 업로드: **NOT_EXECUTED / UNVERIFIED**
- GitHub 공개 이미지 URL: **UNVERIFIED**
- 네이버 SmartEditor 직접 업로드: **USER_ACTION_REQUIRED**

## 승인 이미지 목록

**KBO**
1. `kbo_01_cover.png` — 와일드카드 4·5위 조건
2. `kbo_02_home.png` — 홈구장 조건
3. `kbo_03_bracket.png` — 포스트시즌 라운드

**다저스**
1. `dodgers_01_cover.png` — 7회 2타점 안타
2. `dodgers_02_7th.png` — 승부 흐름
3. `dodgers_03_next.png` — 다음 상대 밀워키

**김민솔**
1. `golf_01_cover.png` — 버디 8개 / 15점
2. `golf_02_scoring.png` — 점수제
3. `golf_03_15points.png` — 계산 구조

자세한 바이트 크기·원본 SHA-256·예정 GitHub 경로는 [승인 매니페스트](./asset_manifest_APPROVED.json)를 확인하세요.

원본 PNG가 실제 `main` 브랜치에 업로드된 뒤, 원격 SHA-256 및 반환된 공개 HTTPS raw 주소를 대조해야만 업로드 완료로 변경합니다. 이 README와 매니페스트 등록은 이미지 자체가 업로드되었다는 의미가 아닙니다.

이미지는 실제 경기 사진을 대체하는 증거가 아닌 블로그용 제작 그래픽입니다.

## GitHub 자동 무결성 검사

GitHub `main`에 이 폴더의 PNG가 업로드되면 [검증 워크플로](../../.github/workflows/verify_sports_approved_assets_20261009.yml)가 9개 파일의 이름·크기·SHA-256을 승인 매니페스트와 대조합니다. 워크플로가 PASS하더라도 공개 raw HTTPS 주소의 접근성은 별도로 확인해야 합니다.
