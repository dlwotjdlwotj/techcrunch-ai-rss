"""
웹 블로그 서버 실행 스크립트
"""
import sys
from app import app

if __name__ == "__main__":
    print("=" * 60)
    print("TechCrunch AI 요약 블로그 웹 서버 시작")
    print("=" * 60)
    print("\n브라우저에서 다음 주소를 열어보세요:")
    print("  http://localhost:5000")
    print("\n종료하려면 Ctrl+C를 누르세요.\n")
    print("=" * 60)
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("\n\n서버를 종료합니다.")
        sys.exit(0)
