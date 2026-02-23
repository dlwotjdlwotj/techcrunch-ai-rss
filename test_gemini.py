#!/usr/bin/env python3
"""
Gemini API 연결 테스트 스크립트.
실행: python test_gemini.py
"""
import os
import sys

def main():
    from config import GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        print("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        print("  환경 변수: $env:GEMINI_API_KEY='your-key' (PowerShell)")
        print("  또는 config.py에서 설정")
        sys.exit(1)
    
    key_source = "환경 변수" if os.environ.get("GEMINI_API_KEY") else "config.py 기본값"
    print(f"API 키 출처: {key_source}")
    print(f"키 앞 10자: {GEMINI_API_KEY[:10]}...")
    print()
    
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="한국어로 '테스트 성공'이라고만 답해주세요."
        )
        text = getattr(response, "text", None)
        if text:
            print(f"성공: {text.strip()}")
        else:
            print("응답에 텍스트가 없습니다:", response)
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
