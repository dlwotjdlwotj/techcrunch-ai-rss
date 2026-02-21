"""
서버(프로덕션)용 실행 스크립트. Gunicorn으로 앱을 띄웁니다.
- PORT 환경 변수가 있으면 해당 포트 사용 (PaaS 호환)
- 로컬: python run_server.py  →  http://0.0.0.0:5000
"""
import os
import sys
from pathlib import Path

def main():
    # 프로젝트 루트를 작업 디렉터리로 (output/ 경로 맞추기)
    root = Path(__file__).resolve().parent
    os.chdir(root)
    port = os.environ.get("PORT", "5000")
    bind = f"0.0.0.0:{port}"
    workers = int(os.environ.get("GUNICORN_WORKERS", "1"))

    try:
        from gunicorn.app.base import BaseApplication
        from gunicorn import util
    except ImportError:
        print("gunicorn이 필요합니다. 설치: pip install gunicorn", file=sys.stderr)
        sys.exit(1)

    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            from gunicorn import util
            return util.import_app(self.application)

    options = {
        "bind": bind,
        "workers": workers,
        "threads": 1,
        "timeout": 30,
        "accesslog": "-",
        "errorlog": "-",
    }
    print(f"Gunicorn 시작: {bind} (workers={workers})")
    StandaloneApplication("app:app", options).run()


if __name__ == "__main__":
    main()
