/* ==================================================
   이교장 뉴스레터 – App Logic
   ================================================== */

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

function formatViewCount(count) {
    if (!count) return '';
    if (count >= 10000) return `${(count / 10000).toFixed(1)}만회`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}천회`;
    return `${count}회`;
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

// ──────── 유튜브 큐레이션 데이터 로드 ────────
let curatedItems = [];

async function loadCuratedData() {
    try {
        const response = await fetch('data/youtube_curated.json');
        if (!response.ok) throw new Error('데이터 로드 실패');
        const data = await response.json();
        curatedItems = data.items || [];
        renderGallery();
    } catch (err) {
        console.warn('큐레이션 데이터 로드 실패:', err);
        const gallery = document.getElementById('gallery');
        if (gallery) {
            gallery.innerHTML = `
                <div class="gallery-empty">
                    <span class="gallery-empty-icon">📺</span>
                    <p>큐레이션 데이터를 불러올 수 없습니다.</p>
                    <p class="gallery-empty-sub">잠시 후 다시 시도해주세요.</p>
                </div>
            `;
        }
    }
}

// ──────── 갤러리 렌더링 ────────
function renderGallery() {
    const gallery = document.getElementById('gallery');
    if (!gallery || !curatedItems.length) return;

    gallery.innerHTML = '';

    curatedItems.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'gallery-card';
        card.style.animationDelay = `${index * 0.07}s`;
        card.setAttribute('data-index', index);

        const viewStr = formatViewCount(item.viewCount);

        card.innerHTML = `
            <div class="card-thumbnail">
                <img src="${item.thumbnailUrl}" alt="${item.title}" loading="lazy"
                     onerror="this.src='https://i.ytimg.com/vi/${item.videoId}/hqdefault.jpg'">
                <div class="card-play-overlay">
                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                        <circle cx="24" cy="24" r="24" fill="rgba(0,0,0,0.65)"/>
                        <path d="M19 15l14 9-14 9V15z" fill="#fff"/>
                    </svg>
                </div>
                <div class="card-duration-badge">
                    ⏱ ${item.duration}
                </div>
            </div>
            <div class="card-body">
                <h3 class="card-title">${item.title}</h3>
                <div class="card-meta">
                    <span class="card-channel">📺 ${item.channelName}</span>
                    <span class="card-date">📅 ${item.publishedAt}</span>
                </div>
                <div class="card-footer">
                    ${viewStr ? `<span class="card-views">👁 ${viewStr}</span>` : '<span></span>'}
                    <span class="card-link-icon">자세히 보기 →</span>
                </div>
            </div>
        `;

        card.addEventListener('click', () => openModal(index));
        gallery.appendChild(card);
    });
}

// ──────── 팝업 모달 ────────
function openModal(index) {
    const item = curatedItems[index];
    if (!item) return;

    const modal = document.getElementById('video-modal');
    const iframe = document.getElementById('modal-iframe');

    // 유튜브 임베드 URL 설정
    iframe.src = `https://www.youtube.com/embed/${item.videoId}?autoplay=1&rel=0`;

    // 정보 채우기
    document.getElementById('modal-title').textContent = item.title;
    document.getElementById('modal-channel').textContent = `📺 ${item.channelName}`;
    document.getElementById('modal-date').textContent = `📅 ${item.publishedAt}`;
    document.getElementById('modal-duration').textContent = `⏱ ${item.duration}`;

    // 키워드
    const keywordsEl = document.getElementById('modal-keywords');
    keywordsEl.innerHTML = (item.keywords || [])
        .map(k => `<span class="keyword-tag">#${k}</span>`)
        .join('');

    // 추천이유
    document.getElementById('modal-recommendation').textContent =
        item.recommendation || '추천 정보가 없습니다.';

    // 요약
    document.getElementById('modal-summary').textContent =
        item.summary || '요약 정보가 없습니다.';

    // 팝업 열기
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('video-modal');
    const iframe = document.getElementById('modal-iframe');

    modal.classList.remove('active');
    iframe.src = '';
    document.body.style.overflow = '';
}

function initModal() {
    const modal = document.getElementById('video-modal');
    const closeBtn = document.getElementById('modal-close');

    if (!modal || !closeBtn) return;

    // X 버튼 클릭
    closeBtn.addEventListener('click', closeModal);

    // 오버레이 클릭 (모달 콘텐츠 외부)
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // ESC 키
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
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
    loadCuratedData();
    initModal();
    initCTAForm();
});
