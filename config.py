# TechCrunch AI 카테고리 RSS 피드 (공식)
TECHCRUNCH_AI_FEED_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"

# 수집 결과 저장 경로
OUTPUT_DIR = "output"
ARTICLES_JSON = "articles.json"
SUMMARIZED_JSON = "summarized_articles.json"

# Gemini API (환경 변수 GEMINI_API_KEY 사용, 없으면 여기서 설정)
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBGp8deRhESHx9yyIkm0B5LpQCfBY-8OHs")
GEMINI_MODEL = "gemini-2.5-flash"
