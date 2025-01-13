import pandas as pd
from deep_translator import GoogleTranslator
import re
import time

# 텍스트 전처리 함수
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # 이모지 제거
    return text

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
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# 분할된 텍스트를 번역하는 함수
def translate_text(text, target="ko"):
    if not text or text.strip() == "":  # None 또는 빈 문자열 처리
        return ""
    if len(text) > 5000:  # 5000자를 초과하는 경우 스킵
        return "텍스트가 5000자를 초과하여 번역을 생략했습니다."
    try:
        chunks = split_text(text)
        translated_chunks = []
        for chunk in chunks:
            try:
                time.sleep(1)  # 요청 간 지연 추가
                translated_chunk = GoogleTranslator(source="en", target=target).translate(chunk)
                translated_chunks.append(translated_chunk if translated_chunk else "")  # None 값을 빈 문자열로 처리
            except Exception as e:
                print(f"번역 중 오류 발생(세부 텍스트): {e}")
                translated_chunks.append(chunk)  # 오류 발생 시 원문 유지
        return " ".join(translated_chunks)
    except Exception as e:
        print(f"번역 중 오류 발생(전체 텍스트): {e}")
        return text  # 번역 실패 시 원문 반환

# 로컬 CSV 파일 불러오기 및 전처리
input_csv_path = "reddit_crawling_results.csv"  # 원본 CSV 파일 경로
output_csv_path = "translated_results.csv"  # 번역 결과를 저장할 CSV 파일 경로

data = pd.read_csv(input_csv_path)

# NaN 값 및 None 값을 빈 문자열로 대체
data = data.fillna("")

# 번역 적용
if "title" in data.columns:
    data['title_ko'] = data['title'].apply(translate_text)
if "selftext" in data.columns:
    data['selftext_ko'] = data['selftext'].apply(translate_text)
if "comments" in data.columns:
    data['comments_ko'] = data['comments'].apply(
        lambda x: '\n'.join([
            translate_text(comment) for comment in str(x).split('\n') if comment  # None 값 제거
        ])
    )

# 번역 결과 저장
data.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

print(f"번역이 완료된 데이터를 {output_csv_path}에 저장했습니다.")
