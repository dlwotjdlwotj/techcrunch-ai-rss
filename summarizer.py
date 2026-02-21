"""
Gemini API를 사용해 기사를 한국어로 요약하는 모듈.
"""
import re
import time
from pathlib import Path

import google.generativeai as genai

import json

from config import GEMINI_API_KEY, GEMINI_MODEL, OUTPUT_DIR, SUMMARIZED_JSON


def _strip_html(text: str) -> str:
    """HTML 태그를 제거하고 공백을 정리합니다."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _ensure_client() -> None:
    """API 키가 설정되었는지 확인하고 genai를 설정합니다."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY가 없습니다. "
            "환경 변수로 설정하거나 config.py에서 설정하세요. "
            "발급: https://aistudio.google.com/apikey"
        )
    genai.configure(api_key=GEMINI_API_KEY)


def summarize_article(article: dict, model_name: str = GEMINI_MODEL) -> str:
    """
    기사 하나를 Gemini로 한국어 요약합니다.
    article: title, link, summary 등이 있는 딕셔너리
    """
    _ensure_client()
    title = article.get("title", "")
    raw_summary = article.get("summary", "")
    summary_clean = _strip_html(raw_summary)
    if not summary_clean:
        summary_clean = title

    prompt = f"""다음 TechCrunch AI 기사를 한국어로 2~4문장으로 간단히 요약해주세요. 핵심만 담고, 마크다운이나 제목 형식은 쓰지 말고 평문으로만 답하세요.

제목: {title}

내용:
{summary_clean[:4000]}
"""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    if not response.text:
        return ""
    return response.text.strip()


def summarize_articles(
    articles: list[dict],
    model_name: str = GEMINI_MODEL,
    delay_seconds: float = 2.0,
) -> list[dict]:
    """
    기사 목록을 순서대로 요약합니다.
    각 기사에 summary_ko 필드를 추가한 새 리스트를 반환합니다.
    delay_seconds: API rate limit 방지용 대기 시간(초)
    """
    _ensure_client()
    result = []
    for i, article in enumerate(articles):
        try:
            summary_ko = summarize_article(article, model_name=model_name)
            result.append({**article, "summary_ko": summary_ko})
        except Exception as e:
            result.append({**article, "summary_ko": f"[요약 실패: {e}]"})
        if delay_seconds and i < len(articles) - 1:
            time.sleep(delay_seconds)
    return result


def _is_failed_summary(summary_ko: str) -> bool:
    """요약 실패 메시지인지 확인합니다."""
    if not summary_ko or not isinstance(summary_ko, str):
        return True
    return summary_ko.strip().startswith("[요약 실패:")


def remove_failed_articles_from_file(
    output_dir: str = OUTPUT_DIR,
    filename: str = SUMMARIZED_JSON,
) -> int:
    """기존 요약 파일에서 요약 실패한 기사를 제거하고 파일을 다시 저장합니다. 제거한 개수를 반환합니다."""
    from datetime import datetime

    from config import TECHCRUNCH_AI_FEED_URL

    filepath = Path(output_dir) / filename
    if not filepath.exists():
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    articles = data.get("articles", [])
    ok = [a for a in articles if not _is_failed_summary(a.get("summary_ko", ""))]
    removed = len(articles) - len(ok)
    if removed == 0:
        return 0
    data["articles"] = ok
    data["count"] = len(ok)
    data["fetched_at"] = datetime.utcnow().isoformat() + "Z"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return removed


def load_existing_summarized(
    output_dir: str = OUTPUT_DIR,
    filename: str = SUMMARIZED_JSON,
) -> list[dict]:
    """기존 요약 파일이 있으면 기사 목록을 반환하고, 없으면 빈 리스트를 반환합니다."""
    filepath = Path(output_dir) / filename
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("articles", [])
    except Exception:
        return []


def merge_and_summarize(
    fresh_articles: list[dict],
    existing_articles: list[dict],
    model_name: str = GEMINI_MODEL,
    delay_seconds: float = 2.0,
) -> tuple[list[dict], list[dict]]:
    """
    기존 요약은 유지하고, RSS에서 새로 나타난 기사만 요약해 병합합니다.
    요약에 실패한 기사는 목록에 넣지 않습니다.
    - fresh_articles: 방금 수집한 RSS 기사 목록 (최신 순)
    - existing_articles: 기존에 요약해 둔 기사 목록
    반환: (저장할 기사 목록, 요약 실패한 기사 목록 [{title, link, error}, ...])
    """
    existing_by_link = {a.get("link"): a for a in existing_articles if a.get("link")}
    fresh_links = {a.get("link") for a in fresh_articles if a.get("link")}

    new_articles = [a for a in fresh_articles if a.get("link") not in existing_by_link]
    summarized_new_by_link = {}
    failed_list = []

    if new_articles:
        _ensure_client()
        for i, article in enumerate(new_articles):
            try:
                summary_ko = summarize_article(article, model_name=model_name)
                summarized_new_by_link[article["link"]] = {**article, "summary_ko": summary_ko}
            except Exception as e:
                failed_list.append({
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "error": str(e),
                })
            if delay_seconds and i < len(new_articles) - 1:
                time.sleep(delay_seconds)

    merged = []
    for a in fresh_articles:
        link = a.get("link")
        if link in existing_by_link:
            merged.append(existing_by_link[link])
        elif link in summarized_new_by_link:
            merged.append(summarized_new_by_link[link])
        # 요약 실패한 새 기사는 merged에 넣지 않음

    for a in existing_articles:
        if a.get("link") and a["link"] not in fresh_links:
            merged.append(a)

    return merged, failed_list


def save_summarized(
    articles_with_summary: list[dict],
    output_dir: str = OUTPUT_DIR,
    filename: str = SUMMARIZED_JSON,
) -> Path:
    """요약이 포함된 기사 목록을 JSON으로 저장합니다."""
    from datetime import datetime

    from config import TECHCRUNCH_AI_FEED_URL

    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    filepath = path / filename
    data = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "source": TECHCRUNCH_AI_FEED_URL,
        "count": len(articles_with_summary),
        "articles": articles_with_summary,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath
