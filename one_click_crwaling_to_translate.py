import praw
import json
import pandas as pd
from googletrans import Translator

# Reddit API 설정
reddit = praw.Reddit(
    client_id='JivI2me1M4bxc7EIC1mzgg',
    client_secret='M1bZIds0Ykt-oz5LSFUtexxjurBpzg',
    user_agent='sound_effect_crawler'
)

# Subreddit 리스트와 키워드 설정
subreddit_list = ["IndieDev", "VideoEditing"]
keyword = (
    "sound effect OR free sound effects OR game sound effects OR "
    "sound design OR audio fx OR background music OR royalty-free music OR "
    "game music OR ambient sound OR video editing music OR sound library OR "
    "audio tools OR DAW OR audio mixing OR music copyright"
)
results = []

# 데이터 크롤링
for subreddit_name in subreddit_list:
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.search(keyword, limit=100):  # 게시글 검색
        results.append({
            "title": submission.title,
            "url": submission.url,
            "selftext": submission.selftext,
            "comments": [comment.body for comment in submission.comments if hasattr(comment, "body")]
        })

print(f"총 {len(results)}개의 게시글 크롤링 완료")

# 번역기 설정
translator = Translator()

# 긴 텍스트를 5000자 이하로 분할하는 함수
def split_text(text, max_length=5000):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = sentence + ". "
        else:
            current_chunk += sentence + ". "
    if current_chunk:  # 마지막 남은 텍스트 추가
        chunks.append(current_chunk)
    return chunks

# 분할된 텍스트를 번역하는 함수
def translate_text(text, target="ko"):
    if not text:
        return ""
    try:
        chunks = split_text(text)
        translated_chunks = [translator.translate(chunk, src="en", dest=target).text for chunk in chunks]
        return " ".join(translated_chunks)
    except Exception as e:
        print(f"번역 중 오류 발생: {e}")
        return text  # 번역 실패 시 원문 반환

# 크롤링 데이터 번역
for item in results:
    item['title_ko'] = translate_text(item['title'])
    item['selftext_ko'] = translate_text(item['selftext'])
    item['comments_ko'] = [translate_text(comment) for comment in item['comments']]

# JSON 파일로 저장
with open("reddit_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

# CSV 파일로 저장
df = pd.DataFrame([{**item, 'comments': '\n'.join(item['comments']), 'comments_ko': '\n'.join(item['comments_ko'])} for item in results])
df.to_csv("reddit_results.csv", index=False, encoding="utf-8-sig")

print("크롤링 및 번역 데이터 저장 완료 (JSON 및 CSV 파일 생성)")
