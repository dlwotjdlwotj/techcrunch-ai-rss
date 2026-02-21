"""
TechCrunch AI 카테고리 RSS 피드를 수집하는 모듈.
"""
import json
from datetime import datetime
from pathlib import Path

import feedparser

from config import TECHCRUNCH_AI_FEED_URL, OUTPUT_DIR, ARTICLES_JSON


def fetch_techcrunch_ai_feed(url: str = TECHCRUNCH_AI_FEED_URL) -> feedparser.FeedParserDict:
    """TechCrunch AI RSS 피드를 가져옵니다."""
    return feedparser.parse(url)


def parse_entries(feed: feedparser.FeedParserDict) -> list[dict]:
    """피드에서 기사 목록을 파싱해 딕셔너리 리스트로 반환합니다."""
    entries = []
    for entry in feed.entries:
        # published 파싱 (포맷이 다양할 수 있음)
        published = getattr(entry, "published", None) or getattr(entry, "updated", "")
        entries.append({
            "title": getattr(entry, "title", ""),
            "link": getattr(entry, "link", ""),
            "published": published,
            "summary": getattr(entry, "summary", ""),
            "id": getattr(entry, "id", ""),
        })
    return entries


def save_articles(articles: list[dict], output_dir: str = OUTPUT_DIR, filename: str = ARTICLES_JSON) -> Path:
    """수집한 기사를 JSON 파일로 저장합니다."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    filepath = path / filename
    data = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "source": TECHCRUNCH_AI_FEED_URL,
        "count": len(articles),
        "articles": articles,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


def collect() -> tuple[list[dict], Path | None]:
    """
    TechCrunch AI RSS를 수집하고 저장합니다.
    Returns: (기사 리스트, 저장된 파일 경로 또는 None)
    """
    feed = fetch_techcrunch_ai_feed()
    if feed.bozo and not feed.entries:
        raise RuntimeError("RSS 파싱 실패 또는 피드가 비어 있음")
    articles = parse_entries(feed)
    filepath = save_articles(articles)
    return articles, filepath
