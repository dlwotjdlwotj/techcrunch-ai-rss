# TechCrunch AI 카테고리 RSS 피드 (공식)
TECHCRUNCH_AI_FEED_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"

# 수집 결과 저장 경로
OUTPUT_DIR = "output"
ARTICLES_JSON = "articles.json"
SUMMARIZED_JSON = "summarized_articles.json"

# Gemini API - 반드시 환경 변수 GEMINI_API_KEY 설정 (config에 키 넣지 말 것, 유출 위험)
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
