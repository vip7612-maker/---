#!/usr/bin/env python3
"""
이교장 뉴스레터 – 데일리 팟캐스트 자동 생성 스크립트

1. data/keywords.json에서 키워드 로드
2. Google News RSS에서 키워드 기반 뉴스 수집
3. OpenAI API로 팟캐스트 스크립트 생성 (없으면 간단 요약)
4. edge-tts로 TTS 오디오 생성
5. assets/podcast/latest.mp3로 저장
6. data/curated.json 업데이트
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

import edge_tts
import feedparser
import requests
from bs4 import BeautifulSoup

# ──────── 경로 설정 ────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "keywords.json")
OUTPUT_AUDIO = os.path.join(BASE_DIR, "assets", "podcast", "latest.mp3")
CURATED_FILE = os.path.join(BASE_DIR, "data", "curated.json")

KST = timezone(timedelta(hours=9))


def load_keywords():
    """키워드 설정 로드"""
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def fetch_news(keywords, max_per_keyword=5):
    """Google News RSS에서 키워드별 뉴스 수집"""
    all_articles = []
    seen_titles = set()

    for keyword in keywords:
        encoded = requests.utils.quote(keyword)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_keyword]:
                title = entry.get('title', '').strip()
                # 중복 제거
                if title in seen_titles:
                    continue
                seen_titles.add(title)

                # 소스 추출 (제목에서 " - 출처" 형식)
                source = ""
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0]
                    source = parts[1] if len(parts) > 1 else ""

                all_articles.append({
                    "title": title,
                    "source": source,
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "keyword": keyword
                })
        except Exception as e:
            print(f"⚠️ 키워드 '{keyword}' 뉴스 수집 실패: {e}")

    # 최신순 정렬
    all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
    return all_articles[:15]  # 최대 15건


def generate_script_with_ai(articles, duration_minutes=3):
    """OpenAI API로 팟캐스트 스크립트 생성"""
    api_key = os.environ.get('OPENAI_API_KEY')

    if not api_key:
        print("⚠️ OPENAI_API_KEY가 설정되지 않음, 간단 요약 사용")
        return generate_simple_script(articles, duration_minutes)

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)

        today = datetime.now(KST).strftime("%Y년 %m월 %d일")
        articles_text = "\n".join([
            f"- [{a['source']}] {a['title']}" for a in articles
        ])

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""당신은 '이교장 뉴스레터 팟캐스트'의 진행자입니다.
오늘 날짜는 {today}입니다.
아래 뉴스 목록을 바탕으로 약 {duration_minutes}분 분량의 한국어 팟캐스트 스크립트를 작성하세요.

규칙:
- 자연스럽고 친근한 말투 사용
- "안녕하세요, 이교장 뉴스레터 팟캐스트입니다"로 시작
- 핵심 뉴스 4~5개를 선별하여 각각 2~3문장으로 설명
- 각 뉴스 사이에 자연스러운 전환 문구 사용
- "이상으로 오늘의 뉴스 브리핑을 마칩니다"로 마무리
- 마크다운이나 특수문자 사용 금지"""
                },
                {
                    "role": "user",
                    "content": f"오늘의 뉴스:\n{articles_text}"
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ AI 스크립트 생성 실패: {e}, 간단 요약 사용")
        return generate_simple_script(articles, duration_minutes)


def generate_simple_script(articles, duration_minutes=3):
    """AI 없이 간단한 팟캐스트 스크립트 생성"""
    today = datetime.now(KST).strftime("%Y년 %m월 %d일")
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    weekday = weekdays[datetime.now(KST).weekday()]

    lines = [
        f"안녕하세요, 이교장 뉴스레터 팟캐스트입니다.",
        f"오늘은 {today} {weekday}요일입니다. 오늘의 주요 뉴스를 전해드리겠습니다.",
        ""
    ]

    for i, article in enumerate(articles[:5]):
        ordinal = ['첫', '두', '세', '네', '다섯'][i] if i < 5 else f'{i+1}'
        lines.append(f"{ordinal} 번째 소식입니다.")
        lines.append(f"{article['title']}.")
        if article['source']:
            lines.append(f"이 소식은 {article['source']}에서 전해드렸습니다.")
        lines.append("")

    lines.extend([
        "이상으로 오늘의 이교장 뉴스레터 팟캐스트를 마칩니다.",
        "더 자세한 내용은 뉴스레터 페이지에서 확인해주세요.",
        "내일도 유익한 소식으로 찾아뵙겠습니다. 감사합니다."
    ])

    return "\n".join(lines)


async def generate_tts(script, voice, output_path):
    """edge-tts로 오디오 생성"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    communicate = edge_tts.Communicate(script, voice, rate="-5%")
    await communicate.save(output_path)


def save_curated(articles):
    """큐레이션 데이터 저장"""
    # 썸네일 URL 목록 (교육 관련 이미지)
    thumbnails = [
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1588072432836-e10032774350?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1655720828018-edd71de41e19?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1523050854058-8df90110c476?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=600&h=340&fit=crop",
        "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&h=340&fit=crop",
    ]

    curated = []
    for i, article in enumerate(articles[:10]):
        score = max(60, 98 - i * 3)
        curated.append({
            "title": article["title"],
            "description": f"{article['source']}에서 보도한 뉴스입니다.",
            "thumbnail": thumbnails[i % len(thumbnails)],
            "badge": "core" if i < 4 else "ref",
            "score": score,
            "url": article["link"],
            "source": article["source"] or "뉴스"
        })

    os.makedirs(os.path.dirname(CURATED_FILE), exist_ok=True)
    with open(CURATED_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "date": datetime.now(KST).strftime("%Y-%m-%d"),
            "items": curated
        }, f, ensure_ascii=False, indent=2)

    print(f"📋 큐레이션 데이터 저장 완료: {len(curated)}건")


async def main():
    print("=" * 50)
    print("🚀 이교장 뉴스레터 데일리 팟캐스트 생성")
    print("=" * 50)

    # 1. 키워드 로드
    config = load_keywords()
    keywords = config.get('keywords', ['AI 교육', '에듀테크'])
    voice = config.get('voice', 'ko-KR-SunHiNeural')
    duration = config.get('duration_minutes', 3)

    print(f"📌 키워드: {', '.join(keywords)}")
    print(f"🎙️ 음성: {voice}, 목표 길이: {duration}분")

    # 2. 뉴스 수집
    print("\n📡 뉴스 수집 중...")
    articles = fetch_news(keywords)
    print(f"✅ {len(articles)}건 수집 완료")

    if not articles:
        print("❌ 수집된 뉴스가 없습니다. 종료합니다.")
        sys.exit(1)

    for a in articles[:5]:
        print(f"  • [{a['source']}] {a['title']}")

    # 3. 팟캐스트 스크립트 생성
    print("\n✍️ 팟캐스트 스크립트 생성 중...")
    script = generate_script_with_ai(articles, duration)
    print(f"✅ 스크립트 생성 완료 ({len(script)}자)")

    # 4. TTS 오디오 생성
    print(f"\n🎧 TTS 오디오 생성 중 (음성: {voice})...")
    await generate_tts(script, voice, OUTPUT_AUDIO)
    size_kb = os.path.getsize(OUTPUT_AUDIO) / 1024
    print(f"✅ 오디오 생성 완료: {size_kb:.1f} KB")

    # 5. 큐레이션 데이터 저장
    save_curated(articles)

    print("\n🎉 데일리 팟캐스트 생성 완료!")


if __name__ == "__main__":
    asyncio.run(main())
