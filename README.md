# 📰 이교장 뉴스레터

매일 아침 AI가 자동으로 뉴스를 수집하고, TTS 팟캐스트를 생성하여 배포하는 데일리 뉴스레터 서비스입니다.

## 🌐 배포 URL

| 환경 | URL |
|------|-----|
| **Vercel (메인)** | [lee-newsletter.vercel.app](https://lee-newsletter.vercel.app) |
| **관리자 페이지** | [lee-newsletter.vercel.app/admin.html](https://lee-newsletter.vercel.app/admin.html) |
| **GitHub Pages** | [vip7612-maker.github.io/---](https://vip7612-maker.github.io/---/) |

## ✨ 주요 기능

### 메인 페이지
- **고정 네비게이션 바** – 왼쪽: 브랜드명, 오른쪽: 키워드 관리 버튼
- **팟캐스트 플레이어** – 매일 자동 생성되는 TTS 뉴스 오디오 재생
- **큐레이션 갤러리** – 관심도 점수별 뉴스 카드 그리드
- **CTA 섹션** – "나만의 뉴스레터" 월 ₩9,900 구독 서비스 신청

### 관리자 페이지 (`/admin.html`)
- **키워드 관리** – 뉴스 검색용 키워드 추가/삭제
- **팟캐스트 설정** – TTS 음성 선택, 길이 설정
- **구독자 관리** – 이메일/문자 구독자 목록
- **브랜드 설정** – 뉴스레터 이름, 태그라인, 연락처

### 자동화 (GitHub Actions)
- **매일 05:00 KST** 자동 실행 (`cron: '0 20 * * *'`)
- Google News RSS에서 키워드 기반 뉴스 수집
- OpenAI API로 팟캐스트 스크립트 생성 (없으면 간단 요약 모드)
- edge-tts로 한국어 TTS 오디오(MP3) 생성
- 자동 커밋 & 푸시 → Vercel 자동 재배포

## 📁 프로젝트 구조

```
이교장 뉴스레터/
├── index.html                 # 메인 페이지
├── admin.html                 # 관리자 페이지
├── css/
│   ├── style.css              # 메인 스타일
│   └── admin.css              # 관리자 스타일
├── js/
│   ├── app.js                 # 메인 로직 (오디오 플레이어, 갤러리, CTA)
│   └── admin.js               # 관리자 로직 (키워드 CRUD, 설정)
├── assets/
│   ├── header.png             # 헤더 배너 이미지
│   └── podcast/
│       └── latest.mp3         # 최신 팟캐스트 오디오
├── data/
│   └── keywords.json          # 키워드 & 설정 데이터
├── scripts/
│   └── generate_podcast.py    # 뉴스 수집 + AI 요약 + TTS 생성
├── .github/
│   └── workflows/
│       └── daily-podcast.yml  # GitHub Actions 워크플로우
└── requirements.txt           # Python 패키지 의존성
```

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| 프론트엔드 | HTML, CSS, JavaScript (바닐라) |
| 폰트 | Noto Sans KR (Google Fonts) |
| TTS | edge-tts (Microsoft Edge TTS, 무료) |
| 뉴스 수집 | Google News RSS + feedparser |
| AI 요약 | OpenAI GPT-4o-mini (선택, 없으면 간단 요약) |
| CI/CD | GitHub Actions |
| 배포 | Vercel, GitHub Pages |

## 🚀 로컬 개발

```bash
# 의존성 설치 (팟캐스트 생성용)
pip3 install -r requirements.txt

# 로컬 서버 실행
npx serve .

# 팟캐스트 수동 생성
python3 scripts/generate_podcast.py
```

## ⚙️ GitHub Actions 설정

자동화를 활성화하려면 GitHub 리포지토리 Settings → Secrets에 다음 시크릿을 등록하세요:

| 시크릿 | 필수 | 설명 |
|--------|------|------|
| `OPENAI_API_KEY` | 선택 | OpenAI API 키 (없으면 간단 요약 모드) |

> 수동 실행: Actions 탭 → "Daily Podcast Generator" → "Run workflow"

## 📊 키워드 설정 (`data/keywords.json`)

```json
{
    "keywords": ["AI 교육", "에듀테크", "학교 디지털 전환"],
    "voice": "ko-KR-SunHiNeural",
    "duration_minutes": 3,
    "updated_at": "2026-03-17T08:00:00+09:00"
}
```

### 사용 가능한 TTS 음성
- `ko-KR-SunHiNeural` – 한국어 여성 (기본)
- `ko-KR-InJoonNeural` – 한국어 남성
- `ko-KR-HyunsuNeural` – 한국어 남성

## 📝 향후 개발 계획

- [ ] GitHub API 연동으로 관리자 페이지 → keywords.json 직접 수정
- [ ] 구독자 관리 기능 실제 연동 (이메일/SMS 발송)
- [ ] 큐레이션 데이터(`data/curated.json`)를 메인 페이지에서 동적 로드
- [ ] 다국어 TTS 지원
- [ ] 팟캐스트 아카이브 (날짜별 이전 에피소드 보관)

---

© 2026 이교장 뉴스레터
