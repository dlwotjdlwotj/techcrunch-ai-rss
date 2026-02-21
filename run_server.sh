#!/bin/sh
# Linux/macOS 서버에서 웹 서버 실행 (Gunicorn)
# 사용: ./run_server.sh   또는  PORT=8080 ./run_server.sh
cd "$(dirname "$0")"
PORT=${PORT:-5000}
exec gunicorn -w 1 -b "0.0.0.0:${PORT}" --timeout 30 app:app
