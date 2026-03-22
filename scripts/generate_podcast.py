#!/usr/bin/env python3
"""
이교장 뉴스레터 – 남녀 대화형 팟캐스트 생성 스크립트

1. data/youtube_curated.json에서 유튜브 영상 정보 로드
2. OpenAI API로 남녀 대화형 팟캐스트 스크립트 생성 (없으면 간단 대화)
3. edge-tts로 2화자 TTS 오디오 생성 (여성 SunHi + 남성 InJoon)
4. 파트별 오디오를 순서대로 결합 → assets/podcast/latest.mp3 저장
"""

import asyncio
import json
import os
import re
import sys
import struct
import io
from datetime import datetime, timezone, timedelta

import edge_tts

# ──────── 경로 설정 ────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "keywords.json")
YOUTUBE_FILE = os.path.join(BASE_DIR, "data", "youtube_curated.json")
OUTPUT_AUDIO = os.path.join(BASE_DIR, "assets", "podcast", "latest.mp3")

KST = timezone(timedelta(hours=9))

# TTS 음성 설정
FEMALE_VOICE = "ko-KR-SunHiNeural"   # 여성 진행자 (지현)
MALE_VOICE = "ko-KR-InJoonNeural"     # 남성 진행자 (민수)


def load_keywords():
    """키워드 설정 로드"""
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_youtube_data():
    """유튜브 큐레이션 데이터 로드"""
    if not os.path.exists(YOUTUBE_FILE):
        print("❌ youtube_curated.json이 없습니다. 먼저 crawl_youtube.py를 실행하세요.")
        sys.exit(1)

    with open(YOUTUBE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get("items", [])
    if not items:
        print("❌ 유튜브 큐레이션 데이터가 비어있습니다.")
        sys.exit(1)

    return items


def generate_dialogue_with_ai(videos, duration_minutes=5):
    """OpenAI API로 남녀 대화형 팟캐스트 스크립트 생성"""
    api_key = os.environ.get('OPENAI_API_KEY')

    if not api_key:
        print("⚠️ OPENAI_API_KEY가 설정되지 않음, 간단 대화 스크립트 사용")
        return generate_simple_dialogue(videos, duration_minutes)

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)

        today = datetime.now(KST).strftime("%Y년 %m월 %d일")
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        weekday = weekdays[datetime.now(KST).weekday()]

        # 영상 정보 텍스트 구성
        videos_text = ""
        for i, v in enumerate(videos[:10]):
            videos_text += f"\n[영상 {i+1}]\n"
            videos_text += f"제목: {v['title']}\n"
            videos_text += f"채널: {v['channelName']}\n"
            videos_text += f"영상길이: {v['duration']}\n"
            videos_text += f"키워드: {', '.join(v.get('keywords', []))}\n"
            videos_text += f"추천이유: {v.get('recommendation', '')}\n"
            videos_text += f"요약: {v.get('summary', '')[:300]}\n"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""당신은 '이교장 뉴스레터 팟캐스트' 대본 작가입니다.
오늘은 {today} {weekday}요일입니다.

두 명의 진행자가 자연스럽게 대화하는 팟캐스트 대본을 작성하세요:
- [지현]: 여성 메인 진행자. 밝고 친근한 말투. 주제를 소개하고 핵심을 정리하는 역할.
- [민수]: 남성 공동 진행자. 호기심 많고 질문을 잘 하는 스타일. 리액션과 보충 설명.

규칙:
- 반드시 각 대사 앞에 [지현] 또는 [민수] 태그를 붙이세요
- 약 {duration_minutes}분 분량 (1분에 약 250자 기준)
- Google의 NotebookLM 팟캐스트처럼 자연스러운 대화체
- "아~", "오!", "맞아요", "그렇죠" 같은 자연스러운 추임새 사용
- 10개 영상 중 핵심 5~7개를 선별하여 다루세요
- 인사로 시작하고, 마무리 인사로 끝내세요
- 마크다운, 특수문자, 이모지 사용 금지
- 대괄호 태그 [지현], [민수] 외에는 대괄호 사용 금지"""
                },
                {
                    "role": "user",
                    "content": f"오늘의 유튜브 큐레이션 영상 목록:\n{videos_text}"
                }
            ],
            temperature=0.8,
            max_tokens=3000
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ AI 스크립트 생성 실패: {e}, 간단 대화 스크립트 사용")
        return generate_simple_dialogue(videos, duration_minutes)


def generate_simple_dialogue(videos, duration_minutes=5):
    """AI 없이 간단한 남녀 대화형 스크립트 생성"""
    today = datetime.now(KST).strftime("%Y년 %m월 %d일")
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    weekday = weekdays[datetime.now(KST).weekday()]

    lines = [
        f"[지현] 안녕하세요! 이교장 뉴스레터 팟캐스트입니다. 오늘은 {today} {weekday}요일이에요.",
        f"[민수] 네, 안녕하세요! 오늘도 AI 교육 관련 유튜브 영상들을 함께 살펴보겠습니다.",
        "[지현] 오늘 총 열 편의 영상을 큐레이션했는데요, 그 중에서 핵심적인 것들을 골라서 이야기해볼게요.",
        ""
    ]

    for i, video in enumerate(videos[:5]):
        ordinal = ['첫', '두', '세', '네', '다섯'][i]
        channel = video.get('channelName', '알 수 없음')
        title = video.get('title', '제목 없음')
        recommendation = video.get('recommendation', '')

        lines.append(f"[지현] {ordinal} 번째는 {channel} 채널의 영상이에요. 제목은 {title}입니다.")

        if recommendation:
            lines.append(f"[민수] 오, 이 영상 흥미로운데요. {recommendation[:150]}")
        else:
            lines.append(f"[민수] 네, 이 영상도 정말 유익해 보이네요.")

        lines.append(f"[지현] 맞아요. 교육 관련해서 좋은 인사이트를 얻을 수 있는 영상이에요.")
        lines.append("")

    lines.extend([
        "[민수] 오늘도 정말 알찬 영상들이었네요.",
        "[지현] 네, 더 자세한 내용은 이교장 뉴스레터 페이지에서 영상을 직접 시청해보세요.",
        "[민수] 그럼 다음 시간에 또 만나요!",
        "[지현] 네, 감사합니다. 안녕히 계세요!"
    ])

    return "\n".join(lines)


def parse_dialogue(script):
    """대본을 화자별 파트로 분리"""
    parts = []
    # [지현] 또는 [민수] 태그로 분리
    pattern = r'\[(지현|민수)\]\s*(.+?)(?=\[(?:지현|민수)\]|$)'
    matches = re.findall(pattern, script, re.DOTALL)

    for speaker, text in matches:
        text = text.strip()
        if not text:
            continue
        voice = FEMALE_VOICE if speaker == "지현" else MALE_VOICE
        parts.append({
            "speaker": speaker,
            "voice": voice,
            "text": text
        })

    if not parts:
        # 파싱 실패 시 전체를 여성 음성으로
        parts.append({
            "speaker": "지현",
            "voice": FEMALE_VOICE,
            "text": script
        })

    return parts


async def generate_part_audio(text, voice, output_path):
    """개별 파트 TTS 생성"""
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save(output_path)


def concat_mp3_files(file_list, output_path):
    """MP3 파일들을 순서대로 결합 (바이너리 결합)"""
    with open(output_path, 'wb') as outfile:
        for fpath in file_list:
            if os.path.exists(fpath):
                with open(fpath, 'rb') as infile:
                    outfile.write(infile.read())


async def generate_podcast_audio(script):
    """대본 파싱 → 파트별 TTS → MP3 병합"""
    parts = parse_dialogue(script)
    print(f"📝 대본 파싱 완료: {len(parts)}개 파트")

    # 임시 파일 디렉토리
    tmp_dir = os.path.join(BASE_DIR, "assets", "podcast", "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    part_files = []

    for i, part in enumerate(parts):
        tmp_path = os.path.join(tmp_dir, f"part_{i:03d}.mp3")
        speaker_icon = "👩" if part["speaker"] == "지현" else "👨"
        print(f"  {speaker_icon} [{part['speaker']}] {part['text'][:40]}...")

        try:
            await generate_part_audio(part["text"], part["voice"], tmp_path)
            part_files.append(tmp_path)
        except Exception as e:
            print(f"  ⚠️ 파트 {i} TTS 실패: {e}")

    if not part_files:
        print("❌ 생성된 오디오 파트가 없습니다.")
        sys.exit(1)

    # MP3 결합
    os.makedirs(os.path.dirname(OUTPUT_AUDIO), exist_ok=True)
    concat_mp3_files(part_files, OUTPUT_AUDIO)

    # 임시 파일 정리
    for f in part_files:
        try:
            os.remove(f)
        except OSError:
            pass
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass

    size_kb = os.path.getsize(OUTPUT_AUDIO) / 1024
    print(f"✅ 오디오 생성 완료: {size_kb:.1f} KB")


async def main():
    print("=" * 50)
    print("🎙️ 이교장 뉴스레터 – 남녀 대화형 팟캐스트 생성")
    print("=" * 50)

    # 1. 설정 로드
    config = load_keywords()
    duration = config.get('duration_minutes', 5)

    # 2. 유튜브 큐레이션 데이터 로드
    print("\n📺 유튜브 큐레이션 데이터 로드 중...")
    videos = load_youtube_data()
    print(f"✅ {len(videos)}개 영상 로드 완료")
    for v in videos[:5]:
        print(f"  • [{v['channelName']}] {v['title'][:50]}")

    # 3. 남녀 대화형 스크립트 생성
    print(f"\n✍️ 남녀 대화형 스크립트 생성 중 (목표: {duration}분)...")
    script = generate_dialogue_with_ai(videos, duration)
    print(f"✅ 스크립트 생성 완료 ({len(script)}자)")
    print("\n--- 스크립트 미리보기 ---")
    preview = script[:500]
    print(preview)
    if len(script) > 500:
        print("...")
    print("--- 끝 ---\n")

    # 4. 2화자 TTS 오디오 생성
    print("🎧 2화자 TTS 오디오 생성 중...")
    print(f"  👩 여성(지현): {FEMALE_VOICE}")
    print(f"  👨 남성(민수): {MALE_VOICE}")
    await generate_podcast_audio(script)

    print("\n🎉 남녀 대화형 팟캐스트 생성 완료!")
    print(f"📁 저장: {OUTPUT_AUDIO}")


if __name__ == "__main__":
    asyncio.run(main())
