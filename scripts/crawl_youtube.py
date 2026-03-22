#!/usr/bin/env python3
"""
이교장 뉴스레터 – 유튜브 큐레이션 크롤링 스크립트

1. data/keywords.json에서 키워드 로드
2. yt-dlp로 각 키워드별 유튜브 영상 검색
3. OpenAI API로 키워드, 추천이유, 요약 생성 (없으면 영상 설명 발췌)
4. data/youtube_curated.json에 저장
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "keywords.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "youtube_curated.json")


def load_keywords():
    """키워드 설정 로드"""
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_youtube(keyword, max_results=5):
    """yt-dlp로 유튜브 검색"""
    search_url = f"ytsearch{max_results}:{keyword}"

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--dump-json",
        "--no-download",
        "--flat-playlist",
        search_url
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"  ⚠️ yt-dlp 검색 실패: {result.stderr[:200]}")
            return []

        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    data = json.loads(line)
                    videos.append(data)
                except json.JSONDecodeError:
                    continue
        return videos
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ 검색 시간 초과: {keyword}")
        return []
    except Exception as e:
        print(f"  ⚠️ 검색 오류: {e}")
        return []


def get_video_details(video_id):
    """yt-dlp로 개별 영상 상세 정보 가져오기"""
    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--dump-json",
        "--no-download",
        url
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception:
        return None


def format_duration(seconds):
    """초 → MM:SS 또는 H:MM:SS 형식"""
    if not seconds or seconds <= 0:
        return "0:00"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_date(date_str):
    """날짜 문자열 포맷"""
    if not date_str:
        return ""
    # yt-dlp는 보통 YYYYMMDD 형식
    try:
        if len(date_str) == 8:
            dt = datetime.strptime(date_str, "%Y%m%d")
            return dt.strftime("%Y-%m-%d")
        return date_str[:10]
    except Exception:
        return date_str


def extract_summary_from_description(description, max_len=500):
    """영상 설명에서 요약 발췌"""
    if not description:
        return "영상 설명이 없습니다."

    # URL 제거
    text = re.sub(r'https?://\S+', '', description)
    # 해시태그 제거
    text = re.sub(r'#\S+', '', text)
    # 빈 줄 정리
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    # 첫 500자 이내로 자르기
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + '...'

    return text if text else "영상 설명이 없습니다."


def extract_keywords_from_tags(tags, title, max_keywords=5):
    """태그와 제목에서 키워드 추출"""
    keywords = []

    if tags:
        keywords.extend(tags[:max_keywords])
    else:
        # 태그가 없으면 제목에서 주요 단어 추출
        words = re.findall(r'[가-힣a-zA-Z]{2,}', title)
        keywords = words[:max_keywords]

    return keywords[:max_keywords]


def generate_recommendation(title, channel, description):
    """추천이유 생성 (AI가 없으면 간단 생성)"""
    api_key = os.environ.get('OPENAI_API_KEY')

    if api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 교육 분야 유튜브 영상 큐레이터입니다. 주어진 영상 정보를 바탕으로 추천이유를 300자 이내, 요약을 500자 이내로 작성하세요. 추천이유에는 이 영상이 왜 교육자/학부모에게 유익한지 구체적으로 설명하세요. JSON 형식으로만 응답하세요: {\"recommendation\": \"...\", \"summary\": \"...\", \"keywords\": [\"...\"]}"
                    },
                    {
                        "role": "user",
                        "content": f"제목: {title}\n채널: {channel}\n설명: {description[:1000]}"
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            text = response.choices[0].message.content.strip()
            # JSON 파싱
            if text.startswith("```"):
                text = re.sub(r'^```\w*\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            return json.loads(text)
        except Exception as e:
            print(f"  ⚠️ AI 추천이유 생성 실패: {e}")

    # AI 없이 간단 생성
    desc_short = (description[:200] if description else "").strip()
    recommendation = f"{channel} 채널에서 제공하는 '{title[:40]}' 관련 영상입니다. {desc_short}"
    if len(recommendation) > 300:
        recommendation = recommendation[:297] + "..."

    return {
        "recommendation": recommendation,
        "summary": extract_summary_from_description(description),
        "keywords": extract_keywords_from_tags(None, title)
    }


def crawl_youtube():
    """메인 크롤링 로직"""
    print("=" * 50)
    print("🎬 유튜브 큐레이션 크롤링 시작")
    print("=" * 50)

    # 키워드 로드
    config = load_keywords()
    keywords = config.get('keywords', ['AI 교육', '에듀테크'])
    print(f"📌 키워드: {', '.join(keywords)}")

    all_videos = []
    seen_ids = set()

    # 키워드별 검색
    for keyword in keywords:
        print(f"\n🔍 '{keyword}' 검색 중...")
        results = search_youtube(keyword, max_results=5)
        print(f"  ✅ {len(results)}개 결과")

        for video in results:
            video_id = video.get('id') or video.get('url', '')
            if video_id in seen_ids:
                continue
            seen_ids.add(video_id)

            title = video.get('title', '제목 없음')
            print(f"  📺 {title[:50]}...")

            # 상세 정보 가져오기
            detail = get_video_details(video_id)

            if detail:
                duration_sec = detail.get('duration', 0)
                channel = detail.get('channel', detail.get('uploader', ''))
                upload_date = detail.get('upload_date', '')
                description = detail.get('description', '')
                tags = detail.get('tags', [])
                thumbnail = detail.get('thumbnail', f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
                view_count = detail.get('view_count', 0)
            else:
                duration_sec = video.get('duration', 0)
                channel = video.get('channel', video.get('uploader', ''))
                upload_date = video.get('upload_date', '')
                description = video.get('description', '')
                tags = video.get('tags', [])
                thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                view_count = video.get('view_count', 0)

            # AI 또는 간단 생성으로 추천이유/요약 생성
            ai_result = generate_recommendation(title, channel, description)

            all_videos.append({
                "videoId": video_id,
                "title": title,
                "channelName": channel or "알 수 없음",
                "publishedAt": format_date(upload_date),
                "duration": format_duration(duration_sec or 0),
                "durationSeconds": duration_sec or 0,
                "thumbnailUrl": thumbnail,
                "keywords": ai_result.get("keywords", extract_keywords_from_tags(tags, title)),
                "recommendation": ai_result.get("recommendation", ""),
                "summary": ai_result.get("summary", extract_summary_from_description(description)),
                "viewCount": view_count or 0,
                "searchKeyword": keyword
            })

    # 중복 제거 후 최대 10개
    all_videos = all_videos[:10]

    # 저장
    output = {
        "date": datetime.now(KST).strftime("%Y-%m-%d"),
        "items": all_videos
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(all_videos)}개 영상 크롤링 완료")
    print(f"📁 저장: {OUTPUT_FILE}")
    return all_videos


if __name__ == "__main__":
    crawl_youtube()
