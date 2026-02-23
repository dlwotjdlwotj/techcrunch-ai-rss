"""
서버에서 예약 실행용 스크립트.
- 오늘 이미 업데이트했으면 건너뛰고, 아니면 run_with_summary를 실행합니다.

사용법 (Linux 서버):
  - cron: crontab -e 로 매일 실행 시간 설정
  - systemd: techcrunch-update.timer 사용
  - 자동 설정: bash setup-server-update.sh 실행
  - 자세한 내용은 SERVER.md 참고
"""
import sys
from datetime import date
from pathlib import Path

from config import OUTPUT_DIR

# 이 스크립트 파일이 있는 디렉터리를 작업 디렉터리로 (cron/systemd에서 다른 CWD로 실행될 수 있음)
SCRIPT_DIR = Path(__file__).resolve().parent
STATE_FILE = SCRIPT_DIR / OUTPUT_DIR / "last_update_date.txt"


def already_updated_today() -> bool:
    """오늘 이미 업데이트했는지 확인합니다 (로컬 날짜 기준)."""
    if not STATE_FILE.exists():
        return False
    try:
        content = STATE_FILE.read_text(encoding="utf-8").strip()
        return content == date.today().isoformat()
    except Exception:
        return False


def main():
    if SCRIPT_DIR != Path.cwd():
        import os
        os.chdir(SCRIPT_DIR)

    lock_file = SCRIPT_DIR / OUTPUT_DIR / "update_in_progress.lock"
    try:
        if already_updated_today():
            print("오늘은 이미 업데이트했습니다. 건너뜁니다.")
            return 0

        print("오늘 업데이트가 없습니다. RSS 수집 및 요약을 실행합니다.\n")
        from run_with_summary import main as run_main
        return run_main()
    finally:
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
