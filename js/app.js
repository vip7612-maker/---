/* ==================================================
   이교장 뉴스레터 – App Logic
   ================================================== */

// ──────── 샘플 큐레이션 데이터 ────────
const CURATED_ITEMS = [
    {
        title: "AI가 바꾸는 교육의 미래 – 2026 트렌드 보고서",
        description: "인공지능 기반 맞춤형 학습이 전 세계 교육 현장을 어떻게 변화시키고 있는지 분석합니다.",
        thumbnail: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&h=340&fit=crop",
        badge: "core",
        score: 98,
        url: "https://youtube.com",
        source: "YouTube"
    },
    {
        title: "구글, 차세대 Gemini 모델 공개 – 교육 분야 적용 확대",
        description: "구글이 새롭게 발표한 AI 모델이 교육 현장에서 어떤 잠재력을 지니는지 살펴봅니다.",
        thumbnail: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=340&fit=crop",
        badge: "core",
        score: 95,
        url: "https://blog.google",
        source: "Google Blog"
    },
    {
        title: "학교 현장 디지털 전환 성공 사례 5가지",
        description: "국내외 학교들이 디지털 도구를 활용해 수업 효율을 높인 실제 사례를 소개합니다.",
        thumbnail: "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&h=340&fit=crop",
        badge: "core",
        score: 92,
        url: "https://example.com",
        source: "EdTech Review"
    },
    {
        title: "학부모가 알아야 할 AI 리터러시 교육",
        description: "자녀의 AI 시대 역량을 키우기 위해 학부모가 미리 알아두면 좋은 핵심 포인트입니다.",
        thumbnail: "https://images.unsplash.com/photo-1588072432836-e10032774350?w=600&h=340&fit=crop",
        badge: "ref",
        score: 88,
        url: "https://example.com",
        source: "교육신문"
    },
    {
        title: "노코드 도구로 학급 관리 앱 만들기",
        description: "교사가 직접 노코드 플랫폼을 활용해 출석, 과제 관리 앱을 만드는 방법을 안내합니다.",
        thumbnail: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&h=340&fit=crop",
        badge: "ref",
        score: 85,
        url: "https://example.com",
        source: "YouTube"
    },
    {
        title: "ChatGPT 활용 수업 설계 가이드",
        description: "생성형 AI를 수업에 효과적으로 통합하는 단계별 설계 방법론을 제시합니다.",
        thumbnail: "https://images.unsplash.com/photo-1655720828018-edd71de41e19?w=600&h=340&fit=crop",
        badge: "core",
        score: 91,
        url: "https://example.com",
        source: "교육 블로그"
    },
    {
        title: "2026 대학 입시 트렌드 분석",
        description: "올해 달라지는 대입 전형과 학생부 종합 평가의 핵심 변화를 정리했습니다.",
        thumbnail: "https://images.unsplash.com/photo-1523050854058-8df90110c476?w=600&h=340&fit=crop",
        badge: "ref",
        score: 82,
        url: "https://example.com",
        source: "입시뉴스"
    },
    {
        title: "메타버스 교실 – 가상현실 수업의 가능성",
        description: "VR·AR 기술을 활용한 몰입형 교육 환경의 최신 동향과 한계를 살펴봅니다.",
        thumbnail: "https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=600&h=340&fit=crop",
        badge: "ref",
        score: 79,
        url: "https://example.com",
        source: "TechCrunch"
    },
    {
        title: "교원 역량 강화를 위한 온라인 연수 플랫폼 비교",
        description: "교사 전문성 개발에 활용할 수 있는 주요 온라인 학습 플랫폼 5곳을 비교 분석합니다.",
        thumbnail: "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=600&h=340&fit=crop",
        badge: "ref",
        score: 76,
        url: "https://example.com",
        source: "한국교육"
    },
    {
        title: "프로젝트 기반 학습(PBL)의 AI 접목 전략",
        description: "PBL 수업에 AI 도구를 융합하여 학생 주도적 탐구를 극대화하는 전략을 제안합니다.",
        thumbnail: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&h=340&fit=crop",
        badge: "core",
        score: 89,
        url: "https://example.com",
        source: "교육연구원"
    }
];

// ──────── 유틸리티 ────────
function formatDate(date) {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${year}년 ${month}월 ${day}일 (${weekday})`;
}

function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

// ──────── 날짜 표시 ────────
function initDates() {
    const today = new Date();
    const dateStr = formatDate(today);

    const headerDate = document.getElementById('today-date');
    if (headerDate) headerDate.textContent = `📅 ${dateStr}`;

    const playerDate = document.getElementById('player-date');
    if (playerDate) playerDate.textContent = dateStr;
}

// ──────── 고정 네비게이션 ────────
function initStickyNav() {
    const nav = document.getElementById('sticky-nav');
    if (!nav) return;

    let lastScrollY = 0;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        if (currentScrollY > 60) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
        lastScrollY = currentScrollY;
    });
}

// ──────── 오디오 플레이어 ────────
function initAudioPlayer() {
    const audio = document.getElementById('audio-element');
    const playBtn = document.getElementById('play-btn');
    const playIcon = document.getElementById('play-icon');
    const pauseIcon = document.getElementById('pause-icon');
    const progressBar = document.getElementById('progress-bar');
    const progressFill = document.getElementById('progress-fill');
    const progressKnob = document.getElementById('progress-knob');
    const currentTimeEl = document.getElementById('current-time');
    const totalTimeEl = document.getElementById('total-time');

    // 오디오 메타데이터 로드 시 전체 시간 표시
    audio.addEventListener('loadedmetadata', () => {
        totalTimeEl.textContent = formatTime(audio.duration);
    });

    // 재생/일시정지
    playBtn.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().catch(err => {
                console.warn('오디오 재생 실패:', err);
            });
        } else {
            audio.pause();
        }
    });

    audio.addEventListener('play', () => {
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
    });

    audio.addEventListener('pause', () => {
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
    });

    // 진행률 업데이트
    audio.addEventListener('timeupdate', () => {
        if (audio.duration) {
            const pct = (audio.currentTime / audio.duration) * 100;
            progressFill.style.width = pct + '%';
            progressKnob.style.left = pct + '%';
            currentTimeEl.textContent = formatTime(audio.currentTime);
        }
    });

    // 재생 종료
    audio.addEventListener('ended', () => {
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        progressFill.style.width = '0%';
        progressKnob.style.left = '0%';
        currentTimeEl.textContent = '0:00';
    });

    // 프로그레스바 클릭 → 시간 이동
    progressBar.addEventListener('click', (e) => {
        if (!audio.duration) return;
        const rect = progressBar.getBoundingClientRect();
        const pct = (e.clientX - rect.left) / rect.width;
        audio.currentTime = pct * audio.duration;
    });
}

// ──────── 갤러리 렌더링 ────────
function renderGallery() {
    const gallery = document.getElementById('gallery');
    if (!gallery) return;

    // 관심도 점수 내림차순 정렬
    const sorted = [...CURATED_ITEMS].sort((a, b) => b.score - a.score);

    gallery.innerHTML = '';

    sorted.forEach((item, index) => {
        const card = document.createElement('a');
        card.className = 'gallery-card';
        card.href = item.url;
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
        card.style.animationDelay = `${index * 0.07}s`;

        const badgeClass = item.badge === 'core' ? 'badge-core' : 'badge-ref';
        const badgeLabel = item.badge === 'core' ? '🎯 핵심' : '💡 참고';

        card.innerHTML = `
            <div class="card-thumbnail">
                <img src="${item.thumbnail}" alt="${item.title}" loading="lazy"
                     onerror="this.style.display='none'">
                <div class="card-score-badge">
                    ⭐ ${item.score}점
                </div>
            </div>
            <div class="card-body">
                <span class="card-badge ${badgeClass}">${badgeLabel}</span>
                <h3 class="card-title">${item.title}</h3>
                <p class="card-description">${item.description}</p>
                <div class="card-footer">
                    <span class="card-source">📰 ${item.source}</span>
                    <span class="card-link-icon">원본 보기 →</span>
                </div>
            </div>
        `;

        gallery.appendChild(card);
    });
}

// ──────── CTA 폼 제출 ────────
function initCTAForm() {
    const form = document.getElementById('cta-form');
    if (!form) return;

    // 전화번호 자동 포맷
    const phoneInput = document.getElementById('cta-phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            if (value.length >= 8) {
                value = value.replace(/(\d{3})(\d{4})(\d{0,4})/, '$1-$2-$3');
            } else if (value.length >= 4) {
                value = value.replace(/(\d{3})(\d{0,4})/, '$1-$2');
            }
            e.target.value = value;
        });
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('cta-name').value;
        const email = document.getElementById('cta-email').value;
        const phone = document.getElementById('cta-phone').value;
        const brand = document.getElementById('cta-brand').value;

        const subject = encodeURIComponent(`[뉴스레터 신청] ${name}님의 나만의 뉴스레터`);
        const body = encodeURIComponent(
            `이름: ${name}\n이메일: ${email}\n연락처: ${phone}\n\n브랜드/주제:\n${brand}`
        );

        window.location.href = `mailto:vip7612@gmail.com?subject=${subject}&body=${body}`;

        // 성공 피드백
        const btn = form.querySelector('.cta-submit-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ 신청 메일이 준비되었습니다!';
        btn.style.background = 'linear-gradient(135deg, #059669, #10b981)';
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
        }, 3000);
    });
}

// ──────── 초기화 ────────
document.addEventListener('DOMContentLoaded', () => {
    initDates();
    initStickyNav();
    initAudioPlayer();
    renderGallery();
    initCTAForm();
});
