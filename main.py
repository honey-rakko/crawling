import praw
import pandas as pd

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

# CSV 파일로 저장
df = pd.DataFrame([{**item, 'comments': '\n'.join(item['comments'])} for item in results])
df.to_csv("reddit_crawling_results.csv", index=False, encoding="utf-8-sig")

print("크롤링 데이터 저장 완료 (CSV 파일 생성)")