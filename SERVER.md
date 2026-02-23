# 서버에서 실행하기

웹 서버를 **서버(또는 PaaS)**에서 프로덕션 모드로 돌리는 방법입니다.

## 1. 필요한 것

- Python 3.10+
- 환경 변수 **GEMINI_API_KEY** (RSS 요약용, 웹 서버만 돌릴 땐 없어도 됨)

## 2. 설치

```bash
cd /path/to/techcrunch-ai-rss
pip install -r requirements.txt
```

## 3. 웹 서버 실행 (프로덕션)

### 방법 A: Python으로 실행 (Windows/Linux 공통)

```bash
python run_server.py
```

- 기본 포트: **5000**
- 다른 포트: `PORT=8080 python run_server.py` (Linux/Mac) 또는 `set PORT=8080 && python run_server.py` (Windows)

### 방법 B: Linux/macOS에서 Gunicorn 직접 실행

```bash
chmod +x run_server.sh
./run_server.sh
```

또는:

```bash
PORT=8080 gunicorn -w 1 -b 0.0.0.0:8080 app:app
```

### 방법 C: PaaS (Railway, Render 등)

- 저장소 연결 후 **빌드 명령**: `pip install -r requirements.txt`
- **실행 명령**: `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`
- **환경 변수**: `GEMINI_API_KEY` 설정 (선택)
- 루트에 **Procfile**이 있으면 그대로 사용 가능:
  ```
  web: gunicorn -w 1 -b 0.0.0.0:$PORT app:app
  ```

## 4. 서버에서 매일 자동 업데이트 설정

RSS 수집·요약을 **서버에서 매일 자동으로** 실행하도록 설정할 수 있습니다.

### 내장 스케줄러 (Railway, Render 등 PaaS)

웹 서버가 실행 중이면 **매일 00:00 한국 시간(KST)**에 자동으로 업데이트됩니다. 별도의 cron-job.org 설정이 필요 없습니다. `GEMINI_API_KEY` 환경 변수만 설정하면 됩니다.

### 방법 A: 자동 설정 스크립트 사용 (Linux 서버)

```bash
cd /path/to/techcrunch-ai-rss
chmod +x setup-server-update.sh
sudo bash setup-server-update.sh
```

이 스크립트가 자동으로 cron 작업을 설정합니다.

### 방법 B: Cron 수동 설정

```bash
crontab -e
```

아래 내용 추가 (경로는 실제 서버 경로로 변경):

```
# 매일 오전 9시에 RSS 수집 및 요약 실행
0 9 * * * cd /path/to/techcrunch-ai-rss && /usr/bin/python3 /path/to/techcrunch-ai-rss/scheduled_update.py >> /path/to/techcrunch-ai-rss/logs/update.log 2>&1
```

또는 `crontab.example` 파일을 참고하세요:

```bash
# crontab.example 파일의 경로를 수정한 후
crontab crontab.example
```

**로그 확인**:
```bash
tail -f logs/update.log
```

### 방법 C: 외부 Cron (cron-job.org) - 수동 트리거 또는 다른 시간대

내장 스케줄러(00:00 KST) 대신 다른 시간에 실행하거나, 수동으로 트리거하려면:

1. **Railway 환경 변수**에 추가:
   - `CRON_SECRET`: 임의의 비밀 문자열 (예: `my-secret-key-123`)
   - `GEMINI_API_KEY`: (필수) RSS 요약용

2. **[cron-job.org](https://cron-job.org)** 가입 후 새 cron 작업:
   - **URL**: `https://실제도메인/api/trigger-update?key=CRON_SECRET에_설정한_값`
   - **스케줄**: 원하는 시간 (타임존: Asia/Seoul 선택)
   - **요청 방식**: GET 또는 POST

### 방법 D: Systemd Timer 사용 (Linux systemd 시스템)

1. 서비스 파일과 타이머 파일의 경로 수정:
   ```bash
   # techcrunch-update.service와 techcrunch-update.timer 파일에서
   # /path/to/techcrunch-ai-rss 를 실제 경로로 변경
   ```

2. 시스템에 복사 및 활성화:
   ```bash
   sudo cp techcrunch-update.service techcrunch-update.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable techcrunch-update.timer
   sudo systemctl start techcrunch-update.timer
   ```

3. 상태 확인:
   ```bash
   sudo systemctl status techcrunch-update.timer
   sudo systemctl list-timers | grep techcrunch
   ```

### 동작 방식

- `scheduled_update.py`는 **"오늘 이미 업데이트했는지"** 확인하고, 안 했을 때만 실행합니다.
- 서버를 재부팅한 뒤에도, 그날 업데이트가 없으면 다음에 스크립트가 돌 때 자동으로 한 번 실행됩니다.
- 로그는 `logs/update.log`에 저장됩니다 (로그 디렉터리가 자동 생성됨).

### 테스트

설정 후 수동으로 테스트:

```bash
cd /path/to/techcrunch-ai-rss
python3 scheduled_update.py
```

## 5. 데이터 준비

- 웹 서버는 **output/summarized_articles.json**을 읽어서 화면에 뿌립니다.
- 처음 배포 시:
  1. 서버에서 한 번 실행: `python run_with_summary.py` (GEMINI_API_KEY 필요)
  2. 또는 로컬에서 만든 **output/** 폴더를 그대로 서버에 복사해도 됩니다.

## 6. 포트/디버그

- **PORT**: 환경 변수로 지정 (기본 5000). PaaS는 보통 자동으로 지정합니다.
- **FLASK_DEBUG**: `true`로 두면 Flask 개발 서버처럼 디버그 모드로 동작합니다. 서버에서는 보통 설정하지 않습니다.
