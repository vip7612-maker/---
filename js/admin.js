/* ==================================================
   이교장 뉴스레터 – Admin Dashboard Logic
   ================================================== */

// ──────── GitHub API 설정 ────────
const GITHUB_OWNER = 'vip7612-maker';
const GITHUB_REPO = '---';
const KEYWORDS_PATH = 'data/keywords.json';

// ──────── 상태 ────────
let keywordsData = {
    keywords: [],
    voice: 'ko-KR-SunHiNeural',
    duration_minutes: 3,
    updated_at: ''
};
let keywordsSha = null;

// ──────── 초기화 ────────
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMobileMenu();
    loadKeywords();
    initKeywordForm();
    initSettingsForms();
});

// ──────── 네비게이션 ────────
function initNavigation() {
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            if (!section) return;

            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
            const target = document.getElementById(`section-${section}`);
            if (target) target.classList.add('active');

            // 모바일: 사이드바 닫기
            closeMobileMenu();
        });
    });
}

// ──────── 모바일 메뉴 ────────
function initMobileMenu() {
    const toggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (toggle) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeMobileMenu);
    }
}

function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
}

// ──────── 키워드 로드 (로컬 fetch) ────────
async function loadKeywords() {
    try {
        // 로컬 JSON 파일에서 로드 시도
        const res = await fetch('data/keywords.json');
        if (res.ok) {
            keywordsData = await res.json();
        }
    } catch (e) {
        console.warn('키워드 로드 실패, 기본값 사용:', e);
    }

    renderKeywords();
    updateAutomationStatus();
}

// ──────── 키워드 렌더링 ────────
function renderKeywords() {
    const list = document.getElementById('keywords-list');
    const count = document.getElementById('keyword-count');

    if (!list) return;

    count.textContent = `${keywordsData.keywords.length}개`;

    if (keywordsData.keywords.length === 0) {
        list.innerHTML = '<p style="color:#6b7280;font-size:0.85rem;">등록된 키워드가 없습니다.</p>';
        return;
    }

    list.innerHTML = keywordsData.keywords.map((kw, i) => `
        <span class="keyword-tag">
            ${kw}
            <button class="keyword-remove" data-index="${i}" title="삭제">✕</button>
        </span>
    `).join('');

    // 삭제 이벤트
    list.querySelectorAll('.keyword-remove').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.index);
            keywordsData.keywords.splice(idx, 1);
            keywordsData.updated_at = new Date().toISOString();
            renderKeywords();
            saveKeywordsLocal();
            showToast('키워드가 삭제되었습니다');
        });
    });
}

// ──────── 키워드 추가 폼 ────────
function initKeywordForm() {
    const input = document.getElementById('new-keyword');
    const btn = document.getElementById('add-keyword-btn');

    if (!btn || !input) return;

    const addKeyword = () => {
        const value = input.value.trim();
        if (!value) return;
        if (keywordsData.keywords.includes(value)) {
            showToast('이미 등록된 키워드입니다');
            return;
        }
        keywordsData.keywords.push(value);
        keywordsData.updated_at = new Date().toISOString();
        input.value = '';
        renderKeywords();
        saveKeywordsLocal();
        showToast(`"${value}" 키워드가 추가되었습니다`);
    };

    btn.addEventListener('click', addKeyword);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addKeyword();
        }
    });
}

// ──────── 설정 폼 ────────
function initSettingsForms() {
    // 팟캐스트 설정 저장
    const savePodcast = document.getElementById('save-podcast-settings');
    if (savePodcast) {
        // 초기값 설정
        const voiceSelect = document.getElementById('voice-select');
        const durationSelect = document.getElementById('duration-select');
        if (voiceSelect) voiceSelect.value = keywordsData.voice || 'ko-KR-SunHiNeural';
        if (durationSelect) durationSelect.value = String(keywordsData.duration_minutes || 3);

        savePodcast.addEventListener('click', () => {
            keywordsData.voice = voiceSelect.value;
            keywordsData.duration_minutes = parseInt(durationSelect.value);
            keywordsData.updated_at = new Date().toISOString();
            saveKeywordsLocal();
            showToast('팟캐스트 설정이 저장되었습니다');
        });
    }

    // 브랜드 설정 저장
    const saveBrand = document.getElementById('save-brand-settings');
    if (saveBrand) {
        saveBrand.addEventListener('click', () => {
            showToast('브랜드 설정이 저장되었습니다');
        });
    }
}

// ──────── 로컬 저장 (localStorage) ────────
function saveKeywordsLocal() {
    try {
        localStorage.setItem('newsletter_keywords', JSON.stringify(keywordsData));
    } catch (e) {
        console.warn('로컬 저장 실패:', e);
    }
    updateAutomationStatus();
}

// ──────── 자동화 상태 업데이트 ────────
function updateAutomationStatus() {
    const lastUpdated = document.getElementById('last-updated');
    if (lastUpdated && keywordsData.updated_at) {
        const d = new Date(keywordsData.updated_at);
        lastUpdated.textContent = formatDate(d);
    }

    // 다음 실행 계산
    const nextRun = document.getElementById('next-run');
    if (nextRun) {
        const now = new Date();
        const next = new Date(now);
        next.setHours(5, 0, 0, 0);
        if (now >= next) next.setDate(next.getDate() + 1);

        const diff = next - now;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        if (hours > 0) {
            nextRun.textContent = `약 ${hours}시간 ${minutes}분 후 (오전 5:00)`;
        } else {
            nextRun.textContent = `약 ${minutes}분 후 (오전 5:00)`;
        }
    }
}

// ──────── 유틸리티 ────────
function formatDate(date) {
    const y = date.getFullYear();
    const m = date.getMonth() + 1;
    const d = date.getDate();
    const h = date.getHours();
    const min = String(date.getMinutes()).padStart(2, '0');
    return `${y}년 ${m}월 ${d}일 ${h}:${min}`;
}

// ──────── 토스트 알림 ────────
function showToast(message) {
    // 기존 토스트 제거
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}
