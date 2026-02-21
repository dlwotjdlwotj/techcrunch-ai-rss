"""
TechCrunch AI RSS 수집 스크립트.
실행 시 피드를 가져와 output/articles.json에 저장하고 콘솔에 요약을 출력합니다.
"""
import sys
from rss_fetcher import collect


def main():
    print("TechCrunch AI RSS 수집 중...")
    try:
        articles, filepath = collect()
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"수집 완료: {len(articles)}개 기사")
    print(f"저장 위치: {filepath}\n")
    print("--- 최근 기사 ---")
    for i, a in enumerate(articles[:10], 1):
        print(f"{i}. {a['title']}")
        print(f"   {a['link']}")
        print(f"   발행: {a['published']}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
