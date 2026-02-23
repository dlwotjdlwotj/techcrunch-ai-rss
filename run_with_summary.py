"""
TechCrunch AI RSS 수집 + Gemini 요약 스크립트.
RSS 수집 후 각 기사를 Gemini API로 한국어 요약해 output/summarized_articles.json에 저장합니다.
실행 전에 환경 변수 GEMINI_API_KEY를 설정하세요.
"""
import sys
from datetime import date
from pathlib import Path

from config import OUTPUT_DIR
from rss_fetcher import collect
from summarizer import (
    load_existing_summarized,
    merge_and_summarize,
    remove_failed_articles_from_file,
    save_summarized,
)


def main():
    removed = remove_failed_articles_from_file()
    if removed > 0:
        print(f"기존 파일에서 요약 실패한 기사 {removed}건을 제거했습니다.\n")

    print("TechCrunch AI RSS 수집 중...")
    try:
        articles, articles_path = collect()
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"수집 완료: {len(articles)}개 기사")
    print(f"원본 저장: {articles_path}\n")

    existing = load_existing_summarized()
    new_count = sum(1 for a in articles if a.get("link") not in {e.get("link") for e in existing})
    print(f"기존 요약: {len(existing)}개 / 이번 피드에서 새 글: {new_count}개")

    if new_count > 0:
        print("Gemini API로 새 기사만 한국어 요약 중... (기사당 15초 간격, 무료 한도 5회/분 준수)")
    else:
        print("새 기사 없음. 기존 요약과 피드 순서만 반영합니다.")
    try:
        merged, failed_list = merge_and_summarize(articles, existing, delay_seconds=15.0)
        summary_path = save_summarized(merged)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

    if failed_list:
        print("\n[!] 요약 실패: 아래 기사는 목록에 포함되지 않았습니다.")
        for f in failed_list:
            title = f['title']
            print(f"   · {title[:60] + '...' if len(title) > 60 else title}")
            print(f"     링크: {f['link']}")
            err = f['error']
            print(f"     사유: {err[:100] + '...' if len(err) > 100 else err}")
        print()

    print(f"저장 완료: {len(merged)}개 기사 → {summary_path}\n")

    # 오늘 업데이트했음을 기록 (예약 실행 시 "이미 오늘 했는지" 판단용)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    (Path(OUTPUT_DIR) / "last_update_date.txt").write_text(date.today().isoformat(), encoding="utf-8")

    print("--- 최근 기사 (한국어 요약) ---")
    for i, a in enumerate(merged[:5], 1):
        print(f"{i}. {a['title']}")
        print(f"   요약: {a.get('summary_ko', '-')}")
        print(f"   링크: {a['link']}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
