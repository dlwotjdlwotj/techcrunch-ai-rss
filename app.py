"""
TechCrunch AI 요약 블로그 웹 서버 (Flask)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from flask import Flask, render_template, request

from config import OUTPUT_DIR, SUMMARIZED_JSON

app = Flask(__name__)


def load_articles():
    """summarized_articles.json을 읽어서 기사 목록을 반환합니다."""
    # 프로젝트 루트 기준 경로 (서버 실행 위치와 무관)
    root = Path(__file__).resolve().parent
    filepath = root / OUTPUT_DIR / SUMMARIZED_JSON
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("articles", [])
    except Exception:
        return []


@app.route("/")
def index():
    """메인 페이지: 기사 목록"""
    articles = load_articles()
    return render_template("index.html", articles=articles)


@app.route("/article/<int:article_id>")
def article_detail(article_id):
    """기사 상세 페이지"""
    articles = load_articles()
    if 0 <= article_id < len(articles):
        article = articles[article_id]
        return render_template("article.html", article=article, article_id=article_id)
    return "기사를 찾을 수 없습니다.", 404


@app.route("/api/trigger-update", methods=["GET", "POST"])
def trigger_update():
    """
    외부 cron에서 호출해 RSS 수집·요약을 실행합니다.
    매일 00:00 KST에 호출하려면 cron-job.org 등에서 설정하세요.
    """
    secret = os.environ.get("CRON_SECRET")
    if not secret:
        return {"error": "CRON_SECRET not configured"}, 503
    key = request.args.get("key") or request.headers.get("X-Cron-Key")
    if key != secret:
        return {"error": "Unauthorized"}, 401

    root = Path(__file__).resolve().parent
    subprocess.Popen(
        [sys.executable, str(root / "scheduled_update.py")],
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return {"status": "started", "message": "RSS 수집 및 요약을 백그라운드에서 실행 중입니다."}, 202


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print("TechCrunch AI 요약 블로그 시작 중...")
    print(f"브라우저에서 http://localhost:{port} 을 열어보세요.")
    app.run(debug=debug, host="0.0.0.0", port=port)
