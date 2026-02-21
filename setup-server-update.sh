#!/bin/bash
# 서버에서 자동 업데이트 설정 스크립트
# 사용법: sudo bash setup-server-update.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "TechCrunch AI RSS 서버 자동 업데이트 설정"
echo "프로젝트 경로: $PROJECT_DIR"
echo ""

# Python 경로 확인
PYTHON3=$(which python3)
if [ -z "$PYTHON3" ]; then
    echo "오류: python3를 찾을 수 없습니다."
    exit 1
fi
echo "Python 경로: $PYTHON3"

# 로그 디렉터리 생성
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
echo "로그 디렉터리 생성: $LOG_DIR"

# cron 설정
echo ""
echo "=== Cron 설정 ==="
CRON_LINE="0 9 * * * cd $PROJECT_DIR && $PYTHON3 $PROJECT_DIR/scheduled_update.py >> $LOG_DIR/update.log 2>&1"

# 현재 사용자의 crontab에 추가
(crontab -l 2>/dev/null | grep -v "scheduled_update.py"; echo "$CRON_LINE") | crontab -

echo "Cron 작업이 추가되었습니다:"
echo "  $CRON_LINE"
echo ""
echo "확인: crontab -l"
echo ""

# systemd timer 설정 (선택사항)
if systemctl --version > /dev/null 2>&1; then
    echo "=== Systemd Timer 설정 (선택사항) ==="
    echo "systemd를 사용하려면:"
    echo "  1. techcrunch-update.service와 techcrunch-update.timer 파일의 경로를 수정"
    echo "  2. sudo cp techcrunch-update.service techcrunch-update.timer /etc/systemd/system/"
    echo "  3. sudo systemctl daemon-reload"
    echo "  4. sudo systemctl enable techcrunch-update.timer"
    echo "  5. sudo systemctl start techcrunch-update.timer"
    echo ""
fi

echo "설정 완료!"
echo ""
echo "다음 명령어로 테스트:"
echo "  cd $PROJECT_DIR && $PYTHON3 scheduled_update.py"
