# TechCrunch AI RSS 수집기

TechCrunch AI 카테고리 RSS를 수집하고, **Gemini API**로 한국어 요약까지 저장하는 프로젝트입니다.

## 설정

```bash
cd C:\program1\techcrunch-ai-rss
pip install -r requirements.txt
```

### Gemini API 키 (요약 기능 사용 시)

1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키 발급 (무료)
2. 환경 변수로 설정:
   - Windows (PowerShell): `$env:GEMINI_API_KEY="your-api-key"`
   - Windows (CMD): `set GEMINI_API_KEY=your-api-key`
   - Linux/macOS: `export GEMINI_API_KEY=your-api-key`

또는 `config.py`에서 `GEMINI_API_KEY = "your-api-key"` 로 직접 설정할 수 있습니다 (공유 시 키 제외 권장).

## 실행

### RSS만 수집

```bash
python run.py
```

- 수집 결과: `output/articles.json`

### 수집 + Gemini 한국어 요약

```bash
python run_with_summary.py
```

- RSS 수집 후 각 기사를 Gemini로 2~4문장 한국어 요약
- 결과: `output/summarized_articles.json` (각 기사에 `summary_ko` 필드 추가)
- 무료 한도 내에서 기사당 약 2초 대기로 rate limit 방지

### 웹 블로그 실행

```bash
python run_web.py
```

또는

```bash
python app.py
```

- 브라우저에서 `http://localhost:5000` 접속
- `output/summarized_articles.json`의 기사들을 웹 페이지로 표시
- 반응형 디자인으로 모바일/데스크톱 모두 지원

**참고**: 웹 블로그를 보려면 먼저 `python run_with_summary.py`로 기사를 수집하고 요약해야 합니다.

### Railway 배포 및 매일 자동 업데이트

서버 배포·매일 자동 수집 방법은 [SERVER.md](SERVER.md)를 참고하세요. Railway + cron-job.org로 매일 00:00에 기사를 자동 업데이트할 수 있습니다.

## 다른 코드에서 사용

```python
from rss_fetcher import collect, fetch_techcrunch_ai_feed, parse_entries
from summarizer import summarize_articles, save_summarized

# 수집만
articles, path = collect()

# 수집 + 요약
articles, _ = collect()
summarized = summarize_articles(articles, delay_seconds=2.0)
save_summarized(summarized)
```

## 출처

RSS 사용 시 [TechCrunch RSS 이용약관](https://techcrunch.com/rss-terms-of-use/)을 준수하고, 기사 링크와 출처(TechCrunch)를 표기해야 합니다.
