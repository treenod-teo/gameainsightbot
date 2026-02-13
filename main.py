import feedparser
import os
import requests
from openai import OpenAI

# 1. 설정 (키워드 수정 가능)
KEYWORDS = ["게임기획 AI", "game monetization design", "loyalty system game", "live ops retention"]
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

def fetch_news():
    articles = []
    for kw in KEYWORDS:
        url = f"https://news.google.com/rss/search?q={kw}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # 키워드당 3개씩
            articles.append({"title": entry.title, "link": entry.link})
    return articles

def analyze_and_send():
    news_list = fetch_news()
    news_text = "\n".join([f"- {a['title']} ({a['link']})" for a in news_list])
    
    # 테오의 업무 맥락(골든호밍, 로열티 등)을 반영한 프롬프트
    prompt = f"""
    너는 게임 기획 전략가야. 아래 뉴스 목록 중 기획자에게 유익한 5개를 선정해줘.
    특히 '로열티 시스템', '유저 리텐션', 'BM 설계'와 관련 있으면 우선순위를 높여줘.
    
    형식:
    * [제목](링크)
    * 요약: 1줄
    * 기획 인사이트: 테오의 프로젝트(로열티, 결제 전략 등)에 적용할 점 1줄
    
    뉴스 목록:
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    result = response.choices[0].message.content
    
    # 슬랙 전송
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"channel": "#general", "text": f"📅 오늘의 게임 기획 & AI 인사이트\n\n{result}"}
    )

if __name__ == "__main__":
    analyze_and_send()
